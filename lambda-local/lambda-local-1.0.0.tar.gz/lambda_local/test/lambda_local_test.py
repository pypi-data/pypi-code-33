from lambda_local.lambda_local import LambdaLocal


def lambda_local_test_1():
    try:
        LambdaLocal(None, None, None).run()
    except Exception as e:
        raise Exception(e)


def lambda_local_test_2():
    try:
        LambdaLocal(lambda x, y: "calling function with Nones", None, None).run()
    except Exception as e:
        raise Exception(e)


def handler(events, context):
    print("events :", events)
    print("context :", context)
    return events


def lambda_local_test_3():
    try:
        events = {"x": 7}
        context = {"timeout": 100}
        LambdaLocal(handler, events, context).run()
    except Exception as e:
        raise Exception(e)


if __name__ == "__main__":
    try:
        lambda_local_test_1()
    except Exception as e:
        print("lambda_local_test_1 : ", "All args are None.")

    try:
        lambda_local_test_2()
    except Exception as e:
        print("lambda_local_test_2 : ", "All args are None accept function.")

    try:
        lambda_local_test_3()
    except Exception as e:
        print("lambda_local_test_3 : ", "All args.")
