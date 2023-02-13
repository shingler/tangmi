import hashlib
import json
import logging

import time
from paho.mqtt import client as mqtt_client


# 向mqtt服务器发布及订阅消息的通用逻辑，具体操作应继承本类使用
class MqttClient:
    # 设备序列号
    device_no = ""
    # 连接信息
    mqtt_addr = ""
    mqtt_port = ""
    mqtt_user = None
    mqtt_passwd = None
    # mqtt客户端
    client = None
    # 日志
    logger = None

    # 获取mqtt客户端并连接
    def __init__(self, mqtt_addr, mqtt_port, device_no, mqtt_user=None, mqtt_passwd=None):
        self.device_no = device_no
        self.mqtt_addr = mqtt_addr
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_passwd = mqtt_passwd

        self.client = getClient()
        self.logger = logging.getLogger("mqtt")

    # 生成请求id
    def request_id(self, data):
        if len(data) == 0 or data is None:
            data = {}
        datastr = json.dumps(data) + str(int(time.time()))
        return hashlib.md5(datastr.encode()).hexdigest()[:16]

    # 将请求id与请求内容存入全局变量中
    def save(self, key, value):
        MqttSession.set(key, value)

    # 全局变量访问器
    def get(self, key):
        return MqttSession.get(key)

    # 检查全局变量是否返回结果
    def check(self, key):
        return True if MqttSession.get(key) is not None else False

    # 访问mqtt代理，向对应主题发消息（被子类负责具体命令的方法调用）
    def request(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos=qos, retain=retain)

    # 订阅主题并等待回复
    def waitForResponse(self, topic, request_id, qos=0, timeout=180):
        self.client.subscribe(topic=topic, qos=qos)
        self.client.user_data_set({"request_id": request_id})
        self.client.loop_forever(timeout=timeout, retry_first_connection=False)

    # 连接资源
    def connect(self):
        self.client.connect(host=self.mqtt_addr, port=self.mqtt_port)

    # 中端连接，释放资源
    def disconnect(self):
        self.client.disconnect()


# 用于保存和设备交互的问答信息
class MqttSession(object):
    __session = dict()

    @classmethod
    def set(cls, key, value):
        cls.__session[key] = value

    @classmethod
    def get(cls, key):
        return cls.__session[key] if key in cls.__session.keys() else None

    @classmethod
    def has(cls, key):
        return key in cls.__session.keys()


# 返回mqtt连接客户端
def getClient():
    logger = logging.getLogger("mqtt")
    # 连接成功的回调
    def on_connect(client, userdata, flags, rc):
        # 记录mqtt服务的状态
        logger.info("Connected with result code: " + str(rc))
        pass

    # 收到消息的回调
    def on_message(client, userdata, msg):
        # 记录mqtt服务的状态
        logger.info("message received: [%s]" % msg.topic)
        logger.info(msg.payload.decode("utf-8"))

        if MqttSession.has(userdata["request_id"]):
            MqttSession.set(userdata["request_id"], msg.payload.decode("utf-8"))
            logger.info("message was stored.")
            client.disconnect()

    # 消息被订阅的回调
    def on_subscribe(client, userdata, mid, granted_qos):
        # 记录mqtt服务的状态
        logger.info("On Subscribed: qos = %d" % granted_qos)
        pass

    #   发布消息回调
    def on_publish(client, userdata, mid):
        # 记录mqtt服务的状态
        logger.info("On onPublish: qos = %d" % mid)
        pass

    #   断开链接回调
    def on_disconnect(client, userdata, rc):
        # 记录mqtt服务的状态
        logger.info("Unexpected disconnection rc = " + str(rc))
        pass

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    return client
