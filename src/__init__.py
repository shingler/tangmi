import os
import sys
from configparser import ConfigParser

from flask import Flask

import device
import member
import log


def create_app():
    app = Flask(__name__)
    # 根据环境读取不同变量
    env_file = os.path.join(os.getcwd(), "env.ini")
    # print(env_file)
    if not os.path.exists(env_file):
        sys.exit("环境文件不存在")

    conf = ConfigParser()
    conf.read(env_file, encoding="utf-8")
    if not conf.has_option("env", "env"):
        sys.exit("环境文件格式有误")

    if conf["env"]["env"].lower() == "development":
        app.config.from_object("settings.Development")
    elif conf["env"]["env"].lower() == "test":
        app.config.from_object("settings.Test")
    else:
        app.config.from_object("settings.Product")

    # 注册蓝图
    app.register_blueprint(member.blueprint)
    app.register_blueprint(device.blueprint)
    app.register_blueprint(log.blueprint)

    return app
