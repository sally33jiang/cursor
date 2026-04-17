import json
import time
from datetime import datetime

import pytest
import requests

try:
    import pymysql
except ImportError:  # optional dependency
    pymysql = None


ENV_TT = {
    "name": "TT客户",
    "config_url": "http://oms-dev2.ydhex.com",
    "api_url": "http://oms-dev.ydhex.com/webservice/PublicService.asmx/ServiceInterfaceUTF8",
    "credentials": {
        "appToken": "yaft692vqog75dkkz52b1zr4gswbm3iat",
        "appKey": "y9yo7ezjlfzbwsg9sap9qvpytknon0iwffo6p5nufszv9pixlwtloju7u95w1l6u6",
    },
    "database": {
        "host": "rm-uf66ewbxk3w61f78kio.mysql.rds.aliyuncs.com",
        "port": 3306,
        "user": "oms_test",
        "password": "0ZX9oQQZ9G",
        "database": "tms-test",
        "charset": "utf8mb4",
        "pre_sql": "UPDATE sys_system_config SET config_value=1 WHERE config_key='TIKTOK_CUSTOMERS'",
    },
}


def build_params_json(reference_no: str) -> dict:
    return {
        "reference_no": reference_no,
        "platform_id": "1",
        "shipping_method": "YY16",
        "order_weight": 3.0,
        "order_pieces": 1,
        "insurance_value": 0.0,
        "mail_cargo_type": "4",
        "consignee": {
            "consignee_company": "",
            "consignee_province": "大 阪 府",
            "consignee_city": "貝 塚 市",
            "consignee_street": "港 ",
            "consignee_postcode": "5970043",
            "consignee_name": "大 阪 府 ",
            "consignee_telephone": "08172653321",
            "consignee_mobile": "08172653321",
            "consignee_countrycode": "JP",
        },
        "shipper": {
            "shipper_countrycode": "JP",
            "shipper_city": ".",
            "shipper_street": "..",
            "shipper_areacode": "35000000",
            "shipper_name": ".",
            "shipper_telephone": "..",
            "shipper_mobile": "..",
            "shipper_postcode": "35000000",
        },
        "invoice": [
            {
                "invoice_enname": "Dresses",
                "invoice_cnname": "连衣裙",
                "invoice_quantity": 1,
                "unit_code": "PCE",
                "invoice_unitcharge": 15.0,
                "invoice_note": "Dresses",
            }
        ],
    }


def maybe_run_pre_sql():
    """
    可选预处理SQL。
    只有安装了 pymysql 并且允许连库时才会执行。
    """
    if pymysql is None:
        return

    db = ENV_TT["database"]
    conn = pymysql.connect(
        host=db["host"],
        port=db["port"],
        user=db["user"],
        password=db["password"],
        database=db["database"],
        charset=db["charset"],
        autocommit=True,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(db["pre_sql"])
    finally:
        conn.close()


@pytest.mark.api
def test_create_order_tt_customer():
    # reference_no 每次唯一，避免重复下单冲突
    reference_no = f"CCC{datetime.now().strftime('%Y%m%d%H%M%S')}{int(time.time() * 1000) % 1000:03d}"
    params_json = build_params_json(reference_no)

    # 如不需要数据库预处理，可注释这行
    maybe_run_pre_sql()

    payload = {
        "appToken": ENV_TT["credentials"]["appToken"],
        "appKey": ENV_TT["credentials"]["appKey"],
        "serviceMethod": "createorder",
        "paramsJson": json.dumps(params_json, ensure_ascii=False),
    }

    resp = requests.post(
        ENV_TT["api_url"],
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )

    assert resp.status_code == 200, f"HTTP状态码异常: {resp.status_code}, body={resp.text}"

    body = resp.json()
    assert body.get("success") == 1, f"创建失败: {body}"
    assert body.get("cnmessage") == "订单创建成功", f"提示文案不符: {body}"
    assert body.get("data", {}).get("order_id"), f"缺少 order_id: {body}"
    assert body.get("data", {}).get("refrence_no") == reference_no, f"reference_no 不匹配: {body}"
