# API 自动化测试骨架

## 目录分层

- `config/`：公共配置、不同客户配置（YAML）
- `data/`：测试数据（YAML）
- `common/`：通用能力（YAML读取、配置管理、请求封装、DB操作）
- `ops/`：业务操作封装（例如登录）
- `testcases/`：测试用例（只编排步骤和断言）

## 安装依赖

```bash
pip install -r api_tests/requirements.txt
```

## 运行用例

```bash
pytest api_tests --customer "TT客户" --alluredir=api_tests/reports/allure-results
```

## 生成并打开 Allure 报告

```bash
allure generate api_tests/reports/allure-results -o api_tests/reports/allure-report --clean
allure open api_tests/reports/allure-report
```

## 数据库前后置与回滚

- 在 `config/environments.yaml` 的 `database.pre_sql` 配置测试前 SQL
- 在 `config/environments.yaml` 的 `database.rollback_sql` 配置测试后回滚 SQL
- `db_guard` fixture 会在每条用例执行前后自动调用

## 示例说明

- `testcases/test_create_order.py` 展示了：
  - 下单数据从 `data/create_order_cases.yaml` 读取
  - 请求结构使用官方格式：`appToken/appKey/serviceMethod/paramsJson`
  - `reference_no` 在运行时自动生成唯一值，避免重复冲突
  - 下单请求从 `ops/order_ops.py` 统一封装
