#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from logging import config

from flask import Response

from src import create_app

app = create_app()
config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf"))


@app.route("/")
def default():
    return Response("It Works!")


app.run(host="0.0.0.0", debug=app.config["DEBUG"])
