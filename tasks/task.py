# Create time:2018-12-30 22:33
# Author:Chen

import logging
import redis
from celery import task
from tasks.spider import Spider

# 初始化12306爬虫
spider = Spider()
logging.debug("爬虫初始化成功")
# 用于连接代理池
redis_server = redis.Redis('127.0.0.1', 6379)
# 代理池的key
REDIS_KEY = "https_proxies"


@task
def search(src, dst, date):
	"""
	查询
	:param src: 起始站
	:param dst: 到达站
	:param date: 日期
	:return:
	"""
	try:
		return spider.search(src, dst, date)
	except Exception as E:
		return E.args[0]


@task
def order(username, password, train_code, src, dst, date, seat_type, passenger_name):
	"""
	订票
	:param username: 12306账户名称
	:param password: 12306账户密码
	:param train_code: 车次
	:param src: 出发站
	:param dst: 到达站
	:param date: 日期
	:param seat_type: 座位类型
	:param passenger_name: 乘客名字
	:return: 车票的信息
	"""
	if not spider.if_login:
		spider.login_in(username, password)
	try:
		return spider.order_ticket(train_code, src, dst, date, seat_type, passenger_name)
	except Exception as E:
		return E.args[0]


@task
def scramble(username, password, train_code, src, dst, date, seat_type, passenger_name):
	"""
	抢票
	:param username:
	:param password:
	:param args:
	:return:
	"""
	while True:
		proxy = redis_server.srandmember(REDIS_KEY, 1)[0].decode("utf-8")
		data = search(src, dst, date, proxy=proxy)
		for i in data:
			if train_code == i['车次'] and i[seat_type] != '无':
				order(username, password, train_code, src, dst, date, seat_type, passenger_name)






