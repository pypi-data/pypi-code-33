# 日志获取的远程接口
from datetime import datetime

from schedule.utils.log import TaskLogFileAppender
from . import remote
from flask import request, jsonify

@remote.route('/remote/log-read-service/<log_id>/<trigger_time>', methods=['GET'])
def log_detail(trigger_time, log_id):
    from_line_num = request.args.get("fromLineNum", default=0)
    to_line_num = request.args.get("toLineNum", default=-1)
    # 获取日志文件
    return jsonify(TaskLogFileAppender.read_log(datetime.fromtimestamp(trigger_time),log_id,from_line_num,to_line_num))