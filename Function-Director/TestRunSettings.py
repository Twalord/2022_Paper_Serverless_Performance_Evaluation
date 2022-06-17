import Models

openfaas_image_runs_1k = [
    Models.build_image_test_run("1k_images_16_replica", 10, 16, 4, 8,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_16_replica_no_processing", 10, 16, 4, 8,
                                Models.request_function_dic["openfaas"]["magick-example-no-processing"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_8_replica", 10, 8, 2, 8,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_8_replica_no_processing", 10, 8, 2, 8,
                                Models.request_function_dic["openfaas"]["magick-example-no-processing"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_4_replica", 10, 4, 1, 8,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_4_replica_no_processing", 10, 4, 1, 8,
                                Models.request_function_dic["openfaas"]["magick-example-no-processing"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_2_replica", 10, 2, 1, 4,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_2_replica_no_processing", 10, 2, 1, 4,
                                Models.request_function_dic["openfaas"]["magick-example-no-processing"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_1_replica", 10, 1, 1, 2,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_1_replica_no_processing", 10, 1, 1, 2,
                                Models.request_function_dic["openfaas"]["magick-example-no-processing"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
]

openfaas_sync_bytes_runs = [
    Models.build_bytes_test_run("1_request_Up_to_16MB_1_replica", 1000, 1, 10, 8,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 1),
    Models.build_bytes_test_run("1_request_Up_to_16MB_4_replica", 1000, 4, 40, 8,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 1)
]

openfaas_async_bytes_runs = [
    Models.build_bytes_test_run("100_request_Up_to_16MB_1_replica", 10, 1, 1, 4,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_4_replica", 10, 2, 2, 4,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_4_replica", 10, 4, 2, 8,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_8_replica", 10, 8, 4, 8,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_16_replica", 10, 16, 8, 8,
                                Models.request_function_dic["openfaas"]["magick-example-dummy"],
                                16777216, 2, 100),
]

openfaas_mini_image_test_run = [
    Models.build_image_test_run("mini_image_test_run", 1, 1, 1, 2,
                                Models.request_function_dic["openfaas"]["magick-example"],
                                "./shared/input/8images", "./shared/output/8images"),
]


nuclio_image_runs_1k = [
    Models.build_image_test_run("1k_images_16_replica", 10, 16, 4, 8,
                                Models.request_function_dic["nuclio"]["magick-16"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_16_replica_no_processing", 10, 16, 4, 8,
                                Models.request_function_dic["nuclio"]["magick-np-16"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_8_replica", 10, 8, 2, 8,
                                Models.request_function_dic["nuclio"]["magick-8"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_8_replica_no_processing", 10, 8, 2, 8,
                                Models.request_function_dic["nuclio"]["magick-np-8"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_4_replica", 10, 4, 1, 8,
                                Models.request_function_dic["nuclio"]["magick-4"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_4_replica_no_processing", 10, 4, 1, 8,
                                Models.request_function_dic["nuclio"]["magick-np-4"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_2_replica", 10, 2, 1, 4,
                                Models.request_function_dic["nuclio"]["magick-2"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_2_replica_no_processing", 10, 2, 1, 4,
                                Models.request_function_dic["nuclio"]["magick-np-2"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_1_replica", 10, 1, 1, 2,
                                Models.request_function_dic["nuclio"]["magick"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
    Models.build_image_test_run("1k_images_1_replica_no_processing", 10, 1, 1, 2,
                                Models.request_function_dic["nuclio"]["magick-np"],
                                "./shared/input/1kinput", "./shared/output/1koutput"),
]

nuclio_sync_bytes_runs = [
    Models.build_bytes_test_run("1_request_Up_to_16MB_1_replica", 1000, 1, 10, 8,
                                Models.request_function_dic["nuclio"]["dummy"],
                                16777216, 2, 1),
    Models.build_bytes_test_run("1_request_Up_to_16MB_4_replica", 1000, 4, 40, 8,
                                Models.request_function_dic["nuclio"]["dummy-4"],
                                16777216, 2, 1),
]

nuclio_async_bytes_runs = [
    Models.build_bytes_test_run("100_request_Up_to_16MB_1_replica", 10, 1, 1, 4,
                                Models.request_function_dic["nuclio"]["dummy"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_2_replica", 10, 2, 2, 4,
                                Models.request_function_dic["nuclio"]["dummy-2"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_4_replica", 10, 4, 2, 8,
                                Models.request_function_dic["nuclio"]["dummy-4"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_8_replica", 10, 8, 4, 8,
                                Models.request_function_dic["nuclio"]["dummy-8"],
                                16777216, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_16MB_16_replica", 10, 16, 8, 8,
                                Models.request_function_dic["nuclio"]["dummy-16"],
                                16777216, 2, 100),
]

nuclio_mini_image_test_run = [
    Models.build_image_test_run("mini_image_test_run", 1, 1, 1, 8,
                                Models.request_function_dic["nuclio"]["magick"],
                                "./shared/input/8images", "./shared/output/8images"),
]

nuclio_mini_bytes_test_run = [
    Models.build_bytes_test_run("mini_bytes_test_run", 1, 1, 1, 8,
                                Models.request_function_dic["nuclio"]["dummy"],
                                2097152, 2, 1),
]

nuclio_sync_bytes_go_runs = [
    Models.build_bytes_test_run("1_request_Up_to_2MB_1_replica", 1000, 1, 10, 8,
                                Models.request_function_dic["nuclio"]["dummy-go"],
                                2097152, 2, 1),
    Models.build_bytes_test_run("1_request_Up_to_2MB_4_replica", 1000, 4, 40, 8,
                                Models.request_function_dic["nuclio"]["dummy-go-4"],
                                2097152, 2, 1),
]

nuclio_async_bytes_go_runs = [
    Models.build_bytes_test_run("100_request_Up_to_2MB_1_replica", 10, 1, 1, 4,
                                Models.request_function_dic["nuclio"]["dummy-go"],
                                2097152, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_2MB_2_replica", 10, 2, 2, 4,
                                Models.request_function_dic["nuclio"]["dummy-go-2"],
                                2097152, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_2MB_4_replica", 10, 4, 2, 8,
                                Models.request_function_dic["nuclio"]["dummy-go-4"],
                                2097152, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_2MB_8_replica", 10, 8, 4, 8,
                                Models.request_function_dic["nuclio"]["dummy-go-8"],
                                2097152, 2, 100),
    Models.build_bytes_test_run("100_request_Up_to_2MB_16_replica", 10, 16, 8, 8,
                                Models.request_function_dic["nuclio"]["dummy-go-16"],
                                2097152, 2, 100),
]

openfaas_runs = [
    # *openfaas_mini_image_test_run,
    *openfaas_async_bytes_runs,
    *openfaas_sync_bytes_runs,
    *openfaas_image_runs_1k
]

nuclio_runs = [
    # *nuclio_mini_image_test_run,
    # *nuclio_mini_bytes_test_run,
    *nuclio_image_runs_1k,
    *nuclio_async_bytes_runs,
    *nuclio_sync_bytes_runs
]

nuclio_go_runs = [
    *nuclio_sync_bytes_go_runs,
    *nuclio_async_bytes_go_runs
]

test_runs = [
    *openfaas_runs,
    *nuclio_runs,
    *nuclio_go_runs
]
