import inspect


def log_call():
    data = inspect.stack()
    # for d in data[1]:
    #     print(d)
    print(data[1][3])