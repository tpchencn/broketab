# coding: utf-8

import configparser


def init_conf(config_file):
    conf = configparser.ConfigParser()
    conf.read(config_file,'UTF-8')
    return conf
