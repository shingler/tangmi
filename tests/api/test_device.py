import requests

DEVICE_SERIAL_NO = "121EC1-0D1FCB-0000FF"


def test_unlock(init_app):
    url = init_app.config["API_ADDR"]+"/device/unlock"
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

    # 设备在线
    param3 = param_correct
    res3 = requests.post(url, data=param3)
    assert res3.status_code == 200
    assert res3 is not None
    res3 = res3.json()
    assert res3["status"] == 0
    assert len(res3["result"]) > 0


def test_status(init_app):
    url = init_app.config["API_ADDR"]+"/device/status"
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

    # 设备在线
    param3 = param_correct
    res3 = requests.post(url, data=param3)
    assert res3.status_code == 200
    assert res3.status_code == 200
    res3 = res3.json()
    assert res3["status"] == 0
    assert len(res3["result"]) > 0
    # 设备不在线的情况会导致长时间挂起，暂时无法验证


