import json
from datetime import datetime

from flask import Blueprint, current_app, request

from src.error_code import from_api, from_device
from src.member import Member
from src.utility import imageUrl2Base64

blueprint = Blueprint("member", __name__, url_prefix="/member")


# 给一个手机号新增权限
# @param string device_no 必填，设备序列号
# @param string person_id 必填，人员ID（不超过19字节），建议将系统的人员id直接传过来保持一致
# @param string phone 必填，人员手机号
# @param string display_name 显示在刷脸成功后终端上的名字
# @param string reg_image 必填，图像url
# @param string term_start 有效期开始时间，不填则会存为useless，即不使用该字段
# @param string term_end 有效期结束时间，不填则会存为forever，即永久有效
@blueprint.route("/add", methods=["POST"])
def add():
    device_no = request.form.get("device_no", "")
    phone = request.form.get("phone", "")
    display_name = request.form.get("display_name", "")
    person_id = request.form.get("person_id", "")
    reg_image = request.form.get("reg_image", "")
    term_start = request.form.get("term_start", "useless")
    term_end = request.form.get("term_end", "forever")

    # 基本校验
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}
    # 检查人员手机号
    if len(phone) == 0:
        return {"status": 10003, "message": from_api[10003]}
    if len(person_id) == 0:
        return {"status": 10005, "message": from_api[10005]}
    # 检查人像不为空
    if len(reg_image) == 0:
        return {"status": 10004, "message": from_api[10004]}
    # 人像url解码
    reg_image_bstring = imageUrl2Base64(reg_image, origin_output=False)
    if not reg_image_bstring:
        return {"status": 30003, "message": from_api[30003]}
    reg_image_bstring = bytes.decode(reg_image_bstring)

    # 有效期范围检查
    if len(term_start) > 0 and len(term_end) > 0 and term_start != "useless" and term_end not in ["never", "forever"] \
            and datetime.timestamp(datetime.strptime(term_start, "%Y-%m-%d %H:%M:%S")) > datetime.timestamp(
        datetime.strptime(term_end, "%Y-%m-%d %H:%M:%S")):
        return {"status": 30005, "message": from_api[30005]}

    # 重复注册检查
    client = Member(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)

    request_id = client.getMember(person_id=person_id)
    ret = json.loads(client.get(request_id))

    if ret["total"] > 0:
        return {"status": 30002, "message": from_api[30002]}

    request_id = client.getMember(person_name=phone)
    res = client.get(request_id)

    ret = json.loads(res)
    if ret["total"] > 0:
        return {"status": 30002, "message": from_api[30002]}

    # 执行注册
    request_id = client.add(person_id, phone, reg_image_bstring, kind=0,
                            term_start=term_start, term_end=term_end, customer_text=display_name, timeout=30)
    ret = client.get(request_id)
    if ret is not None:
        ret = json.loads(ret)
        if ret["code"] == 0:
            # 注册成功
            return {"status": 0, "result": {"code": 0, "id": ret["id"]}}
        else:
            # 注册失败
            return {"status": ret["code"], "message": from_device[ret["code"]]}

    return {"status": 30007, "message": from_api[30007]}


# 删除指定手机号的权限
# @param string device_no 设备序列号
# @param string person_id 人员id
@blueprint.route("/delete", methods=["POST"])
def delete():
    device_no = request.form.get("device_no", "")
    person_id = request.form.get("person_id", "")

    # 基本校验
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}
    # 检查人员id
    if len(person_id) == 0:
        return {"status": 10005, "message": from_api[10005]}

    # id是否存在
    client = Member(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)

    request_id = client.getMember(person_id=person_id)
    ret = json.loads(client.get(request_id))

    if ret["total"] == 0:
        return {"status": 30001, "message": from_api[30001]}

    # 执行删除
    request_id = client.delete(person_id, timeout=30)
    ret = client.get(request_id)
    if ret is not None:
        ret = json.loads(ret)
        if ret["code"] == 0:
            # 删除成功
            return {"status": 0, "result": {"code": 0, "id": ret["id"]}}
        else:
            # 删除失败
            return {"status": ret["code"], "message": from_device[ret["code"]]}

    return {"status": 30007, "message": from_api[30007]}


# 修改人员信息，除了人员id，其他资料不填则不修改
# @param string device_no 必填，设备序列号
# @param string person_id 必填，人员ID（不超过19字节），建议将系统的人员id直接传过来保持一致
# @param string phone 人员手机号
# @param string display_name 显示在刷脸成功后终端上的名字
# @param string reg_image 注册图像(base64)，注：以元数据开始，不要加文件描述
# @param string term_start 有效期开始时间，不填则会存为useless，即不使用该字段
# @param string term_end 有效期结束时间，不填则会存为forever，即永久有效
@blueprint.route("/modify", methods=["POST"])
def modify():
    device_no = request.form.get("device_no", "")
    phone = request.form.get("phone", "")
    display_name = request.form.get("display_name", "")
    person_id = request.form.get("person_id", "")
    reg_image = request.form.get("reg_image", "")
    term_start = request.form.get("term_start", "")
    term_end = request.form.get("term_end", "")

    # 基本校验
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}
    # 检查人员id
    if len(person_id) == 0:
        return {"status": 10005, "message": from_api[10005]}

    # 有效期范围检查
    if len(term_start) > 0 and len(term_end) > 0 and term_start != "useless" and term_end not in ["never", "forever"] \
            and datetime.timestamp(datetime.strptime(term_start, "%Y-%m-%d %H:%M:%S")) > datetime.timestamp(
        datetime.strptime(term_end, "%Y-%m-%d %H:%M:%S")):
        return {"status": 30005, "message": from_api[30005]}

    client = Member(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)

    # id是否存在检查
    request_id = client.getMember(person_id=person_id)
    res = client.get(request_id)
    res = json.loads(res)
    if res["total"] == 0:
        return {"status": 30001, "message": from_api[30001]}

    # 手机号重复检查
    if len(phone) > 0:
        request_id = client.getMember(person_name=phone)
        res = client.get(request_id)
        ret = json.loads(res)
        if ret["total"] > 0:
            return {"status": 30002, "message": from_api[30002]}

    # 执行修改
    request_id = client.modify(person_id, phone, reg_image, kind=0,
                               term_start=term_start, term_end=term_end, customer_text=display_name, timeout=30)
    ret = client.get(request_id)
    if ret is not None:
        ret = json.loads(ret)
        if ret["code"] == 0:
            # 修改成功
            return {"status": 0, "result": {"code": 0, "id": ret["id"]}}
        else:
            # 修改失败
            return {"status": ret["code"], "message": from_device[ret["code"]]}

    return {"status": 30007, "message": from_api[30007]}


# 查看指定手机号的权限
# @param string device_no 必填，设备序列号
# @param string person_id 人员id（记录在设备中的人员id，建议在新录入时与原系统id相同
# @param string phone 人员手机号
@blueprint.route("/get", methods=["POST"])
def getMember():
    device_no = request.form.get("device_no", "")
    person_id = request.form.get("person_id", "")
    phone = request.form.get("phone", "")

    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}
    # 检查人员id与手机号
    if len(person_id) == 0 and len(phone) == 0:
        return {"status": 10002, "message": from_api[10002]}

    # 向mqtt服务器发布消息
    client = Member(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)
    request_id = client.getMember(person_id=person_id, person_name=phone, timeout=current_app.config["WAITING_TIMEOUT"])
    ret = json.loads(client.get(request_id))

    if ret["total"] > 0:
        return {"status": 0, "result": ret["persons"]}
    else:
        return {"status": 30001, "message": from_api[30001]}
