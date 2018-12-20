# Create time:2018-11-24 00:19
# Author:Chen
import datetime
import multiprocessing
from json import JSONDecodeError
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .search import Search
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from .crawl import OrderTicket
from .SendSMS import SendSMS


# 主视图页面
def main_view(request):
	return render(request, "train12306.htm")


# 处理查询数据表单
def search_ajax(request):
	from_station = request.POST.get("from_station")
	to_station = request.POST.get("to_station")
	date = request.POST.get("date")
	try:
		data = Search(from_station, to_station, date).crawl()
	except TypeError:
		return JsonResponse({'code': 1})
	except JSONDecodeError:
		return JsonResponse({'code': 2})
	r = render(request, "tableRender.html", {'data': data})
	return JsonResponse({'code': 0, 'html': r.content.decode("utf-8"), 'quantity': len(data)})


# 接收短信
@csrf_exempt
def receive_SMS(request):
	request.POST.get("Body")
	resp = MessagingResponse()
	resp.message("回复内容")
	return HttpResponse(str(resp))


# 订票视图页面
def ticket_order_view(request):
	data = {
		"from_station": request.session.get("from_station"),
		"to_station": request.session.get("to_station"),
		"date": request.session.get("date"),
		"train_no": request.session.get("train_no")
	}
	return render(request, "orderTicket.html", data)


# 预定按钮处理
def ticket_order_ajax(request):
	request.session.update({
		"date": request.POST.get("date"),
		"from_station": request.POST.get("from_station"),
		"to_station": request.POST.get("to_station"),
		"train_no": request.POST.get("train_no")
	})
	response = JsonResponse({"status_code": '0'})
	return response


# 订票
def order_action_ajax(request):
	date = datetime.datetime.strptime(request.session.get('date'), "%Y%m%d").strftime("%Y-%m-%d")
	order = OrderTicket(
		request.session.get("from_station"),
		request.session.get("to_station"),
		date,
		request.session.get("train_no"),
		request.POST.get("seat_type"),
		request.POST.get("passenger_name"),
		request.POST.get("username"),
		request.POST.get("password"),
		request.POST.get("inform_phone")
	)
	# 登录
	login = order.login_in()
	if not login:
		return JsonResponse({"status": "error", "message": "登录失败，请检查用户名或者密码"})
	# 查询
	secret_str = order.search()
	if secret_str == 2:
		return JsonResponse({"status": "error", "message": "没有相关车次"})
	elif secret_str == 1:
		return JsonResponse({"status": "error", "message": "没有座位了，请检查该列车是否有该座位类型，或者选择抢票"})
	# 订票
	order_info = order.order_ticket(secret_str)
	if "error" in order_info:
		return JsonResponse({"status": "error", "message": order_info['error']})
	SendSMS(
		request.POST.get("inform_phone"),
		(
			f"订票成功!订单号码:{order_info['sequence_no']},出发日期:{order_info['train_date']},车厢号:{order_info['coach_no']}," +
			f"座位号: {order_info['seat_no']},座位类别:{order_info['seat_type_name']},车票类别:{order_info['ticket_type_name']}" +
			f'订票时间:{order_info["reserve_time"]},最迟付款:{order_info["pay_limit_time"]},票价:{order_info["str_ticket_price_page"]}'
		)
	)
	return JsonResponse({
		"status": 1,
		'订单号码': order_info['sequence_no'],
		'出发日期': order_info['train_date'],
		'车厢号': order_info["coach_no"],
		'座位号': order_info['seat_no'],
		'座位类别': order_info["seat_type_name"],
		'车票类别': order_info["ticket_type_name"],
		'订票时间': order_info["reserve_time"],
		'最迟付款': order_info["pay_limit_time"],
		'票价': order_info["str_ticket_price_page"]})


# 抢票
def scramble_ticket_ajax(request):
	date = datetime.datetime.strptime(request.session.get('date'), "%Y%m%d").strftime("%Y-%m-%d")
	order = OrderTicket(
		request.session.get("from_station"),
		request.session.get("to_station"),
		date,
		request.session.get("train_no"),
		request.POST.get("seat_type"),
		request.POST.get("passenger_name"),
		request.POST.get("username"),
		request.POST.get("password"),
		request.POST.get("inform_phone")
	)
	# 登录
	login = order.login_in()
	if not login:
		return JsonResponse({"message": "登录失败，请检查用户名或者密码"})
	multiprocessing.Process(target=order.scramble_ticket).start()
	return JsonResponse({"message": "正在抢票，请等待短信通知"})
