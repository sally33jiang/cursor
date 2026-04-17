import allure

from common.http_client import HttpClient


@allure.step("执行登录请求")
def do_login(http_client: HttpClient, path: str, form: dict, headers: dict | None = None):
    return http_client.request(
        method="POST",
        path=path,
        headers=headers or {"Content-Type": "application/x-www-form-urlencoded"},
        form=form,
    )
