import logging
import time

from logging import handlers


def get_logger_handler(logfile=""):
    formatter = logging.Formatter('%(levelname)-8s[%(asctime)s] %(name)-14s:  %(message)s')
    # set format to the handler
    rotation_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=5120, backupCount=0)
    rotation_handler.setFormatter(formatter)

    return rotation_handler


def function_tracker(logger=None, debug=False):
    """
        Decorator,
        Usages:\n
        @function_tracker(logger=logging.getLogger("function-tracker"))\n
        def your_function():
            pass
    """
    if logger is None:
        logger = logging.getLogger("function_tracker")

    def function_timer_decorator(function):
        def wrapper_func(*args, **kwargs):
            function_name = function.__name__
            if debug:
                logger.info("{} called with: args:{}, kwargs: {}".format(function_name, args, kwargs))

            start_time = time.time()
            try:
                result = function(*args, **kwargs)
                lapsed = round(time.time() - start_time, 2)

                logger.info("Function: [ {} ] completed, time used: [ {} ] seconds.".format(function_name, lapsed))
                return result
            except Exception as e:
                lapsed = round(time.time() - start_time, 2)
                logger.error("Function: [ {} ] interrupted, time used before interrupted: [ {} ] seconds. error: {}".format(function_name, lapsed, str(e)))
                raise e

        return wrapper_func

    return function_timer_decorator
