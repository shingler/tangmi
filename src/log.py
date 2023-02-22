from src.mqtt_client import MqttClient


class Log(MqttClient):
    # 消息主题
    LOG_UNLOCK_REQUEST = "topic/face/capture/request/"
    LOG_UNLOCK_RESPONSE = "topic/face/capture/response/"

    # 预定义消息模板
    PAYLOAD = {
        "log_unlock": {
          # 应答标记，字符串格式，固定不变！(必选)
          "reply": "ACK",
          # 应答命令，字符串格式，固定不变！(必选)
          "cmd": "face",
          # 应答码，数字格式，固定不变！(必选)
          "code": 0,
          # 序号，数字格式，与推送过来的一致！！！(必选)
          "sequence_no": 1,
            # 抓拍时间，字符串格式，需要与推送过来的一致！！！(必选)
          "cap_time": "2017/12/18 16:45:30.003",
        },
    }

    # 接收刷脸开门推送
    def receiveUnlockPush(self):
        # 生成request_id并存入全局变量
        request_id = self.request_id({"action": "unlock_log"})
        self.save(request_id, None)

        # 连接服务器，接听推送数据
        self.connect()
        # 阻塞等待返回
        self.waitForResponse(self.LOG_UNLOCK_REQUEST + self.device_no, request_id=request_id, qos=0)

        return request_id
