import pytest

from src.device import Device
from src.mqtt_client import MqttSession

DEVICE_SERIAL_NO = "121EC1-0D1FCB-0000FF"


@pytest.fixture()
def device_instance(init_app):
    app = init_app
    settings = app.config
    client = Device(settings["MQTT_ADDR"], settings["MQTT_PORT"], device_no=DEVICE_SERIAL_NO)
    return client


def test_status(device_instance):
    request_id = device_instance.status(data="")
    assert request_id is not None
    print(request_id)
    assert MqttSession.has(request_id)

