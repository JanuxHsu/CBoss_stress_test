import logging
import threading
import time

import os
from functools import reduce

from netapp_restful_api_query import Restful_API_Handler
from utils import function_tracker, get_logger_handler

jobs = list()

to_clone_file = "/source/test_file"

worker_logger = logging.getLogger("worker")
worker_logger.addHandler(get_logger_handler(logfile="call_history.log"))

netapp_rest = Restful_API_Handler()
netapp_rest.set_cluster(cluster="127.0.0.1")
netapp_rest.set_api_user(api_user="admin")
netapp_rest.set_api_password_env(api_password_env="FILER_PWD")
netapp_rest.set_port(port=9999)


def setup_default_logger(log_level=logging.INFO):
    logging.basicConfig(level=log_level,
                        format='%(levelname)-8s[%(asctime)s] %(name)-14s:  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(log_level)


class File_clone_worker(threading.Thread):
    def __init__(self, iteration=0, index=0):
        threading.Thread.__init__(self)
        self.iteration = iteration
        self.index = index
        self.logger = worker_logger
        self.return_job_id = None
        self.status = None

    def run(self) -> None:
        self.logger.info("[{}] start idx:{}".format(self.name, self.index))

        source_path = to_clone_file
        destination_path = "/destination/{}/{}".format(self.iteration, "{}_cloned".format(self.name))

        self.status = "Clone file from: {} to {}.".format(source_path, destination_path)

        res = netapp_rest.trigger_file_clone(
            volume_uuid="3eebd36c-6473-11eb-8ffe-00a098cd3015",
            source_path=source_path,
            destination_path=destination_path)
        self.logger.info(res)
        self.return_job_id = res["job"]["uuid"]


if __name__ == "__main__":
    setup_default_logger()

    main_loop_logger = logging.getLogger("main_loop")
    main_loop_logger.addHandler(get_logger_handler(logfile="main_loop.log"))

    start_time = time.time()

    current = time.time()
    lapsed = 0

    while lapsed < 60 * 10:
        lapsed = current - start_time
        main_loop_logger.info("lapsed: {}".format(round(lapsed, 2)))
        for idx in [1, 2, 3, 4, 5]:
            worker = File_clone_worker(iteration=round(lapsed), index=idx)
            worker.start()

            jobs.append(worker)

        time.sleep(1)
        current = time.time()
        break

    run_check = True
    while run_check:
        run_check = False
        for job in jobs:
            if job.is_alive():
                run_check = True
                main_loop_logger.info("{} still running.".format(job.status))
                break

        time.sleep(1)

    api_result_logger = logging.getLogger("api_result")
    api_result_logger.addHandler(get_logger_handler(logfile="api_result.log"))

    job_ids = list(map(lambda x: x.return_job_id, jobs))

    main_loop_logger.info("All File Clone triggered.")
    main_loop_logger.info("checking total: {} ONTAP jobs".format(len(job_ids)))

    while len(job_ids) > 0:
        for job_id in job_ids:
            job_status = netapp_rest.get_job_status(job_id=job_id)
            job_end_time = job_status["end_time"]
            if job_end_time is not None or not job_end_time == "":
                job_ids.remove(job_id)
                api_result_logger.info(job_status)
                main_loop_logger.info("{} jobs Left.".format(len(job_ids)))
            else:
                print(job_status)
            time.sleep(3)

        main_loop_logger.info("{} jobs still running.".format(len(job_ids)))
        time.sleep(5)

    main_loop_logger.info("Program ended.")
