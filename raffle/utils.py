from datetime import datetime


def get_iso_wk(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').isocalendar()[1]


def ordinal(n):
    ord_str = "%d%s" % (n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])
    return ord_str
