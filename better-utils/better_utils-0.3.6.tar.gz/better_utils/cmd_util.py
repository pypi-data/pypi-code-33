# -*- coding: utf-8 -*-
import subprocess


class CmdUtil:
    @staticmethod
    def exe_unreturn(cmd):
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    @staticmethod
    def exe(cmd):
        '''
        Execute a child program in a new process
        返回结果或空串
        '''
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out = p.communicate()[0]
        return out

