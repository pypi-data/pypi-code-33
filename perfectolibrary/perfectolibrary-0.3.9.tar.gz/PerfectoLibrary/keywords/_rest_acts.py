import perfecto
import os
import robot
import inspect
import urllib2
import PerfectoLibrary

# import urlparse
from perfecto import *
from robot.libraries.BuiltIn import BuiltIn
from appium import webdriver
from .keywordgroup import KeywordGroup
from ._devices import _DeviceKeywords
from urllib import quote_plus


class _RestKeywords(KeywordGroup):
    def __init__(self):
        self.bi = BuiltIn()
        self.securityToken=None
        self.user=None
        self.password=None
        self.host=None

    def _perform_rest_request(self,url):
        '''
        :param url:
        :return:
        '''
        return urllib2.urlopen(url).read()
    
    def _exeRestCmd(self,cmd,subcmd,params):
        '''

        :param cmd:
        :param subcmd:
        :param params:
        :return:
        '''
        actions={}
        actions['command'] = cmd
        actions['subcommand'] = subcmd
        if self._check_driver():
            if('deviceId' not in params):
                params['deviceId'] = self.driver.capabilities['devicename']
            svcStr="executions/"+self.driver.capabilities['executionId']
            return self._exe_restops("command",svcStr,actions,params)

    def set_credentials(self,user,password):
        '''

        :param user:
        :param password:
        :return:
        '''
        self.user=user
        self.password=password

    def set_securityToken(self,securityToken):
        '''
        :param securityToken:
        :return:
        '''
        self.securityToken=securityToken
    def set_host(self,host):
        '''
        :param host:
        :return:
        '''
        self.host=host
    def retrieve_Device_Info(self,deviceid):
        '''

        :param deviceid:
        :return:
        '''
        acts={}
        params={}
        svcStr="handsets/"+deviceid
        # self.bi.log_to_console( "in retrieve_Device_Info")
        self.bi.log_to_console(self._exe_restops("info",svcStr,acts,params))
        
    def start_network_virtualization(self,deviceid,profile):
        '''

        :param deviceid:
        :param profile:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        params['profile']=profile
        self.bi.log_to_console(self._exeRestCmd("vnetwork","start",params))
        
    def update_network_virtualization(self,deviceid,profile):
        '''

        :param deviceid:
        :param profile:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        params['profile']=profile
        self.bi.log_to_console(self._exeRestCmd("vnetwork","update",params))
        
        
    def stop_network_virtualization(self,deviceid):
        '''

        :param deviceid:
        :return:
        '''
        params={}
        params['deviceId']=deviceid
        self.bi.log_to_console(self._exeRestCmd("vnetwork","stop",params))
        
    def _exe_restops(self,ops,serviceStr,actions,params):
        '''

        :param ops:
        :param serviceStr:
        :param actions:
        :param params:
        :return:
        '''
        user = self.user
        password = self.password
        host = self.host
        securityToken = self.securityToken

        if self._check_driver():
            user=self.driver.capabilities['user'] if user==None else user
            password=self.driver.capabilities['password'] if password==None else password
            host=self.driver.capabilities['host'] if host==None else host
            securityToken=self.driver.capabilities['securityToken'] if securityToken==None else securityToken

        if (  None == securityToken or "" == securityToken):
            authStr="&user=" + user + "&password=" + password
        else:
            authStr="&securityToken=" + securityToken

        actionStr=""
        for key, value in actions.iteritems():
            actionStr=actionStr+"&"+key+"="+value

        paramStr=""
        for key, value in params.iteritems():
            paramStr=paramStr+"&param." + key +"="+quote_plus(value)

        url = "https://" \
            + host \
            + "/services/" \
            + serviceStr \
            + "?operation=" + ops \
            + authStr \
            + actionStr \
            + paramStr
        self.bi.log_to_console( 'url=' + url)

        return self._perform_rest_request(url)


