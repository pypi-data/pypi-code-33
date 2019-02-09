from __future__ import print_function
import timeit
from imgaug import parameters as iap
import time
import six.moves as sm

def main():
    number = 100*1000

    print("-----------------------")
    print("handle_continuous_param")
    print("-----------------------")
    setup_code = """\
    from imgaug import parameters as iap""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(1, 'interval', value_range=None, tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("1, without value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    setup_code = """\
    from imgaug import parameters as iap""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(1, 'interval', value_range=(0, 1000), tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("1, with value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    setup_code = """\
    from imgaug import parameters as iap
    interval = (1, 100)""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(interval, 'interval', value_range=None, tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("uniform, without value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    setup_code = """\
    from imgaug import parameters as iap
    interval = (1, 100)""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(interval, 'interval', value_range=(0, 1000), tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("uniform, with value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    setup_code = """\
    from imgaug import parameters as iap
    interval = [1, 100]""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(interval, 'interval', value_range=None, tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("list, without value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    setup_code = """\
    from imgaug import parameters as iap
    interval = [1, 100]""".replace("    ", "")
    stmt_code = "result = iap.handle_continuous_param(interval, 'interval', value_range=(0, 1000), tuple_to_uniform=True, list_to_choice=True)"
    seconds = timeit.timeit(stmt_code, setup=setup_code, number=number)
    print("list, with value_range %.2fs per 100k, %.4fms per call" % (seconds, 1000*(seconds/number)))

    interval = (1, 100)
    time_start = time.time()
    for _ in sm.xrange(number):
        result = iap.handle_continuous_param(interval, 'interval', value_range=(0, 1000), tuple_to_uniform=True, list_to_choice=True)
    time_end = time.time()
    seconds = time_end - time_start
    print("uniform, with value_range %.2fs per 100k, %.4fms per call [custom measurement]" % (seconds, 1000*(seconds/number)))

if __name__ == "__main__":
    main()
