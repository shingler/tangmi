import json

from src.mqtt_client import MqttClient


class Device(MqttClient):
    # 消息主题
    DEVICE_STATUS_REQUEST = "topic/face/manage/request/"
    DEVICE_STATUS_RESPONSE = "topic/face/manage/response/"

    # 预定义消息模板
    PAYLOAD = {
        "device_status": {"cmd": "get network"},
        "device_unlock": {
            "cmd": "gpio control Extend",
            "port": 1,
            "ctrl_type": "on",
            "ctrl_mode": "test",
            "voicePlay": "No0.pass.wav"
        }
    }

    # 查询设备的在线状态
    # @param timeout int 等待消息超时时间
    def status(self, timeout):
        # 生成request_id并存入全局变量
        request_id = self.request_id({"action": "device_status"})
        self.save(request_id, None)

        # 发送消息
        topic = self.DEVICE_STATUS_REQUEST + self.device_no
        payload = self.PAYLOAD["device_status"]
        self.request(topic, payload=json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.DEVICE_STATUS_RESPONSE + self.device_no, request_id=request_id, qos=0, timeout=timeout)

        return request_id

    # 远程开锁
    # @param timeout int 等待消息超时时间
    def unlock(self, timeout=30):
        # 生成request_id并存入全局变量
        request_id = self.request_id({"action": "device_unlock"})
        self.save(request_id, None)

        # 发送消息
        topic = self.DEVICE_STATUS_REQUEST + self.device_no
        payload = self.PAYLOAD["device_unlock"]
        self.request(topic, payload=json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.DEVICE_STATUS_RESPONSE + self.device_no, request_id=request_id, qos=0,
                             timeout=timeout)

        return request_id
