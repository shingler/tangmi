#!/usr/bin/python
# -*- coding:utf-8 -*-
import pytest
import requests
from flask import Flask
from configparser import ConfigParser
import os


@pytest.fixture(scope="session")
def init_app():
    app = Flask(__name__)
    # 根据环境读取不同变量
    env_file = os.path.join(os.getcwd(), "..", "..", "env.ini")
    # print(env_file)
    if not os.path.exists(env_file):
        pytest.exit("环境文件不存在", returncode=1)

    conf = ConfigParser()
    conf.read(env_file, encoding="utf-8")
    if not conf.has_option("env", "env"):
        pytest.exit("环境文件格式有误", returncode=1)

    if conf["env"]["env"].lower() == "development":
        app.config.from_object("settings.Development")
    elif conf["env"]["env"].lower() == "test":
        app.config.from_object("settings.Test")
    else:
        app.config.from_object("settings.Product")

    app_context = app.app_context()
    app_context.push()

    return app


# 先确定http服务是否正常
@pytest.fixture(scope="session")
def test_server_is_run(init_app):
    url = init_app.config["API_ADDR"]
    try:
        res = requests.get(url)
        assert res.status_code == 200
        assert res.content == "It Works!"
    except Exception:
        pytest.exit("目标服务未开启", returncode=1)
