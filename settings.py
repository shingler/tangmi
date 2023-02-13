#!/usr/bin/python
# -*- coding:utf-8 -*-


class Base:
    # mqtt服务器地址
    MQTT_ADDR = ""
    # mqtt服务器端口号
    MQTT_PORT = 1883
    # mqtt服务用户名
    MQTT_USER = ""
    # mqtt服务密码
    MQTT_PASSWD = ""
    # 门禁设备序列号
    DEVICE_SERIAL_NO = ["121EC1-0D1FCB-0000FF",]
    # 接口堵塞超时上限（秒）
    WAITING_TIMEOUT = 180
    # 是否开启日志（1=开启，0=不开启）
    LOG_ON = 1
    # 调试模式
    DEBUG = False
    # JSON中文
    JSON_AS_ASCII = False
    JSONIFY_MIMETYPE = "application/json;charset=utf-8"
    # 接口服务器地址
    API_ADDR = ""


# 开发环境
class Development(Base):
    ENV = "Development"
    MQTT_ADDR = "101.43.161.166"
    MQTT_PORT = 1883
    DEBUG = True
    API_ADDR = "http://127.0.0.1:5000"


# 测试环境
class Test(Base):
    ENV = "Test"


# 生产环境
class Production(Base):
    ENV = "production"
    DEBUG = False
