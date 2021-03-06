import traceback

import log_writer

import multiprocessing as mp
import os
import sys
import time
import random

import datetime as dt

def test_worker(name):

    print("(worker) My PID is {}.".format(os.getpid()))
    
    worker_logger = log_writer.logger
    worker_logger.set_name("worker")

    while True:
        try:
            wait_time = random.randint(0, 500) / 100
            if wait_time < 0.2:
                raise ValueError("Wait time less than 0.2!")
            time.sleep(wait_time)
            level = random.choice(['INFO', 'DEBUG'])
            worker_logger.log(level=level, message="Finished waiting {} seconds.".format(wait_time),
                              extra={'t': wait_time})
        except BaseException as e:
            worker_logger.error(e, extra={}, exc_info=True)


def test_main():

    # extended logger creation; names / IDs are provided by the caller
  
    parent_logger = log_writer.logger
    parent_logger.set_name("parent")

    parent_logger.info("Main process logger connected.", extra={'myfield': 'EXTRA WORKS!'})
    num_workers = 4
    worker_processes = []
    parent_logger.info("Starting worker processes.", extra={'n': num_workers})
    for i in range(num_workers):
        worker_name = 'worker-{}'.format(i)
        parent_logger.debug("Starting process for '{}'.".format(worker_name), extra={})
        wp = mp.Process(target=test_worker, args=(worker_name,), daemon=True)
        wp.start()
        parent_logger.debug("'{}' started; PID={}.".format(worker_name, wp.pid), extra={'PID': wp.pid})
        worker_processes.append(wp)
    try:
        while True:
            time.sleep(5)
            status = [wp.is_alive() for wp in worker_processes]
            parent_logger.info("Status of worker processes: {}".format(status), extra={})
            if any([not s for s in status]):
                parent_logger.warning("Some processes aren't running!", extra={})
    except KeyboardInterrupt as e:
        parent_logger.info("A MESSAGE", exc_info=True)
        parent_logger.info("Got exit signal via CTRL-C. Exiting.")
        sys.exit()


if __name__ == '__main__':
    print("My PID is {}.".format(os.getpid()))
    test_main()

    for fl in os.listdir('./'):
        if os.path.splitext(fl)[1] == '.log' and os.path.splitext(fl)[0] != str(os.getpid()):
            try:
                os.remove(fl)
            except BaseException as e:
                traceback.print_exc()

    logger = log_writer.logger
    logger.debug("First debug message.")
    time.sleep(0.5)
    logger.info("INFORMATION")
    time.sleep(0.5)

    # statuslogger_test.to_ole(dt.datetime.now())
    # time.sleep(0.5)
    logger.warning("A WARNING!")
    logger.debug("Second debug message.")
