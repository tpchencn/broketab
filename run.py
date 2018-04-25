# coding: utf-8
import os
import time
from broker import tabtran
import traceback

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.process

from utils.common import config
from utils.common import logger


def make_app():
    return tornado.web.Application([
        (r"/", tabtran.MainHandler),
        (r"/.*", tabtran.ViewHandler),
    ])


if __name__ == "__main__":
    port = config['common']['port']
    thread = config['common']['thread']
    app = make_app()
    logger.info("Start to run tornado.... ")
    try:
        sockets = tornado.netutil.bind_sockets(port)
        tornado.process.fork_processes(int(thread))
        server = tornado.httpserver.HTTPServer(app)
        server.add_sockets(sockets)
        logger.info("Tornado is running.... ")
        tornado.ioloop.IOLoop.instance().start()
    except:
        logger.info("Tornado cant be started.... ")
        traceback.print_exc()
