# -*- coding: utf-8 -*-

import json
import uuid
from functools import partial
from datetime import datetime
import timeout_decorator
import apache_beam as beam
from beamism.utils import *


class Lambda(beam.DoFn):
    '''
    Parameters:
        func:
            function(dict => (dict, bool, str))
        save_func:
            function(dict => bool)
        pipeline_name: str
        func_version: str
    '''
    def __init__(self,
                 func,
                 input_schema,
                 save_func=None,
                 pipeline_name='',
                 func_version=None,
                 timeout=600):
        self.func = func
        self.input_schema = input_schema
        self.pipeline_name = pipeline_name
        self.save_func = save_func
        self.func_version = func_version
        self.timeout = timeout

    def save(self, output_json, save_mode=True):
        if self.save_func is not None and save_mode:
            is_acknowledged = self.save_func(output_json)
            return is_acknowledged
        return False

    def process(self, msg_text, save_mode=True):
        # Pipelineが処理する一つ一つのJob固有のID( ≠ message_id)
        element_id = str(uuid.uuid4())
        start_utc_time = datetime.utcnow()

        input_json = parse_json_message(msg_text)
        # インプットがJSON形式ではないケース
        if input_json is None:
            output_json = {
                "pipeline": self.pipeline_name,
                "params": { "input_text": msg_text, "error": "parse error" },
                "element_id": element_id,
                "data": None,
                "succeeded": False,
                "message": "Cannot parse this message as json",
                "start_utc_time": str(start_utc_time),
                "end_utc_time": str(datetime.utcnow()),
                "processing_time": (datetime.utcnow() - start_utc_time).total_seconds(),
                "func_version": self.func_version
            }
            self.save(output_json, save_mode)
            return data_packing(output_json)

        # インプットが与えられたスキーマに従っていないケース
        if self.input_schema is not None:
            input_validation_err = validate_json_based_on_schema(input_json, self.input_schema)
            if input_validation_err is not None:
                error_msg = "{0}@{1}".format(input_validation_err.message, ''.join(str(input_validation_err.absolute_path)))
                output_json = {
                    "pipeline": self.pipeline_name,
                    "params": { "input_text": msg_text, "error": "validation error" },
                    "element_id": element_id,
                    "data": None,
                    "succeeded": False,
                    "message": error_msg,
                    "start_utc_time": str(start_utc_time),
                    "end_utc_time": str(datetime.utcnow()),
                    "processing_time": (datetime.utcnow() - start_utc_time).total_seconds(),
                    "func_version": self.func_version
                }
                self.save(output_json, save_mode)
                return data_packing(output_json)

        # 一つ前のJOBが成功していない、もしくは出力のデータが存在しないケース
        if not input_json["succeeded"] or input_json["data"] is None:
            output_jsons = {
                "pipeline": self.pipeline_name,
                "params": input_json["data"],
                "sender_element_id": input_json["element_id"] if "element_id" in input_json else None,
                "element_id": element_id,
                "data": None,
                "succeeded": False,
                "message": input_json["message"],
                "start_utc_time": str(start_utc_time),
                "end_utc_time": str(datetime.utcnow()),
                "processing_time": (datetime.utcnow() - start_utc_time).total_seconds(),
                "func_version": self.func_version
            }
            self.save(output_json, save_mode)
            return data_packing(output_json)

        indata = input_json["data"]

        # timeout処理を挟むためだけの関数
        @timeout_decorator.timeout(self.timeout)
        def main_func():
            return self.func(indata)

        # メインの処理
        results, is_func_success, func_msg = main_func()

        if type(results) != list:
            results = [{}] if results is None else [results]

        # MongoDBへ処理を保存
        output_json_for_mongo = {
            "pipeline": self.pipeline_name,
            "params": input_json["data"],
            "sender_element_id": input_json["element_id"] if "element_id" in input_json else None,
            "element_id": element_id,
            "data": results,
            "succeeded": is_func_success,
            "message": func_msg,
            "start_utc_time": str(start_utc_time),
            "end_utc_time": str(datetime.utcnow()),
            "processing_time": (datetime.utcnow() - start_utc_time).total_seconds(),
            "func_version": self.func_version
        }
        self.save(output_json_for_mongo, save_mode)

        # Pipelineの出力
        outdatas = [merge_jsons(indata, result) for result in results]
        output_jsons = [{ "pipeline": self.pipeline_name,
                          "params": input_json["data"],
                          "sender_element_id": input_json["element_id"] if "element_id" in input_json else None,
                          "element_id": element_id,
                          "data": outdata,
                          "succeeded": is_func_success,
                          "message": func_msg,
                          "start_utc_time": str(start_utc_time),
                          "end_utc_time": str(datetime.utcnow()),
                          "processing_time": (datetime.utcnow() - start_utc_time).total_seconds(),
                          "func_version": self.func_version } for outdata in outdatas]
        return data_packing(output_jsons)
