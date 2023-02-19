#!/usr/bin/python
# -*- coding:utf-8 -*-
import pytest
import requests
from flask import Flask


@pytest.fixture(scope="session")
def init_app():
    app = Flask(__name__)
    app.config.from_object("settings.Development")
    # app.config.from_object("settings.Test")

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
