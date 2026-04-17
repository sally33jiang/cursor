import allure

from common.http_client import HttpClient


@allure.step("执行登录请求")
def do_login(http_client: HttpClient, username: str, password: str):
    return http_client.request(
        method="POST",
        path="/usercenter/manager/login.aspx",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        form={"username": username, "password": password},
    )
