# -*- coding=utf-8 -*-
# Create ime:2018/10/22 1:18 AM
# Author:Chen


import requests
import re
import random
import base64
import time
import json
import datetime
from tasks.yun_da_ma import YDMHttp
from urllib.parse import unquote
from tasks.send_SMS import SendSMS


class OrderTicket:

	def __init__(self, from_station, to_station, date, train_code, seat_type, passenger_name, username, password, inform_phone):
		ua = [
			"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1",
			"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
			"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
			'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
			'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
			'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.0 Safari/534.13',
			'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.3 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/533.3',
			'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.8 (KHTML, like Gecko) Chrome/7.0.521.0 Safari/534.8',
			'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.1 Safari/534.3',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
			'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
			'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8',
			'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7ad-imcjapan-syosyaman-xkgi3lqg03!wgz']
		# request 头部
		self.header = {
			'Host': 'kyfw.12306.cn',
			'User-Agent': random.choice(ua),
			'Accept': '*/*',
			'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'keep-alive',
			'origrn': "https://kyfw.12306.con"}
		self.session = requests.Session()
		self.from_station = from_station
		self.to_station = to_station
		self.date = date
		self.train_code = train_code  # 车次
		self.seat_type = seat_type  # 座位类型
		self.passenger_name = passenger_name  # 乘车人姓名
		self.username = username
		self.password = password
		self.inform_phone = inform_phone

	# 处理验证码
	def yundama(self):
		# 处理验证码
		# 打码平台账户
		username = 'swningmeng'
		password = 'wc1255679669'
		appid = 1
		appkey = '22cc5376925e9387a23cf797cb9ba745'
		filename = 'image.png'
		codetype = 6701
		timeout = 60
		yundama = YDMHttp(username, password, appid, appkey)
		yundama.login()
		# 查询余额
		balance = yundama.balance()
		print(f'balance: {balance}')
		cid, result = yundama.decode(filename, codetype, timeout)
		print(f'cid: {cid}, result: {result}')
		lis = list(result)
		print(lis)
		# 手动处理验证码
		# lis = input("请输入验证码: ")
		return lis

	def captch(self):
		# 获取验证码图片，存入IO
		captch_url = f"https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&{str(time.time()).replace('.', '')[:13]}&callback=jQuery19102009320088771318_1542820554090&_={str(time.time()).replace('.', '')[:13]}"
		captch_js = self.session.get(captch_url, headers=self.header)
		captch_js.encoding = captch_js.apparent_encoding
		image_str = re.findall(re.compile('"image":"(\S+)"'), captch_js.text)[0]
		image = base64.b64decode(image_str)
		with open('image.png', 'wb') as f:
			f.write(image)
		# 验证码序列对应的坐标
		l1 = {'1': '43%2C43', '2': '117%2C51', '3': '177%2C48', '4': '255%2C48', '5': '39%2C115', '6': '110%2C115','7': '180%2C116', '8': '262%2C118'}
		answer = ''
		# 打码平台
		for i in self.yundama():
			answer = answer + l1[i] + '%2C'
		answer = answer[:-3]  # 坐标相应的答案
		# 进行验证
		captch_url = f"https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery19102948558244753501_1543233163035\
			&answer={answer}&rand=sjrand&login_site=E&_={str(int(time.time()))}"
		captch = self.session.get(captch_url, headers=self.header)
		captch.encoding = captch.apparent_encoding
		print("验证码验证结果：", captch.text)
		return captch.text, answer

	# 登录操作
	def login_in(self):
		# get登录页面，获取cookie，初始化会话
		login_url = "https://kyfw.12306.cn/otn/resources/login.html"
		self.session.get(login_url, headers=self.header)
		# 不断验证验证码，直到验证正确
		while True:
			try:
				captch_result, answer = self.captch()
			except (IndexError, KeyError):
				continue
			if "失败" not in captch_result:
				break
		# 登录请求
		login_url = "https://kyfw.12306.cn/passport/web/login"
		login_data = {"username": self.username, "password": self.password, "appid": "otn", "answer": answer}
		login = self.session.post(login_url, data=login_data, headers=self.header)
		login.encoding = login.apparent_encoding
		print("登录申请结果: ", login.text)
		if '错误' in login.text:
			return
		# uamtk请求
		uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk?callback=jQuery19108844914567503552_1543306282686'
		uamtk_data = {"appid": "otn", "_json_att": ""}
		uamtk = self.session.post(uamtk_url, data=uamtk_data, headers=self.header)
		uamtk.encoding = uamtk.apparent_encoding
		print("uamtk结果: ", uamtk.text)
		tk = re.findall(re.compile('"newapptk":"(.+)"'), uamtk.text)[0]
		# uamauthclient请求
		uamauthclient_url = "https://kyfw.12306.cn/otn/uamauthclient"
		uamauthclient_data = {"tk": tk}
		uamauthclient = self.session.post(uamauthclient_url, data=uamauthclient_data, headers=self.header)
		uamauthclient.encoding = uamauthclient.apparent_encoding
		print("uamauthclient结果: ", uamauthclient.text)
		# checkuser请求
		check_user_url = "https://kyfw.12306.cn/otn/login/checkUser?_json_att"
		check_user_response = self.session.post(check_user_url, headers=self.header, )
		print("checkUser: ", check_user_response.text)
		return 1

	# 查询当日的车次
	def search(self):
		# 搜索
		data = Search(self.from_station, self.to_station, self.date, self.session, self.header).crawl()
		for i in data:
			if self.train_code == i['车次']:
				print(i)
				if i[self.seat_type] in ('', '无'):
					print("抱歉，已经没有座位了")
					return 1
				else:
					return i['secretStr']
		print("当日没有相应的车次")
		return 2

	def order_ticket(self, secret_str):
		if secret_str is not None:
			secret_str = unquote(secret_str)
		else:
			return {"error": "无车次相关信息"}
		# submitOrderRequest
		submit_order_request_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
		submit_order_request_data = {
			"secretStr": secret_str,
			"train_date": self.date,
			"back_train_date": datetime.datetime.today().strftime("%Y-%m-%d"),
			"tour_flag": "dc",
			"purpose_codes": "ADULT",
			"query_from_station_name": self.from_station,
			"query_to_station_name": self.to_station,
			"undefined": ""}
		submit = self.session.post(submit_order_request_url, data=submit_order_request_data, headers=self.header)
		print("submit_order_request结果: ", submit.text)
		# init
		init_dc_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc?_json_att"
		init_dc = self.session.post(init_dc_url, headers=self.header)
		# print("init_dc结果: ", init_dc.text)
		global_repeat_submit_token = re.findall(re.compile("globalRepeatSubmitToken\ =\ \'(.+)\'\;"), init_dc.text)[0]
		# 车票信息
		ticket_info = re.findall(re.compile("ticketInfoForPassengerForm=({.+});"), init_dc.text)[0]
		ticket_info_dic = json.loads(ticket_info.replace("'", '"'))
		seat_type_code = ''
		for i in ticket_info_dic['limitBuySeatTicketDTO']['seat_type_codes']:
			if self.seat_type == i['value']:
				seat_type_code = i['id']
				break
		if not seat_type_code:
			return {"error": "无相关座位信息，或者有座位时不能选择无座"}
		# getPasserngerDTOs
		passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
		passenger = self.session.post(passenger_url, data={'_json_att': '', 'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}, headers=self.header)
		passenger.encoding = passenger.apparent_encoding
		print("passenger结果: ", passenger.text)
		passenger_dic = json.loads(passenger.text)
		passenger_detail = ''
		for i in passenger_dic["data"]["normal_passengers"]:
			if i["passenger_name"] == self.passenger_name:
				passenger_detail = i  # 乘客的相关信息
				break
		if not passenger_detail:
			return {"error": "无相关乘客信息"}
		passenger_ticket_str = f'{seat_type_code},0,1,{passenger_detail["passenger_name"]},{passenger_detail["passenger_id_type_code"]},{passenger_detail["passenger_id_no"]},{passenger_detail["mobile_no"]},N'
		old_passenger_str = f'{passenger_detail["passenger_name"]},{passenger_detail["passenger_id_type_code"]},{passenger_detail["passenger_id_no"]},1_'
		# checkOrderInfo
		check_order_data = {
			'cancel_flag': 2,
			'bed_level_order_num': '000000000000000000000000000000',
			'passengerTicketStr': passenger_ticket_str,
			'oldPassengerStr': old_passenger_str,
			'tour_flag': 'dc',
			'randCode': '',
			'whatsSelect': '1',
			'_json_att': '',
			'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
		check_order_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
		check_order = self.session.post(check_order_url, data=check_order_data, headers=self.header)
		print("checkOrder结果: ", check_order.text)
		# getQueueCount
		get_queue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
		get_queue_data = {
			'train_date': datetime.datetime.strptime(self.date, '%Y-%m-%d').strftime("%a %b %d %Y") + " 00:00:00 GMT+0800 (中国标准时间)",
			'train_no': ticket_info_dic['queryLeftNewDetailDTO']['train_no'],
			'stationTrainCode': ticket_info_dic['queryLeftNewDetailDTO']['station_train_code'],
			'seatType': seat_type_code,
			'fromStationTelecode': ticket_info_dic['orderRequestDTO']['from_station_telecode'],
			'toStationTelcode': ticket_info_dic['orderRequestDTO']['to_station_telecode'],
			'leftTicket': ticket_info_dic['leftTicketStr'],
			'purpose_codes': ticket_info_dic['purpose_codes'],
			'train_location': ticket_info_dic['train_location'],
			'_json_att': '',
			'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
		get_queue = self.session.post(get_queue_url, data=get_queue_data, headers=self.header)
		print("get_queue结果: ", get_queue.text)
		# confirm_single
		confirm_single_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
		confirm_single_data = {
			'passengerTicketStr': passenger_ticket_str,
			'oldPassengerStr': old_passenger_str,
			'randCode': '',
			'purpose_codes': ticket_info_dic['purpose_codes'],
			'key_check_isChange': ticket_info_dic['key_check_isChange'],
			'leftTicketStr': ticket_info_dic['leftTicketStr'],
			'train_location': ticket_info_dic['train_location'],
			'choose_seats': '',
			'seatDetailType': '000',
			'whatsSelect': '1',
			'roomType': '00',
			'dwAll': 'N',
			'_json_att': '',
			'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
		confirm_single = self.session.post(confirm_single_url, data=confirm_single_data, headers=self.header)
		print("confirm_single结果: ", confirm_single.text)
		# waitTime 轮询，直到出现orderId为止
		while True:
			wait_time_url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
			wait_time_data = {
				'random': str(time.time()).replace(".", "")[:13],
				'tourFlag': 'dc',
				'_json_att': '',
				'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
			wait_time = self.session.post(wait_time_url, data=wait_time_data, headers=self.header)
			print("wait_time: ", wait_time.text)
			try:
				order_id = re.findall(re.compile(r'"orderId":"(.+)"},'), wait_time.text)[0]
				break
			except IndexError:
				time.sleep(0.5)
				continue
		print("订单号：", order_id)
		#  DcQueue
		dc_queue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
		dc_queue_data = {
			'orderSequence_no': order_id,
			'_json_att': '',
			'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
		dc_queue = self.session.post(dc_queue_url, data=dc_queue_data, headers=self.header)
		print("DcQueue结果：", dc_queue.text)
		complete_url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete?_json_att'
		complete = self.session.post(complete_url, headers=self.header)
		print(complete.text)
		order_info = json.loads(complete.text)['data']['orderDBList'][0]['tickets'][0]
		print("order_info结果: ", order_info)
		return order_info

	# 抢票
	def scramble_ticket(self):
		SendSMS(self.inform_phone, '正在抢票，抢到票后会短信通知')
		while True:
			secret_str = self.search()
			if secret_str == 1:
				time.sleep(30)
				SendSMS(self.inform_phone, '正在抢票')
			else:
				self.order_ticket(secret_str)
				break
		return



if __name__ == "__main__":
	OrderTicket("沈阳", "鞍山", "2018-11-30", "2052", "硬卧", "袁家宝", "HQDXYJB", "199239yjb").order_ticket()
