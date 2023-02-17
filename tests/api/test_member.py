import copy
from random import randint

import time
from datetime import date, timedelta, datetime

import pytest
import requests

DEVICE_SERIAL_NO = "121EC1-0D1FCB-0000FF"
# 默认参照账户
default_person = {
    "person_id": "2023020512563323845",
    "phone": "shingler",
    "reg_image": "https://ts1.cn.mm.bing.net/th/id/R-C.ee0b76e1ca6a8404a456cd622803f836?rik=Z%2bCLE9S0Y0hRxA&riu=http%3a%2f%2fpic1.16xx8.com%2fallimg%2f1ibmr3%2f16xx887829a4x1.jpg&ehk=zcrntuKjdOV9nXurUqwgO9to6hQh%2fHYW1KZMU4%2bkWNg%3d&risl=&pid=ImgRaw&r=0",

}
# 注册成功的账号（便于修改和删除）
success_persons = []


def test_add(init_app):
    person_id_for_test = datetime.now().strftime("%Y%m%d%H%M")
    url = init_app.config["API_ADDR"] + "/member/add"
    term_days = 30
    term_end = date.today() + timedelta(days=term_days)
    param_correct = {
        "device_no": DEVICE_SERIAL_NO,
        "person_id": person_id_for_test,
        "phone": "18611106295",
        "reg_image": "https://ts1.cn.mm.bing.net/th/id/R-C.ee0b76e1ca6a8404a456cd622803f836?rik=Z%2bCLE9S0Y0hRxA&riu=http%3a%2f%2fpic1.16xx8.com%2fallimg%2f1ibmr3%2f16xx887829a4x1.jpg&ehk=zcrntuKjdOV9nXurUqwgO9to6hQh%2fHYW1KZMU4%2bkWNg%3d&risl=&pid=ImgRaw&r=0",
        "term_start": time.strftime('%Y-%m-%d %H:%M:%S'),
        "term_end": term_end.strftime("%Y-%m-%d 23:59:59"),
        "display_name": "老乐",
        "kind": 0,
    }

    # 设备号为空
    param1 = {}
    res1 = requests.post(url, param1)
    assert res1.status_code == 200
    assert res1.json()["status"] == 10001

    # 设备号不存在
    param2 = {"device_no": "123456"}
    res2 = requests.post(url, param2)
    assert res2.status_code == 200
    assert res2.json()["status"] == 20001

    # 人员id为空
    param9 = copy.deepcopy(param_correct)
    param9["person_id"] = ""
    res9 = requests.post(url, param9)
    assert res9.status_code == 200
    res9 = res9.json()
    assert res9["status"] == 10005

    # 手机号为空
    param3 = copy.deepcopy(param_correct)
    param3["phone"] = ""
    res3 = requests.post(url, param3)
    assert res3.status_code == 200
    assert res3.json()["status"] == 10003

    # 人像为空
    param4 = copy.deepcopy(param_correct)
    param4["reg_image"] = ""
    res4 = requests.post(url, param4)
    assert res4.status_code == 200
    assert res4.json()["status"] == 10004

    # 非人脸图像
    param14 = copy.deepcopy(param_correct)
    param14["phone"] = "test for picture without person\'s face"
    param14[
        "reg_image"] = "https://ts1.cn.mm.bing.net/th/id/R-C.243e79d2fcb64ada4702bd4593e7d3f7?rik=bvAhurflqw4Y9A&riu=http%3a%2f%2fwww.quazero.com%2fuploads%2fallimg%2f140303%2f1-140303214S3.jpg&ehk=N2TUq%2fL6le4NSp9spwx0kC1dqWnBSvE%2byT6c9kjDe0I%3d&risl=&pid=ImgRaw&r=0"
    res14 = requests.post(url, param14)
    assert res14.status_code == 200
    assert res14.json()["status"] == 25

    # 手机号已存在
    param5 = copy.deepcopy(param_correct)
    param5["phone"] = default_person["phone"]
    res5 = requests.post(url, param5)
    assert res5.status_code == 200
    assert res5.json()["status"] == 30002

    # 人员id已存在
    param6 = copy.deepcopy(param_correct)
    param6["person_id"] = default_person["person_id"]
    res6 = requests.post(url, param6)
    assert res6.status_code == 200
    assert res6.json()["status"] == 30002

    # 有效期结束时间小于开始时间
    param7 = copy.deepcopy(param_correct)
    term_end = date.today()-timedelta(days=2)
    param7["term_end"] = term_end.strftime("%Y-%m-%d 23:59:59")
    res7 = requests.post(url, param7)
    assert res7.status_code == 200
    assert res7.json()["status"] == 30005

    # 正常注册
    param8 = copy.deepcopy(param_correct)
    res8 = requests.post(url, param8)
    assert res8.status_code == 200
    res8 = res8.json()
    assert res8["status"] == 0
    assert len(res8["result"]["id"]) > 0
    # 记录id
    success_persons.append(res8["result"]["id"])

    # 其他参数验证（不影响流程，仅验证结果）

    # 有效期开始为空（人员id置空是为了方便测试删除，顺便清理测试数据）
    param10 = copy.deepcopy(param_correct)
    param10["person_id"] = person_id_for_test + str(randint(1, 100))
    param10["phone"] = "test for empty term start"
    param10["term_start"] = ""
    print(param10)
    res10 = requests.post(url, param10)
    assert res10.status_code == 200
    res10 = res10.json()
    assert res10["status"] == 0
    assert res10["result"]["code"] == 0
    assert len(res10["result"]["id"]) > 0
    # 记录id
    success_persons.append(res10["result"]["id"])

    # 有效期结束为空（人员id置空是为了方便测试删除，顺便清理测试数据）
    param11 = copy.deepcopy(param_correct)
    param11["person_id"] = person_id_for_test + str(randint(1, 100))
    param11["phone"] = "test for empty term end"
    param11["term_end"] = ""
    res11 = requests.post(url, param11)
    assert res11.status_code == 200
    res11 = res11.json()
    assert res11["status"] == 0
    assert res11["result"]["code"] == 0
    assert len(res11["result"]["id"]) > 0
    # 记录id
    success_persons.append(res11["result"]["id"])

    # 显示姓名为空（人员id置空是为了方便测试删除，顺便清理测试数据）
    param12 = copy.deepcopy(param_correct)
    param12["person_id"] = person_id_for_test + str(randint(1, 100))
    param12["phone"] = "test for empty display name"
    param12["display_name"] = ""
    res12 = requests.post(url, param12)
    assert res12.status_code == 200
    res12 = res12.json()
    assert res12["status"] == 0
    assert res12["result"]["code"] == 0
    assert len(res12["result"]["id"]) > 0
    # 记录id
    success_persons.append(res12["result"]["id"])

    # 相同的人像（设备pc端开启了禁止重复人脸注册时）
    # param13 = copy.deepcopy(param_correct)
    # param13["reg_image"] = default_person["reg_image"]
    # res13 = requests.post(url, param13)
    # assert res13.status_code == 200
    # assert res13.json()["status"] == 16


def test_modify(init_app):
    param_correct = {
        "device_no": DEVICE_SERIAL_NO,
        "person_id": ""
    }
    url = init_app.config["API_ADDR"] + "/member/modify"
    # 设备号为空
    param1 = {"device_no": ""}
    res1 = requests.post(url, param1)
    assert res1.status_code == 200
    assert res1.json()["status"] == 10001

    # 设备号不存在
    param2 = {"device_no": "123456"}
    res2 = requests.post(url, param2)
    assert res2.status_code == 200
    assert res2.json()["status"] == 20001

    # 人员id为空
    param3 = copy.deepcopy(param_correct)
    param3["person_id"] = ""
    res3 = requests.post(url, param3)
    assert res3.status_code == 200
    res3 = res3.json()
    assert res3["status"] == 10005

    # id不存在
    param4 = copy.deepcopy(param_correct)
    param4["person_id"] = "111"
    res4 = requests.post(url, param4)
    assert res4.status_code == 200
    assert res4.json()["status"] == 30001

    # 要修改的手机号已存在
    param5 = copy.deepcopy(param_correct)
    param5["person_id"] = default_person["person_id"]
    param5["phone"] = default_person["phone"]

    res5 = requests.post(url, param5)
    assert res5.status_code == 200
    assert res5.json()["status"] == 30002

    # 下面的逻辑为各种情况的修改测试
    # success_persons.append(202302060002)

    if len(success_persons) == 0:
        pytest.exit(reason="无数据")

    print(success_persons)
    for pid in success_persons:
        print("modify %s" % pid)
        param6 = copy.deepcopy(param_correct)
        param6["person_id"] = pid
        # 将到期时间改为从现在开始的10天以后
        term_end_dt = datetime.now() + timedelta(days=90)
        param6["term_end"] = term_end_dt.strftime("%Y-%m-%d %H:%M:%S")
        # 将自定义名称改为四位随机数
        param6["display_name"] = str(randint(1000,9999))

        res6 = requests.post(url, param6)
        assert res6.status_code == 200
        assert res6.json()["status"] == 0


def test_check(init_app):
    url = init_app.config["API_ADDR"]+"/member/get"
    param_correct = {
        "device_no": DEVICE_SERIAL_NO,
        "person_id": "2023020512563323845",
        "phone": "shingler"
    }

    # 设备号为空
    param1 = {}
    res1 = requests.post(url, param1)
    assert res1.status_code == 200
    assert res1.json()["status"] == 10001

    # 设备号不存在
    param2 = {"device_no": "123456"}
    res2 = requests.post(url, param2)
    assert res2.status_code == 200
    assert res2.json()["status"] == 20001

    # 人员id及姓名均为空
    param3 = {"device_no": DEVICE_SERIAL_NO}
    res3 = requests.post(url, param3)
    assert res3.status_code == 200
    assert res3.json()["status"] == 10002

    # 人员id为空，人员姓名不为空且不存在
    param4 = copy.deepcopy(param_correct)
    param4["person_id"] = None
    param4["phone"] = "aaa"
    res4 = requests.post(url, param4)
    assert res4.status_code == 200
    assert res4.json()["status"] == 30001

    # 人员id为空，人员姓名不为空且存在
    param5 = copy.deepcopy(param_correct)
    param5["person_id"] = None
    res5 = requests.post(url, param5)
    assert res5.status_code == 200
    res5 = res5.json()
    assert res5["status"] == 0
    assert len(res5["result"]) > 0
    assert res5["result"][0]["id"] == param_correct["person_id"]

    # 人员姓名为空，人员id不为空且不存在
    param6 = copy.deepcopy(param_correct)
    param6["phone"] = None
    param6["person_id"] = "111"
    res6 = requests.post(url, param6)
    assert res6.status_code == 200
    assert res6.json()["status"] == 30001

    # 人员姓名为空，人员id不为空且存在
    param7 = copy.deepcopy(param_correct)
    param7["phone"] = None
    res7 = requests.post(url, param7)
    assert res7.status_code == 200
    res7 = res7.json()
    assert res7["status"] == 0
    assert len(res7["result"]) > 0
    assert res7["result"][0]["name"] == param_correct["phone"]

    # 人员姓名及id均不为空且不存在
    param8 = copy.deepcopy(param_correct)
    param8["person_id"] = "111"
    param8["phone"] = "aaa"
    res8 = requests.post(url, param8)
    assert res8.status_code == 200
    assert res8.json()["status"] == 30001

    # 人员姓名及id均不为空且存在但不对应
    param9 = copy.deepcopy(param_correct)
    param9["person_id"] = "202302060002"
    res9 = requests.post(url, param9)
    assert res9.status_code == 200
    assert res9.json()["status"] == 30001

    # 人员姓名及id均不为空且存在并对应
    param10 = copy.deepcopy(param_correct)
    res10 = requests.post(url, param10)
    assert res10.status_code == 200
    res10 = res10.json()
    assert res10["status"] == 0
    assert len(res10["result"]) > 0
    assert res10["result"][0]["name"] == param_correct["phone"]


def test_delete(init_app):
    param_correct = {
        "device_no": DEVICE_SERIAL_NO,
        "person_id": ""
    }
    url = init_app.config["API_ADDR"] + "/member/delete"
    # 设备号为空
    param1 = {"device_no": ""}
    res1 = requests.post(url, param1)
    assert res1.status_code == 200
    assert res1.json()["status"] == 10001

    # 设备号不存在
    param2 = {"device_no": "123456"}
    res2 = requests.post(url, param2)
    assert res2.status_code == 200
    assert res2.json()["status"] == 20001

    # 人员id为空
    param3 = copy.deepcopy(param_correct)
    param3["person_id"] = ""
    res3 = requests.post(url, param3)
    assert res3.status_code == 200
    res3 = res3.json()
    assert res3["status"] == 10005

    # id不存在
    param4 = copy.deepcopy(param_correct)
    param4["person_id"] = "111"
    res4 = requests.post(url, param4)
    assert res4.status_code == 200
    assert res4.json()["status"] == 30001

    # 删除
    if len(success_persons) == 0:
        pytest.exit(reason="无数据")

    print(success_persons)
    for pid in success_persons:
        print("deleting %s" % pid)
        param5 = copy.deepcopy(param_correct)
        param5["person_id"] = pid
        res5 = requests.post(url, param5)
        assert res5.status_code == 200
        assert res5.json()["status"] == 0