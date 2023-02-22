import json
import logging
import os
from configparser import ConfigParser

import requests
import sys
from flask import Flask
from paho.mqtt import client as mqtt_client
from logging import config
from src.log import Log

# 设置日志记录
config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf"))
logger = logging.getLogger("mqtt-unlock")


# 连接成功的回调
def on_connect(client, userdata, flags, rc):
    # 记录mqtt服务的状态
    logger.info("Connected with result code: " + str(rc))
    pass


# 收到消息的回调
def on_message(client, userdata, msg):
    # 记录mqtt服务的状态
    print("message received: [%s]" % msg.topic)
    logger.info("message received: [%s]" % msg.topic)
    logger.info(msg.payload.decode("utf-8"))
    # 转发数据给回调接口
    param = {
        "device_no": userdata["device_no"],
        "data": msg.payload
    }
    res = requests.post(userdata["url"], data=param)
    if res.status_code != 200:
        logger.info("request url %s failed, status_code is %s" % (userdata["url"], res.status_code))
        print("request url %s failed, status_code is %s" % (userdata["url"], res.status_code))
    if len(res.content) == 0:
        logger.info("request url %s success, but response is empty." % userdata["url"])
        print("request url %s failed, status_code is %s" % (userdata["url"], res.status_code))
    try:
        res = res.json()
        if res["message"] == "OK":
            logger.info("request url %s success, response is %s." % (userdata["url"], res["data"]))
            print("request url %s success, response is %s." % (userdata["url"], res["data"]))

            # 给设备发消息，确认已收到
            topic = Log.LOG_UNLOCK_RESPONSE + userdata["device_no"]
            payload = Log.PAYLOAD["log_unlock"]

            # 替换数据
            payload_from_device = json.loads(msg.payload)
            payload["cap_time"] = payload_from_device["cap_time"]
            payload["sequence_no"] = payload_from_device["sequence_no"]
            client.publish(topic, json.dumps(payload), qos=0, retain=False)
            print("publish: %s" % payload)

    except Exception as ex:
        logger.info("request url %s failed, exception is %s" % (userdata["url"], repr(ex)))
        print("request url %s failed, exception is %s" % (userdata["url"], repr(ex)))


# 消息被订阅的回调
def on_subscribe(client, userdata, mid, granted_qos):
    # 记录mqtt服务的状态
    logger.info("On Subscribed: qos = %d" % granted_qos)
    pass


#   发布消息回调
def on_publish(client, userdata, mid):
    # 记录mqtt服务的状态
    logger.info("On onPublish: qos = %d" % mid)
    print("on publish, mid = %d" % mid)


#   断开链接回调
def on_disconnect(client, userdata, rc):
    # 记录mqtt服务的状态
    logger.info("Unexpected disconnection rc = " + str(rc))
    pass


if __name__ == "__main__":
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    # 加载配置文件
    app = Flask(__name__)
    # 根据环境读取不同变量
    env_file = os.path.join(os.getcwd(), "env.ini")
    # print(env_file)
    if not os.path.exists(env_file):
        sys.exit("环境文件不存在")
    # 检查环境文件
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

    host = app.config["MQTT_ADDR"]
    port = app.config["MQTT_PORT"]
    client.connect(host, port, keepalive=60)
    # 订阅刷脸数据
    for sn in app.config["DEVICE_SERIAL_NO"]:
        topic = "topic/face/capture/request/"+sn
        client.subscribe(topic)
        client.user_data_set({"device_no": sn, "url": app.config["CALLBACK_URL"]})
    client.loop_forever()
