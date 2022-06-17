import asyncio
import statistics
import multiprocessing
import PIL.ImageFile
import aiohttp
from PIL import Image
import os
import logging
import secrets
import datetime as dt
import time
import random

from aiohttp import ServerDisconnectedError
from kubernetes import client, config

logger = logging.getLogger("logger")
config.load_kube_config("./shared/config")
os.environ["KUBECONFIG"] = "/app/shared/config"
PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True
process_number = 8
REQUEST_LIMIT_MULTIPLIER = 2  # Tested with 4 for 1 replica, did not provide performance gain

timeout = aiohttp.ClientTimeout(total=120)
TIMEOUT_LIMIT = 10  # Maximum number of Timeouts for a single request before the test run is restarted

# Set base urls pointing to the deployments without trailing /
OPENFASS_BASE_URL = ""
NUCLIO_BASE_URL = ""


class TestRunStuck(Exception):
    pass


def randomize_images_helper(image):
    pic = Image.open(image)
    max_x, max_y = pic.size
    pixels = pic.load()

    x = random.randrange(max_x)
    y = random.randrange(max_y)
    if pixels[x, y] == 255:
        pixels[x, y] = 0
    else:
        pixels[x, y] = 255

    pic.save(image)


class DataImage:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class DataSetImages:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.image_file_names = []
        self.get_image_file_names()
        self.image_count = len(self.image_file_names)

    def randomize_images(self):
        logger.debug("Randomizing " + str(len(self.image_file_names)) + " images")

        with multiprocessing.Pool(process_number) as p:
            p.imap_unordered(randomize_images_helper, self.image_file_names)
            p.close()
            p.join()

        logger.debug("Finished randomizing " + str(len(self.image_file_names)) + " images")

    def get_image_file_names(self):
        images = []
        count = 0
        for root, dirs, files in os.walk(self.input_directory):
            for name in files:
                count += 1
                images.append(os.path.join(root, name))
        self.image_file_names = images
        logger.info("Found " + str(count) + " images in " + self.input_directory)

    def load_all_images(self):
        data_image_list = []
        logger.info("Loading all images")
        for image_file in self.image_file_names:
            with open(image_file, 'rb') as f:
                data = f.read()
                data_image_list.append(DataImage(image_file, data))
                # logger.debug(f"Loaded {image_file} with data {len(data)}")
        logger.info("Loaded all " + str(len(data_image_list)) + " images")
        return data_image_list

    def save_all_images(self, processed_data_image_list):
        logger.info("Saving all images")
        try:
            for data_image in processed_data_image_list:
                logger.debug(f"Saving {data_image.name} with data {len(data_image.data)}")
                output_file = os.path.join(self.output_directory, os.path.basename(data_image.name))
                with open(output_file, 'wb') as f:
                    f.write(data_image.data)
        except:
            logger.exception(f"Error while saving image {data_image.name}.")
            raise
        logger.info("Saved all images")


class DataSetBytes:
    def __init__(self, bytes_cap, factor_step, requests):

        if factor_step <= 1:
            logger.error("Invalid factor_step " + str(factor_step) + " must be greater than 1."
                                                                     "Defaulting to 2.")
            factor_step = 2

        self.bytes_cap = bytes_cap
        self.factor_step = factor_step
        self.bytes_list = []
        self.current_bytes = 1
        self.requests = requests
        self.byte_sizes = self.calculate_byte_sizes()

    def generate_bytes(self):
        self.bytes_list = []
        for _ in range(self.requests):
            self.bytes_list.append(b"\x00" + secrets.token_bytes(int(self.current_bytes)) + b"\x00")

    def step_up_current_bytes(self):
        self.current_bytes = self.current_bytes * self.factor_step
        self.reset_if_cap_is_overshot()

    def reset_if_cap_is_overshot(self):
        if self.current_bytes > self.bytes_cap:
            self.current_bytes = 1

    def calculate_byte_sizes(self):
        i = 1
        byte_sizes = []
        while True:
            byte_sizes.append(i)
            i *= self.factor_step
            if i > self.bytes_cap:
                break
        return byte_sizes


class RequestFunction:
    def __init__(self, url, namespace, deployment, limit, process_pool):
        self.url = url
        self.namespace = namespace
        self.deployment = deployment
        self.limit = limit
        self.process_pool = process_pool

    def scale_replicas(self, number: int):
        api_client = client.ApiClient()
        api_instance = client.AppsV1Api(api_client)
        body = {'spec': {'replicas': number}}
        response = api_instance.patch_namespaced_deployment_scale(self.deployment, self.namespace, body,
                                                                  pretty=True)
        # response = api_instance.read_namespaced_deployment_scale(self.deployment, self.namespace)
        logger.info("Made call to kubernetes to scale " + self.deployment + " to " + str(number) + " replicas.")
        logger.debug(str(response))

    async def make_request_helper(self, data, session, timeout_count):
        try:
            async with session.post(self.url, data=data) as response:
                out = await response.read()
                if response.status not in [200]:
                    logger.debug(f"{response.status}: {str(out)}")
                if response.status in [400, 404, 500, 502, 503, 504]:
                    return await self.make_request_helper(data, session, timeout_count)
                return out
        except ServerDisconnectedError as e:
            logger.debug(f"ServerDisconnectedError")
            return await self.make_request_helper(data, session, timeout_count)
        except asyncio.TimeoutError as e:
            logger.debug(f"asyncio.TimeoutError")
            if timeout_count > TIMEOUT_LIMIT:
                raise TestRunStuck
            return await self.make_request_helper(data, session, timeout_count + 1)
        except aiohttp.ClientOSError as e:
            logger.debug(f"aiohttp.ClientOSError")
            return await self.make_request_helper(data, session, timeout_count)
        except aiohttp.ClientPayloadError as e:
            logger.debug(f"aiohttp.ClientPayloadError")
            return await self.make_request_helper(data, session, timeout_count)
        except:
            logger.exception(f"Make request failed failed")
            raise

    async def make_request(self, data, session):
        return await self.make_request_helper(data, session, 0)


class RequestFunctionImages(RequestFunction):
    def __init__(self, url, namespace, deployment, limit, process_pool, data_set_images: DataSetImages):
        super().__init__(url, namespace, deployment, limit, process_pool)
        self.data_set_images = data_set_images

    def __init__(self, function_dict: {}, limit, process_pool, data_set_images: DataSetImages):
        super().__init__(function_dict["url"], function_dict["namespace"],
                         function_dict["deployment"], limit, process_pool)
        self.data_set_images = data_set_images

    async def make_request_helper(self, data_image: DataImage, session, timeout_count):
        data = data_image.data
        # logger.debug(f"Got image data of len {len(data)} for image {data_image.name}")
        try:
            async with session.post(self.url, data=data) as response:
                out = await response.read()
                # if response.status not in [200, 400, 404, 500, 502, 503]:
                if response.status not in [200]:
                    logger.debug(f"{response.status}: {str(out)}")
                if response.status in [400, 404, 500, 502, 503, 504]:
                    return await self.make_request_helper(data_image, session, timeout_count)
                logger.debug(f"Completed request with {response.status},"
                             f" for image {data_image.name} and received {len(out)}")
                return DataImage(data_image.name, out)
        except ServerDisconnectedError as e:
            logger.debug(f"ServerDisconnectedError")
            return await self.make_request_helper(data_image, session, timeout_count)
        except asyncio.TimeoutError as e:
            logger.debug(f"asyncio.TimeoutError")
            if timeout_count > TIMEOUT_LIMIT:
                raise TestRunStuck
            return await self.make_request_helper(data_image, session, timeout_count + 1)
        except aiohttp.ClientOSError as e:
            logger.debug(f"aiohttp.ClientOSError")
            return await self.make_request_helper(data_image, session, timeout_count)
        except aiohttp.ClientPayloadError as e:
            logger.debug(f"aiohttp.ClientPayloadError")
            return await self.make_request_helper(data_image, session, timeout_count)
        except:
            logger.exception(f"Make request failed")
            raise

    async def make_request(self, data_image: DataImage, session, sem):
        async with sem:
            output = await self.make_request_helper(data_image, session, 0)
        return output

    def prepare_process(self, data_image_list):
        # logger.info("Process starting work: " + str(multiprocessing.current_process()))
        return asyncio.run(self.async_process(data_image_list))

    async def async_process(self, data_image_list):
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.limit), timeout=timeout)
        sem = asyncio.Semaphore(self.limit * REQUEST_LIMIT_MULTIPLIER)
        tasks = []
        for data_image in data_image_list:
            task = asyncio.create_task(self.make_request(data_image, session, sem))
            tasks.append(task)
        processed_data_image_list = []
        for coroutine in asyncio.as_completed(tasks):
            processed_data_image_list.append(await coroutine)
        await session.close()
        return processed_data_image_list

    def make_all_requests(self, data_image_list):
        images_per_process = self.data_set_images.image_count // self.process_pool

        sub_lists = [data_image_list[i * images_per_process:(i + 1) * images_per_process] for i in
                     range((len(data_image_list) + images_per_process - 1) // images_per_process)]

        with multiprocessing.Pool(self.process_pool) as p:
            logger.debug("Starting Process Pool")
            try:
                processed_sub_lists = p.map(self.prepare_process, sub_lists)
                processed_data_image_list = [data_image for sub_list in processed_sub_lists for data_image in sub_list]
            finally:
                p.close()
                p.join()
                logger.debug("Closing Process Pool")
        return processed_data_image_list


class RequestFunctionBytes(RequestFunction):
    def __init__(self, url, namespace, deployment, limit, process_pool, data_set_bytes: DataSetBytes):
        super().__init__(url, namespace, deployment, limit, process_pool)
        self.data_set_bytes = data_set_bytes

    def __init__(self, function_dict: {}, limit, process_pool, data_set_bytes: DataSetBytes):
        super().__init__(function_dict["url"], function_dict["namespace"],
                         function_dict["deployment"], limit, process_pool)
        self.data_set_bytes = data_set_bytes

    def prepare_process(self, bytes_list):
        asyncio.run(self.async_process(bytes_list))

    async def async_process(self, bytes_list):
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=self.limit), timeout=timeout)
        tasks = []
        for bytes_string in bytes_list:
            task = asyncio.create_task(self.make_request(bytes_string, session))
            tasks.append(task)
        for task in asyncio.as_completed(tasks):
            await task
        await session.close()

    def make_all_requests(self):
        if self.data_set_bytes.requests > 1:
            byte_strings_per_process = len(self.data_set_bytes.bytes_list) // self.process_pool

            sub_lists = [self.data_set_bytes.bytes_list[i * byte_strings_per_process:(i + 1) * byte_strings_per_process]
                         for i in range((len(self.data_set_bytes.bytes_list) + byte_strings_per_process - 1)
                                        // byte_strings_per_process)]

            with multiprocessing.Pool(self.process_pool) as p:
                logger.debug("Starting Process Pool")
                try:
                    p.map(self.prepare_process, sub_lists)
                finally:
                    p.close()
                    p.join()
                    logger.debug("Closing Process Pool")
        else:
            self.prepare_process(self.data_set_bytes.bytes_list)


class TestRun:
    def __init__(self, name, repeats, replicas):
        self.name = name
        self.repeats = repeats
        self.replicas = replicas


class TestRunImages(TestRun):
    def __init__(self, name, repeats, replicas, request_function: RequestFunctionImages):
        super().__init__(name, repeats, replicas)
        self.request_function = request_function

    def perform_test_run(self):
        results = []

        completed = False
        while not completed:
            self.request_function.data_set_images.randomize_images()

            data_image_list = self.request_function.data_set_images.load_all_images()
            start_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start = time.perf_counter()

            try:
                processed_data_image_list = self.request_function.make_all_requests(data_image_list)
                completed = True
            except TestRunStuck:
                logger.warning("Test Run Stuck, restarting Test Run")
                completed = False
                continue

        end = time.perf_counter()
        end_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = end - start

        results.append(ResultImages(self.name, self.repeats, self.request_function.data_set_images.image_count,
                                    self.request_function.deployment, start_timestamp, end_timestamp, self.replicas,
                                    [elapsed]))
        self.request_function.data_set_images.save_all_images(processed_data_image_list)

        return results


class TestRunBytes(TestRun):
    def __init__(self, name, repeats: int, replicas, request_function: RequestFunctionBytes):
        super().__init__(name, repeats, replicas)
        self.request_function = request_function

    def perform_test_run(self):
        times_dict = {}
        for byte_size in self.request_function.data_set_bytes.byte_sizes:
            times_dict[byte_size] = []

        for byte_size in self.request_function.data_set_bytes.byte_sizes:
            logger.info(f"Performing data size {byte_size}/{max(self.request_function.data_set_bytes.byte_sizes)} "
                        f"test run")
            completed = False
            while not completed:
                self.request_function.data_set_bytes.generate_bytes()

                start_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start = time.perf_counter()

                try:
                    self.request_function.make_all_requests()
                    completed = True
                except TestRunStuck:
                    logger.warning("Test Run Stuck, restarting Test Run")
                    completed = False
                    continue

            end = time.perf_counter()
            end_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elapsed = end - start

            times_dict[self.request_function.data_set_bytes.current_bytes].append((start_timestamp, end_timestamp,
                                                                                   elapsed))

            self.request_function.data_set_bytes.step_up_current_bytes()

        results = []
        for byte_size in self.request_function.data_set_bytes.byte_sizes:
            current_entry = times_dict[byte_size]
            result = ResultBytes(self.name, self.repeats, self.request_function.data_set_bytes.requests,
                                 self.request_function.deployment, [time_entry[0] for time_entry in current_entry],
                                 [time_entry[1] for time_entry in current_entry], self.replicas,
                                 [time_entry[2] for time_entry in current_entry], byte_size)
            results.append(result)

        return results


class Result:
    def __init__(self, test_run_name, repeats, requests, request_function, start_timestamp,
                 end_timestamp, replicas, times):
        self.test_run_name = test_run_name
        self.repeats = repeats
        self.requests = requests
        self.request_function = request_function
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.replicas = replicas
        self.times = times
        self.average = self.calculate_average()
        self.median = self.calculate_median()

    def calculate_average(self):
        return statistics.mean(self.times)

    def calculate_median(self):
        return statistics.median(self.times)

    def to_list(self):
        return [self.test_run_name, self.request_function, self.requests, self.repeats, self.replicas, self.average,
                self.median,
                self.times, self.start_timestamp, self.end_timestamp]

    def header_row(self):
        return ["Test", "Function", "Requests", "Repeats", "Replicas", "Average", "Median", "Times", "StartTimestamp",
                "EndTimestamp"]


class ResultImages(Result):
    def __init__(self, test_run_name, repeats, requests, request_function, start_timestamp,
                 end_timestamp, replicas, times):
        super().__init__(test_run_name, repeats, requests, request_function, start_timestamp,
                         end_timestamp, replicas, times)

    def to_list(self):
        return super().to_list()

    def header_row(self):
        return super().header_row()


class ResultBytes(Result):
    def __init__(self, test_run_name, repeats, requests, request_function, start_timestamp,
                 end_timestamp, replicas, times, bytes_per_request):
        super().__init__(test_run_name, repeats, requests, request_function, start_timestamp,
                         end_timestamp, replicas, times)
        self.bytes_per_request = bytes_per_request

    def to_list(self):
        return [*super().to_list(), self.bytes_per_request]

    def header_row(self):
        return [*super().header_row(), "Bytes per Request"]


def build_image_test_run(name, repeats, replicas, limit, process_pool, function_dic, input_directory, output_directory):
    return TestRunImages(name, repeats, replicas,
                         RequestFunctionImages(function_dic, limit, process_pool,
                                               DataSetImages(input_directory, output_directory)))


def build_bytes_test_run(name, repeats, replicas, limit, process_pool, function_dic, bytes_cap, factor_step, requests):
    return TestRunBytes(name, repeats, replicas,
                        RequestFunctionBytes(function_dic, limit, process_pool,
                                             DataSetBytes(bytes_cap, factor_step, requests)))


openfaas_function_dic = {
    "magick-example": {
        "url": OPENFASS_BASE_URL + "/function/magick-example",
        "namespace": "openfaas-fn",
        "deployment": "magick-example"},
    "magick-example-no-processing": {
        "url": OPENFASS_BASE_URL + "/function/magick-example-no-processing",
        "namespace": "openfaas-fn",
        "deployment": "magick-example-no-processing"},
    "magick-example-dummy": {
        "url": OPENFASS_BASE_URL + "/function/magick-example-dummy",
        "namespace": "openfaas-fn",
        "deployment": "magick-example-dummy"},
    "magick-example-dummy-sleep": {
        "url": OPENFASS_BASE_URL + "/function/magick-example-dummy-sleep",
        "namespace": "openfaas-fn",
        "deployment": "magick-example-dummy-sleep"}}

nuclio_function_dic = {
    "magick": {
        "url": NUCLIO_BASE_URL + "/magick",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-2": {
        "url": NUCLIO_BASE_URL + "/magick-2",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-4": {
        "url": NUCLIO_BASE_URL + "/magick-4",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-8": {
        "url": NUCLIO_BASE_URL + "/magick-8",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-16": {
        "url": NUCLIO_BASE_URL + "/magick-16",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-np": {
        "url": NUCLIO_BASE_URL + "/magick-np",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-np-2": {
        "url": NUCLIO_BASE_URL + "/magick-np-2",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-np-4": {
        "url": NUCLIO_BASE_URL + "/magick-np-4",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-np-8": {
        "url": NUCLIO_BASE_URL + "/magick-np-8",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "magick-np-16": {
        "url": NUCLIO_BASE_URL + "/magick-np-16",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy": {
        "url": NUCLIO_BASE_URL + "/dummy",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-2": {
        "url": NUCLIO_BASE_URL + "/dummy-2",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-4": {
        "url": NUCLIO_BASE_URL + "/dummy-4",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-8": {
        "url": NUCLIO_BASE_URL + "/dummy-8",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-16": {
        "url": NUCLIO_BASE_URL + "/dummy-16",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-go": {
        "url": NUCLIO_BASE_URL + "/dummy-go",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-go-2": {
        "url": NUCLIO_BASE_URL + "/dummy-go-2",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-go-4": {
        "url": NUCLIO_BASE_URL + "/dummy-go-4",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-go-8": {
        "url": NUCLIO_BASE_URL + "/dummy-go-8",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
    "dummy-go-16": {
        "url": NUCLIO_BASE_URL + "/dummy-go-16",
        "namespace": "nuclio",
        "deployment": "nuclio-nuclio-hello-go"},
}

request_function_dic = {"openfaas": openfaas_function_dic, "nuclio": nuclio_function_dic}
