from tuya_connector import TuyaOpenAPI, TUYA_LOGGER

ACCESS_ID    = "nny57p4jxca8yqfuexuw"
ACCESS_KEY   = "4392af21ec0941c0b7e361e1a2941eab"
API_ENDPOINT = "https://openapi.tuyaeu.com"
DEVICE_ID    = "bf8d29bd269d322452dbgu"

TUYA_LOGGER.setLevel("INFO")

api = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
api.connect()

def get_device_status():
    res = api.get(f"/v1.0/devices/{DEVICE_ID}/status")
    m = {d["code"]: d["value"] for d in res.get("result", [])}
    return {
        "switch":  m.get("switch_1", False),
        "power":   float(m.get("cur_power",   0)) / 10.0,
        "current": float(m.get("cur_current", 0)) / 1000.0,
        "voltage": float(m.get("cur_voltage", 0)) / 10.0,
    }

def turn_on():
    body = {"commands":[{"code":"switch_1","value":True}]}
    return api.post(f"/v1.0/devices/{DEVICE_ID}/commands", body)

def turn_off():
    body = {"commands":[{"code":"switch_1","value":False}]}
    return api.post(f"/v1.0/devices/{DEVICE_ID}/commands", body)
