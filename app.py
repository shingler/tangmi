#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
from logging import config

from flask import Response, Request, request

from src import create_app
from src.error_code import from_api

app = create_app()
config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf"))


@app.route("/")
def default():
    return Response("It Works!")


@app.route("/callback/unlock", methods=["POST"])
def callback():
    device_no = request.form.get("device_no", "")
    raw_data = request.form.get("data", "")

    # 基本校验
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}

    if len(raw_data) == 0:
        return {"status": -1, "message": "empty data"}
    try:
        json_data = json.loads(raw_data)
        ret = {
            "status": 0,
            "message": "OK",
            "data": json_data
        }
    except Exception as ex:
        ret = {
            "status": -1,
            "message": repr(ex)
        }

    return ret


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=app.config["DEBUG"])
