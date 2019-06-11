import time


def is_int(value):
    try:
        int(value)
        return True
    except Exception:
        return False


def is_float(value):
    try:
        float(value)
        return True
    except Exception:
        return False


def is_date(value):
    try:
        time.strptime(value, "%Y-%m-%d")
        return True
    except:
        return False


def is_datetime(value):
    try:
        time.strptime(value, "%Y-%m-%d %H:%M:%S")
        return True
    except:
        return False