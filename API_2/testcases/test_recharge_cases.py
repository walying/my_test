# -*- coding: utf-8 -*-
# @Time     :2019/4/17  14:10
# @Author   :liying
# @Email    :1025452202@qq.com
# @File     :test_recharge_cases.py

import unittest
from ddt import ddt,data,unpack
from API_2.common.do_excel import *
from API_2.common import http_request
from API_2.common import context
from API_2.common import contants
from API_2.common import do_mysql
from API_2.common import logger
@ddt
class LoginTest(unittest.TestCase):
    logger=logger.get_logger(__name__)
    @classmethod
    def setUpClass(cls):
        logger.get_logger(__name__).info('准备测试前置')
        cls.http_test=http_request.HTTPRequest2()
        cls.mysql = do_mysql.DoMysql()

    #读取测试用例
    do_Myexcel = DoExcel(contants.case_file, 'recharge')
    cases = do_Myexcel.get_cases()

    @data(*cases)#装饰方法
    def test_recharge(self,case):
        self.logger.info('开始测试：{0}'.format(case.title))
        # 在请求之前替换参数化的值
        case.data = context.replace(case.data)
        print(case.data)
        #请求之前，判断是否需要执行SQL
        if case.sql is not None:
            sql=eval(case.sql)['sql1']
            member=self.mysql.fetch_one(sql)
            print(member['leaveamount'])
            before=member['leaveamount']

        resp=self.http_test.request(case.method,case.url,case.data)
        #print(resp.text)
        actual_code=resp.json()['code']
        try:
            self.assertEqual(str(case.expected),actual_code)
            #self.assertEqual(case.expected, resp.text)
            self.do_Myexcel.write_result(case.case_id+1,resp.text,'PASS')
            #成功之后，判断是否需要执行SQL   数据库校验，判断是否充值成功
            if case.sql is not None:
                sql = eval(case.sql)['sql1']
                member = self.mysql.fetch_one(sql)
                print(member['leaveamount'])
                after = member['leaveamount']
                recharge_amount=eval(case.data)['amount']#充值金额
                print(type(recharge_amount))
                self.assertEqual(before+recharge_amount,after)
        except AssertionError as e:
            self.do_Myexcel.write_result(case.case_id+1,resp.text,'FAIL')
            self.logger.error('报错了！{0}'.format(e))
            raise e
        self.logger.info('结束测试：{0}'.format(resp.text))

    @classmethod   #所有的用例执行完之后才会执行此类方法
    def tearDownClass(cls):
        cls.http_test.close()
        cls.mysql.close()
        logger.get_logger(__name__).info('准备测试后置')
        print("用例执行完毕")
