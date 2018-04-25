# coding: utf-8

import logging,os
import logging.handlers

def init_log(filename, loggername):
    # 创建一个logger
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    # 创建一个handler，用于写入日志文件
    # f= file(filename, mode='w')
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    fh = logging.handlers.TimedRotatingFileHandler(filename, 'D', 1, 0)
    # 设置后缀名称，跟strftime的格式一样
    fh.suffix = "%Y%m%d.log"

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(funcName)s-%(lineno)d: %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

