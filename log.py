from flask import Blueprint

blueprint = Blueprint("log", __name__, url_prefix="/log")


# 查看开锁记录
# @param string company_code 公司代码
# @param string api_code 执行代码
# @param string command_code 01=cust_vend, 02=fa, 03=invoice, 04=other
# @param int retry 是否重试。retry=0将按照地址1执行；为1则按照地址2执行。
# @param int api_type 接口类型：1=JSON API，2=XML
# @param string options 指定参数，格式为JSON
@blueprint.route("/log/unlock", methods=["POST"])
def unlock():
    pass
