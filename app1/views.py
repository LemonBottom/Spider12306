# Create your views here.

# Create time:2018-11-24 00:19
# Author:Chen
from django.shortcuts import render
from django.http import JsonResponse
from tasks.task import search, order, scramble
import datetime
import multiprocessing


def main_view(request):
	"""首页"""
	return render(request, "train12306.htm")


def search_ajax(request):
	"""查询余票"""
	# 获取用户输入的起始站，到达站与日期
	gen = (request.POST.get(key) for key in ("from_station", "to_station", "date"))
	# 获取搜索结果
	data = search(*gen)
	# 若发生异常返回异常内容
	if isinstance(data, str):
		return JsonResponse({'status': False, 'html': data})
	# 渲染后的html
	html = render(request, "tableRender.html", {'data': data})
	# quantity用于渲染有多少车次
	return JsonResponse({'status': True, 'html': html.content.decode("utf-8"), 'quantity': len(data)})


# 预定按钮处理
def ticket_order_ajax(request):
	"""
	更新session，等待js发起渲染请求
	:param request: 
	:return: 
	"""
	request.session.update({
		"date": request.POST.get("date"),
		"from_station": request.POST.get("from_station"),
		"to_station": request.POST.get("to_station"),
		"train_no": request.POST.get("train_no")
	})
	return JsonResponse({"status_code": '0'}) 


# 订票视图页面
def ticket_order_view(request):
	"""
	返回渲染html
	:param request: 
	:return: 
	"""
	data = {
		"from_station": request.session.get("from_station"),
		"to_station": request.session.get("to_station"),
		"date": request.session.get("date"),
		"train_no": request.session.get("train_no")
	}
	return render(request, "orderTicket.html", data)


# 订票
def order_action_ajax(request):
	# args = [ username, password, train_code, src, dst, date, seat_type, passenger_name ]
	order_result = order(
		request.POST.get("username"),
		request.POST.get("password"),
		request.session.get("train_no"),
		request.session.get("from_station"),
		request.session.get("to_station"),
		datetime.datetime.strptime(request.session.get('date'), "%Y%m%d").strftime("%Y-%m-%d"),
		request.POST.get("seat_type"),
		request.POST.get("passenger_name"),
		request.POST.get("inform_phone")
	)
	if isinstance(order_result, str):
		return JsonResponse({"status": "error", "msg": order_result})
	order_result['status'] = 1
	return JsonResponse(order_result)


# 抢票
def scramble_ticket_ajax(request):
	multiprocessing.Process(target=scramble, args=(
		request.POST.get("username"),
		request.POST.get("password"),
		request.session.get("train_no"),
		request.session.get("from_station"),
		request.session.get("to_station"),
		datetime.datetime.strptime(request.session.get('date'), "%Y%m%d").strftime("%Y-%m-%d"),
		request.POST.get("seat_type"),
		request.POST.get("passenger_name"),
		request.POST.get("inform_phone")
	)).start()
	return JsonResponse({"msg": "已经开始抢票，请等待短信通知"})
