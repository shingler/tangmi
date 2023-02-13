from flask import Flask

import device
import member
import log


def create_app():
    app = Flask(__name__)
    app.config.from_object("settings.Development")
    # app.config.from_object("settings.Test")
    app.register_blueprint(member.blueprint)
    app.register_blueprint(device.blueprint)
    app.register_blueprint(log.blueprint)

    return app
