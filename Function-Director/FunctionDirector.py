import logging
import time
import os
import csv
import TestRunSettings


def main():
    logger = setup_logging("./shared/logs")

    output_directory = "./shared/results"

    time_str = time.strftime("%d-%m-%Y_%H-%M-%S")
    output_file = os.path.join(output_directory, f"Results_{time_str}.csv")
    with open(output_file, "w") as f:
        pass
    test_run_count = 0
    for test_run in TestRunSettings.test_runs:
        test_run_count += 1
        logger.info(f"Starting {test_run_count}/{len(TestRunSettings.test_runs)} test run {test_run.name}")
        logger.debug(f"With {test_run.repeats=}, {test_run.replicas=}, {test_run.request_function.limit=},"
                     f" {test_run.request_function.deployment=}")
        test_run.request_function.scale_replicas(test_run.replicas)

        for repeat in range(test_run.repeats):
            logger.info(f"Performing {repeat + 1}/{test_run.repeats} test run")
            try:
                results = test_run.perform_test_run()
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt, stopping.")
                exit(1)
            except:
                logger.exception(f"TestRun {test_run_count}/{len(TestRunSettings.test_runs)} {test_run.name} failed")
                continue

            logger.info(f"Completed {repeat + 1}/{test_run.repeats} test run")

            with open(output_file, "a") as f:
                wr = csv.writer(f)
                # wr.writerow([test_run.name])
                wr.writerow(results[0].header_row())
                for result in results:
                    wr.writerow(result.to_list())

        logger.info(f"Finished {test_run_count}/{len(TestRunSettings.test_runs)} test run {test_run.name}")


def setup_logging(path_to_logs: str):
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - %(message)s")
    time_str = time.strftime("%d-%m-%Y_%H-%M-%S")
    log_file_name = f"log_{time_str}.log"
    fh = logging.FileHandler(str(os.path.join(path_to_logs, log_file_name)))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Finished setting up logger. Writing logs to " + str(os.path.join(path_to_logs, log_file_name)))

    return logger


if __name__ == "__main__":
    main()
