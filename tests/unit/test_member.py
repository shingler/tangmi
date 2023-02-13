import copy
import json
from datetime import date, timedelta, datetime
from random import randint

import time

from src.member import Member

DEVICE_SERIAL_NO = "121EC1-0D1FCB-0000FF"
person_id_for_test = datetime.now().strftime("%Y%m%d%H%M")
term_days = 30
term_end = date.today() + timedelta(days=term_days)
param_correct = {
    "device_no": DEVICE_SERIAL_NO,
    "person_id": person_id_for_test,
    "phone": "test data from unit test",
    "reg_image": "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",
    "term_start": time.strftime('%Y-%m-%d %H:%M:%S'),
    "term_end": term_end.strftime("%Y-%m-%d 23:59:59"),
    "display_name": "单元测试数据",
    "kind": 0,
}


def test_add(init_app):
    client = Member(init_app.config["MQTT_ADDR"], init_app.config["MQTT_PORT"], device_no=DEVICE_SERIAL_NO)

    # 开始日期为空
    print("===开始日期为空===")
    param1 = copy.deepcopy(param_correct)
    param1["person_id"] = person_id_for_test + str(randint(1, 100))
    param1["phone"] = "test for empty term start"
    param1["term_start"] = ""
    print(param_correct["term_start"] + " : " + param1["term_start"])
    request_id = client.add(param1["person_id"], param1["phone"], param1["reg_image"],
                            kind=param1["kind"], term_start=param1["term_start"],
                            term_end=param1["term_end"], customer_text=param1["display_name"], timeout=30)
    ret = client.get(request_id)
    assert ret is not None
    ret = json.loads(ret)
    print(ret)

    # 结束日期为空
    print("===结束日期为空===")
    param2 = copy.deepcopy(param_correct)
    param2["person_id"] = person_id_for_test + str(randint(1, 100))
    param2["phone"] = "test for empty term end"
    param2["term_end"] = ""
    request_id = client.add(param2["person_id"], param2["phone"], param2["reg_image"],
                            kind=param2["kind"], term_start=param2["term_start"],
                            term_end=param2["term_end"], customer_text=param2["display_name"], timeout=30)
    ret = client.get(request_id)
    assert ret is not None
    ret = json.loads(ret)
    print(ret)

    # 自定义文本为空
    print("===自定义文本为空===")
    param3 = copy.deepcopy(param_correct)
    param3["person_id"] = person_id_for_test + str(randint(1, 100))
    param3["phone"] = "test for empty customer text"
    param3["display_name"] = ""
    request_id = client.add(param3["person_id"], param3["phone"], param3["reg_image"],
                            kind=param3["kind"], term_start=param3["term_start"],
                            term_end=param3["term_end"], customer_text=param3["display_name"], timeout=30)
    ret = client.get(request_id)
    assert ret is not None
    ret = json.loads(ret)
    print(ret)


def test_delete(init_app):
    person_id = "202302131320"
    client = Member(init_app.config["MQTT_ADDR"], init_app.config["MQTT_PORT"], device_no=DEVICE_SERIAL_NO)
    request_id = client.delete(person_id, 30)
    result = client.get(request_id)
    assert result is not None
    result = json.loads(result)
    assert result["code"] == 0


def test_modify(init_app):
    person_id = "202302060002"
    client = Member(init_app.config["MQTT_ADDR"], init_app.config["MQTT_PORT"], device_no=DEVICE_SERIAL_NO)
    term_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    term_end_dt = datetime.now() + timedelta(days=30)
    term_end = term_end_dt.strftime("%Y-%m-%d %H:%M:%S")
    request_id = client.modify(person_id, term_start=term_start, term_end=term_end, customer_text="test modify")
    result = client.get(request_id)
    assert result is not None
    result = json.loads(result)
    assert result["code"] == 0
