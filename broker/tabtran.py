# coding: utf-8
import tornado.web
import requests
import json
import os

from utils.common import config
from utils.common import logger


# 301 Url dosent have company_id argument
# 303 Token is not correct
# 304 Url dosent have token argument
# 305 Url dosent (startswith "/t/" and include "/views/" ) or startswith "/views/"
# 306 Url is a main path
# 307 can not get cookie user token.
# 308 can not get site


def get_ticket(site_name, is_site):
    user = config['common']['user']
    tableau_ticket_server = config['common']['tableau_ticket_server']
    if is_site == -1:  # 是否含site，再决定是否传入site_name
        params = {"username": user}
    else:
        params = {"username": user, "target_site": site_name}

    try:
        r = requests.post(tableau_ticket_server, params)
        ticket = r.text
        if ticket == "-1":
            return None
        else:
            return ticket
    except requests.exceptions.ConnectionError as e:
        logger.error("Cant connect to the ticket server: " + e)
    except Exception as e:
        logger.error("verify ticket error:{}".format(e))

    return None


def token_verify(token):
    user_lib = config['user_verify']['user_lib']  # 用户库API
    headers = {"Accept": "*/*", "token": token}  # 用户库Headers

    try:
        r = requests.get(user_lib, headers=headers)  # 到用户库get信息
        r.encoding = 'utf-8'  # 强制指定requests编码方式
        j = json.loads(r.text)  # 解码json 并返回python对象类型
        return j["success"]  # 结果应该是True 或者 False
    except requests.exceptions.ConnectionError as e:
        logger.error("Cant connect to the token verify server: " + e)
    except Exception as e:
        logger.error("verify token error.{}".format(e))

    return False


def verify_token_step(request_hander, user_id_required, arguments, use_cookie, site, exclude_sites_list):
    if user_id_required == "True":
        if use_cookie != "True" and "token" in arguments:
            if "token" in arguments:
                user_token = request_hander.get_argument("token")
            else:
                logger.error("can not get user token")
                request_hander.write("Please contact Admin.error code: 304")
                return

        if token_verify(user_token) is True:  # token 值到用户库验证
            logger.info("user token verify succeed")
        else:
            logger.error("user token verify failed:{}".format(user_token))
            request_hander.write("用户超时或者在其它方登录(303)")
            return
    else:
        logger.info("user token  not  required")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # self.write("Hello, world")
        arguments = self.request.arguments
        error_code = ""
        path = self.request.path
        logger.info("the path is : " + path)
        self.write("Please contact Admin.error code: 306")


class ViewHandler(tornado.web.RequestHandler):
    def get(self):
        tableau_redirect_server = config['common']['tableau_redirect_server']
        user_id_required = config['user_verify']['user_id_required']
        company_id_required = config['common']['company_id_required']
        use_cookie = config['common']['use_cookie']
        cookie_path_start = config['common']['cookie_path_start']
        path_start = config['common']['path_start']
        cookie_token_names = config['common']['cookie_token_name']
        exclude_sites = config["user_verify"]["exclude_site"]
        exclude_sites_list = exclude_sites.split(",")

        arguments = self.request.arguments
        error_code = ""
        path = self.request.path
        logger.info("--------------------------- Start to get Url request : ---------------------------")
        logger.info("Url path is : " + path)

        # path start verify
        real_path_start = None
        user_token = None
        if use_cookie == "True":
            if "," in cookie_token_names:
                token_list = cookie_token_names.split(",")
                for token_name_one in token_list:
                    user_token = self.get_cookie(token_name_one)
                    if user_token is not None and len(user_token) > 0:
                        # user_token.decode("utf-8")
                        user_token = user_token[len("bearer%20%20"):len(user_token)].strip()
                        break
            else:
                user_token = self.get_cookie(cookie_token_names)

            if user_token is None or len(user_token) < 1:
                logger.error("can not get cookie user token.")
                self.write("Please contact Admin.error code: 307")
                return
            if path.startswith(cookie_path_start) is False:
                logger.error("Cookie run not start with:{}".format(cookie_path_start))
                self.write("Please contact Admin.error code: 305")
                return
            else:
                real_path_start = cookie_path_start

        else:
            if path.startswith(path_start) is False:
                logger.error("path not start with:{}".format(path_start))
                self.write("Please contact Admin.error code: 305")
                return
            else:
                real_path_start = path_start


        #
        # get site
        site_name = path[len(real_path_start):path.index("/views/")]
        if site_name is None or len(site_name) < 1:
            logger.error("can not get site:{}".format(site_name))
            self.write("Please contact Admin.error code: 308")
            return

        # CompanyId verify
        logger.info("Start to verify company Id")
        if company_id_required == "True" and site_name not in exclude_sites:
            if "CompanyId" in arguments:  # 确认是否存在company_id参数
                company_id = self.get_argument("CompanyId")
                logger.info("CompanyId  verify succeed")
            else:
                logger.error("CompanyId not exist")
                self.write("Please contact Admin.error code: 301")
                return
        else:
            logger.info("CompanyId not required")
        logger.info("CompanyId verify finished")



        # user token verify

        logger.info("Start to verify user token")
        if user_id_required == "True" and site_name not in exclude_sites:
            if use_cookie != "True" and "token" in arguments:
                if "token" in arguments:
                    user_token = self.get_argument("token")
                else:
                    logger.error("can not get user token")
                    self.write("Please contact Admin.error code: 304")
                    return

            if token_verify(user_token) is True:  # token 值到用户库验证
                logger.info("user token verify succeed")
            else:
                logger.error("user token verify failed:{}".format(user_token))
                self.write("用户超时或者在其它方登录(303)")
                return
        else:
            logger.info("user token  not  required")
        logger.info("user token verify finished")

        params_str = '&'.join("{0}={1}".format(key, val[0].decode("utf-8")) for (key, val) in arguments.items())
        file = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep + 'config' + os.sep + 'argu.json'
        file = open(file, 'r')
        data = json.JSONDecoder().decode(file.read())
        file.close()
        url_arguments = data['url_argu']
        params_str = params_str + '&' + '&'.join(argument for argument in url_arguments)

        logger.info("Start to get ticket")
        ticket = get_ticket(site_name, 1)
        logger.info("Ticket get finished:{}".format(ticket))

        if ticket is None:
            self.write("Can not get right authorization ticket.")
        else:
            redirect_path = "/t/{}".format(path[len(real_path_start):len(path)])
            redirect_url = "{}/{}{}?{}".format(tableau_redirect_server, ticket, redirect_path, params_str)
            logger.info(redirect_url)
            self.redirect(redirect_url)

        logger.info("--------------------------- Finish to get Url request : ---------------------------")
