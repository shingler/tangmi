import copy
import json

from src.mqtt_client import MqttClient


class Member(MqttClient):
    # 消息主题
    MEMBER_REQUEST = "topic/face/manage/request/"
    MEMBER_RESPONSE = "topic/face/manage/response/"

    # 预定义消息模板
    PAYLOAD = {
        "member_get": {
              "cmd": "request persons",
              "role": -1,
              "page_no": 1,
              "page_size": 10,
              "image_flag": 1,
              "query_mode": 0,
              "condition": {}
            },
        "member_add": {
            "cmd": "upload person",

            # 人员ID（长度不超过19字节）
            "id": "",

            # 人员姓名（长度不超过63字节，注意不是字符）
            # 修改时非必须
            "name": "",

            # 注册图像（base64）
            # 支持jpg和png
            # 要求大小500K以下并且分辨率控制在200W(1080P)以内
            "reg_image": "",

            # 非必填字段
            # 人员角色。（1：白名单 2：黑名单）
            # 新增时不传默认为1
            "role": 1,

            # 人员分类。取值范围：0~15。0为不分类，其它用于分时调度。
            # 新增时不传默认为0
            "kind": 0,

            # 有效期起始时间（useless表示不使用该字段）
            # 新增时不传默认为useless
            # 不能超过2038年
            "term_start": "2017/11/10 12:00:00",

            # 有效期截止时间（forever表示永久有效，never表示永久无效）
            # 新增时不传默认为forever
            # 不能超过2038年
            "term": "2017/12/18 16:45:30",

            # 用户自定义文本内容（不超过67字节）
            # 用途如下：
            #    ①平台用户id为UUID，而设备由于历史问题只能存下19字节编号，则可以使用此字段进行对应
            #    ②人员对比成功后的语音播报或屏幕显示可以将此字段作为输出的一部分
            # "customer_text": "",

            # 人员更新模式（0：自动 1：新增 2：修改）
            # 默认为自动，即有就覆盖，没有就新增
            "upload_mode": 1,
        },
        "member_modify": {
            "cmd": "upload person",

            # 必填，人员ID（长度不超过19字节）
            "id": "",

            # 默认，人员更新模式（0：自动 1：新增 2：修改）
            "upload_mode": 2,

            # 以下均为非必填
            # 人员姓名（长度不超过63字节，注意不是字符）
            # 修改时非必须
            # "name": "",

            # 注册图像（base64）
            # 支持jpg和png
            # 要求大小500K以下并且分辨率控制在200W(1080P)以内
            # "reg_image": "",

            # 非必填字段
            # 人员角色。（1：白名单 2：黑名单）
            # 新增时不传默认为1
            # "role": 1,

            # 人员分类。取值范围：0~15。0为不分类，其它用于分时调度。
            # 新增时不传默认为0
            # "kind": 0,

            # 有效期起始时间（useless表示不使用该字段）
            # 新增时不传默认为useless
            # 不能超过2038年
            # "term_start": "2017/11/10 12:00:00",

            # 有效期截止时间（forever表示永久有效，never表示永久无效）
            # 新增时不传默认为forever
            # 不能超过2038年
            # "term": "2017/12/18 16:45:30",

            # 用户自定义文本内容（不超过67字节）
            # 用途如下：
            #    ①平台用户id为UUID，而设备由于历史问题只能存下19字节编号，则可以使用此字段进行对应
            #    ②人员对比成功后的语音播报或屏幕显示可以将此字段作为输出的一部分
            # "customer_text": "",
        },
        "member_delete": {
            # 命令
            "cmd": "delete person(s)",

            # 标记
            # -1：按ID删除
            #  0：删除所有普通人员
            #  1：删除所有白名单人员
            #  2：删除所有黑名单人员
            #  3：删除所有人员记录
            "flag": -1,

            # 人员ID。按ID删除时，值不应为空字符串。
            "id": "0001",
        }
    }

    def getMember(self, timeout=30, person_id=None, person_name=None):
        # 生成request_id并保存
        request_id = self.request_id({"action": "member_get", "person_id": person_id, "person_name": person_name})
        self.save(request_id, None)

        topic = self.MEMBER_REQUEST + self.device_no
        payload = copy.deepcopy(self.PAYLOAD["member_get"])

        if person_id is not None and len(person_id) > 0:
            payload["condition"]["person_id"] = person_id
        if person_name is not None and len(person_name) > 0:
            payload["condition"]["person_name"] = person_name

        # 将发送给mqtt服务的消息做备份
        self.logger.info("payload: %s" % json.dumps(payload))

        # 连接服务器，发送请求
        self.connect()
        self.request(topic, json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.MEMBER_RESPONSE + self.device_no, request_id=request_id, qos=0,
                             timeout=timeout)

        return request_id

    # 注册人员
    def add(self, person_id, person_name, reg_image, kind=0, term_start="useless", term_end="forever", customer_text="", timeout=30):
        # 生成request_id并保存
        request_id = self.request_id({"action": "member_add", "person_id": person_id, "person_name": person_name})
        self.save(request_id, None)

        topic = self.MEMBER_REQUEST + self.device_no
        payload = copy.deepcopy(self.PAYLOAD["member_add"])

        if person_id is None or len(person_id) == 0:
            return False
        if person_name is None or len(person_name) == 0:
            return False
        if reg_image is None or len(reg_image) == 0:
            return False

        payload["id"] = person_id
        payload["name"] = person_name
        payload["reg_image"] = reg_image
        payload["kind"] = kind

        # 开始时间为空，传useless
        payload["term_start"] = term_start
        if len(payload["term_start"]) == 0:
            payload["term_start"] = "useless"

        # 结束时间为空，传forever
        payload["term"] = term_end
        if len(payload["term"]) == 0:
            payload["term"] = "forever"

        if customer_text is not None and len(customer_text) > 0:
            payload["customer_text"] = customer_text

        # 将发送给mqtt服务的消息做备份
        self.logger.info("payload: %s" % json.dumps(payload))

        # 连接服务器，发送请求
        self.connect()
        self.request(topic, json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.MEMBER_RESPONSE + self.device_no, request_id=request_id, qos=0,
                             timeout=timeout)

        return request_id

    # 删除人员
    def delete(self, person_id, timeout=30):
        # 生成request_id并保存
        request_id = self.request_id({"action": "member_delete", "person_id": person_id})
        self.save(request_id, None)

        topic = self.MEMBER_REQUEST + self.device_no
        payload = copy.deepcopy(self.PAYLOAD["member_delete"])
        payload["id"] = person_id

        # 将发送给mqtt服务的消息做备份
        self.logger.info("payload: %s" % json.dumps(payload))

        # 连接服务器，发送请求
        self.connect()
        self.request(topic, json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.MEMBER_RESPONSE + self.device_no, request_id=request_id, qos=0,
                             timeout=timeout)

        return request_id

    # 修改人员信息
    def modify(self, person_id, person_name="", reg_image="", kind=0, term_start="useless", term_end="forever", customer_text="", timeout=30):
        # 生成request_id并保存
        request_id = self.request_id({"action": "member_modify", "person_id": person_id})
        self.save(request_id, None)

        topic = self.MEMBER_REQUEST + self.device_no
        payload = copy.deepcopy(self.PAYLOAD["member_modify"])

        if person_id is None or len(person_id) == 0:
            return False
        payload["id"] = person_id

        if person_name is not None and len(person_name) > 0:
            payload["name"] = person_name
        if reg_image is not None and len(reg_image) > 0:
            payload["reg_image"] = reg_image
        if kind is not None:
            payload["kind"] = kind
        if term_start is not None and len(term_start) > 0:
            payload["term_start"] = term_start
        if term_end is not None and len(term_end) > 0:
            payload["term"] = term_end
        if customer_text is not None and len(customer_text) > 0:
            payload["customer_text"] = customer_text

        # 将发送给mqtt服务的消息做备份
        self.logger.info("payload: %s" % json.dumps(payload))

        # 连接服务器，发送请求
        self.connect()
        self.request(topic, json.dumps(payload), qos=0, retain=False)

        # 阻塞等待返回
        self.waitForResponse(self.MEMBER_RESPONSE + self.device_no, request_id=request_id, qos=0,
                             timeout=timeout)

        return request_id
