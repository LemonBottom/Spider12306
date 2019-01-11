# Create time:2018-12-30 22:33
# Author:Chen

import time
import redis
from celery import task
from tasks.spider import Spider
from tasks.send_SMS import SendSMS

# 用于连接代理池
redis_server = redis.Redis('127.0.0.1', 6379)
# 代理池的key
REDIS_KEY = "https_proxies"


@task
def search(src, dst, date, proxy=None):
	"""
	查询
	:param src: 起始站
	:param dst: 到达站
	:param date: 日期
	:param proxy: 使用代理
	:return:
	"""
	spider = Spider()
	try:
		return spider.search(src, dst, date, proxy)
	except Exception as E:
		print(E)
		return E.args[0]


@task
def order(username, password, train_code, src, dst, date, seat_type, passenger_name, inform_phone):
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
	:param inform_phone: 接收短信通知的手机号
	:return: 车票的信息字典
	"""
	spider = Spider()
	if not spider.if_login:
		spider.login_in(username, password)
	try:
		# 完成订票任务
		result = spider.order_ticket(train_code, src, dst, date, seat_type, passenger_name)
	except Exception as E:
		return E.args[0]
	result = {
		'订单号码': result['sequence_no'],
		'出发日期': result['train_date'],
		'车厢号': result["coach_no"],
		'座位号': result['seat_no'],
		'座位类别': result["seat_type_name"],
		'车票类别': result["ticket_type_name"],
		'订票时间': result["reserve_time"],
		'最迟付款': result["pay_limit_time"],
		'票价': result["str_ticket_price_page"]
	}
	# 发送短信通知订票信息
	SendSMS(inform_phone, "订票成功！" + str(result))
	return result



@task
def scramble(username, password, train_code, src, dst, date, seat_type, passenger_name, inform_phone):
	"""
	抢票
	:param username: 12306账户名称
	:param password: 12306账户密码
	:param train_code: 车次
	:param src: 出发站
	:param dst: 到达站
	:param date: 日期
	:param seat_type: 座位类型
	:param passenger_name: 乘客名字
	:param inform_phone: 接收短信通知的手机号
	:return: 车票的信息
	"""
	d = Spider()
	d.login_in(username, password)
	while True:
		try:
			data = d.search(src, dst, date)
			if isinstance(data, list):
				for i in data:
					print(i['车次'], i['硬卧'], i['secretStr'])
					if train_code == i['车次'] and i[seat_type] != '无':
						result1 = d.order_ticket(i['secretStr'], src, dst, date, seat_type, passenger_name)
						SendSMS(inform_phone, "订票成功！" + str(result1))
						break
			print('无票')
		except Exception as E:
			print(E)
			print("网络异常")
		time.sleep(0.5)
	# while True:
	# 	data = search(src, dst, date, proxy=proxy)
	# 	if isinstance(data, list):
	# 		for i in data:
	# 			print(i)
	# 			if train_code == i['车次'] and i['secretStr']:
	# 				order(username, password, train_code, src, dst, date, seat_type, passenger_name, inform_phone)
	# 	print('无票')
	# 	time.sleep(0.5)







