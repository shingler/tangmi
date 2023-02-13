from flask import Blueprint, current_app
from flask import request

from src.device import Device
from src.error_code import from_api

blueprint = Blueprint("device", __name__, url_prefix="/device")


# 远程手动开锁
# @param string device_no 门禁设备序列号
@blueprint.route("/unlock", methods=["POST"])
def unlock():
    device_no = request.form.get("device_no", "")
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}

    # 向mqtt服务器发布消息
    client = Device(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)
    request_id = client.unlock(current_app.config["WAITING_TIMEOUT"])

    return {"status": 0, "result": client.get(request_id)}


# 检查设备在线状态
# @param string device_no 门禁设备序列号
@blueprint.route("/status", methods=["POST"])
def status():
    device_no = request.form.get("device_no", "")
    # 设备号非空检查，为空返回10001
    if len(device_no) == 0:
        return {"status": 10001, "message": from_api[10001]}
    # 设备号是否有效
    if device_no not in current_app.config["DEVICE_SERIAL_NO"]:
        return {"status": 20001, "message": from_api[20001]}

    # 向mqtt服务器发布消息
    client = Device(current_app.config["MQTT_ADDR"], current_app.config["MQTT_PORT"], device_no=device_no)
    # request_id = client.status(current_app.config["WAITING_TIMEOUT"])
    request_id = client.status(30)

    return {"status": 0, "result": client.get(request_id)}
