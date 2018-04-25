# coding: utf-8
import os
import hashlib
from datetime import datetime, timedelta

import pandas as pd

from utils.conf import init_conf
from utils.log import init_log


def get_conf():
    cfg_loc = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))) + os.path.sep + 'config' + os.path.sep + 'brokertab.cfg'
    return init_conf(cfg_loc)

def get_logger():
    log_loc = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))) + os.path.sep + 'log' + os.path.sep + 'brokertab.log'
    return init_log(log_loc, "brokertab")


logger = get_logger()
config = get_conf()


def get_write_db_count():
    pandas_write_mysql_count = config["performance"]['pandas_write_mysql_count']
    if pandas_write_mysql_count is None or len(pandas_write_mysql_count) == 0:
        return 10000

    try:
        pandas_write_mysql_count = int(pandas_write_mysql_count)
        return pandas_write_mysql_count
    except:
        return 10000


def get_read_db_count():
    pandas_write_mysql_count = config["performance"]['pandas_read_mysql_count']
    if pandas_write_mysql_count is None or len(pandas_write_mysql_count) == 0:
        return 30000

    try:
        pandas_write_mysql_count = int(pandas_write_mysql_count)
        return pandas_write_mysql_count
    except:
        return 30000


def get_concurrent_count():
    concurrent_count = config["performance"]['concurrent_run_func']
    if concurrent_count is None or len(concurrent_count) == 0:
        return 3

    try:
        concurrent_count = int(concurrent_count)
        return concurrent_count
    except:
        return 3


def get_hashkey(*values):
    str_source = ""
    for value in values:
        str_source = str_source + str(value)

    return hashlib.md5(str_source.encode()).hexdigest()


def get_columns_hashkey(row, keys):
    str_source = ""
    for key in keys:
        value = row[key]
        if (pd.notnull(value)):
            str_source = str_source + str(value)

    return hashlib.md5(str_source.encode()).hexdigest()


def get_args_hashkey(*args):
    str_source = ""
    for value in args:
        if (pd.notnull(value)):
            str_source = str_source + str(value)

    return hashlib.md5(str_source.encode()).hexdigest()


def min_date():
    return datetime(1900, 1, 1)


def max_date():
    return datetime(2261, 1, 1)


def gmt_datetime():
    return datetime.utcnow() + timedelta(hours=8)


def str_datetime(timestr, format="%Y-%m-%d"):
    if timestr is None:
        return None
    transform_datetime = None
    try:
        transform_datetime = datetime.strptime(timestr, format)
    except Exception as e:
        pass

    return transform_datetime
