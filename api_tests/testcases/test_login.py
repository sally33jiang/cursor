import allure
import pytest

from common.template import render_value
from conftest import load_case_file
from ops.login_ops import do_login


CASES = load_case_file("login_cases.yaml")


@allure.feature("用户中心")
@allure.story("登录")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_login(case, http_client, credentials, db_guard):
    context = {
        "username": credentials.get("username", ""),
        "password": credentials.get("password", ""),
    }
    req = render_value(case["request"], context)

    with allure.step(f"执行用例: {case['title']}"):
        response = do_login(
            http_client=http_client,
            username=req["form"]["username"],
            password=req["form"]["password"],
        )

    with allure.step("断言响应"):
        assert response.status_code == case["validate"]["status_code"], response.text
        for item in case["validate"].get("contains", []):
            assert item in response.text, f"响应中缺少关键字: {item}, body={response.text}"
