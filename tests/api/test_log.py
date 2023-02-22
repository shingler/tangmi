import copy
import json

import requests

DEVICE_SERIAL_NO = "121EC1-0D1FCB-0000FF"


def test_unlock(init_app):
    url = init_app.config["API_ADDR"]+"/callback/unlock"
    param_correct = {
        "device_no": DEVICE_SERIAL_NO
    }
    # device_no非空检查
    param1 = {}
    res1 = requests.post(url, data=param1)
    assert res1.status_code == 200
    result1 = res1.json()
    assert result1["status"] == 10001

    # 不存在的device_no
    param2 = {"device_no": "123456"}
    res2 = requests.post(url, data=param2)
    assert res2.status_code == 200
    res2 = res2.json()
    assert res2["status"] == 20001

    # 发送空数据
    param3 = param_correct
    res3 = requests.post(url, data=param3)
    assert res3.status_code == 200
    assert res3 is not None
    res3 = res3.json()
    assert res3["status"] == -1

    # 发送数据
    param4 = copy.deepcopy(param_correct)
    # 测试数据
    param4["data"] = json.dumps({"title": "title", "body": "body"})
    res4 = requests.post(url, data=param4)
    assert res4.status_code == 200
    assert res4 is not None
    res4 = res4.json()
    assert res4["status"] == 0
    assert res4["message"] == "OK"
    assert len(res4["data"]) > 0

