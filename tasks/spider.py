# Create time:2018/11/22 11:52 PM
# Author:Chen

import MySQLdb
import requests
import re
import random
import base64
import time
import json
import datetime
from urllib.parse import unquote
from tasks.yun_da_ma import YDMHttp
from tasks.send_SMS import SendSMS


class Spider:

    def __init__(self):
        # mysql数据库，用于查询车站代号
        self._mysql_server = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123', db='12306db',
                                            charset='utf8').cursor()
        self._session = requests.session()
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
        self._header = {'Host': 'kyfw.12306.cn', 'User-Agent': random.choice(ua)}
        # 用于判断是否登录了
        self.if_login = False

    def get_station_info(self, data, data_type):
        """
        通过站名获取车站的代号，或者通过代号获取站名，如北京：BJP，
        :param data:
        :param data_type: 字符串类型，name是获取站名，code是获取代号
        :return: 查询结果
        """
        assert data_type in ("name", "code"), "data_type must be 'name' or 'code'"
        if data_type == 'code':
            self._mysql_server.execute(f"select nick from station_name where name='{data}';")
        else:
            self._mysql_server.execute(f"select name from station_name where nick='{data}';")
        return self._mysql_server.fetchone()[0]

    def search(self, src, dst, date, proxy=None):
        """
        查询余票信息, 可以不登录
        返回的json用竖线分割数据，对json相应位置的数据解析：
        --r[0]secretStr，r[1]是否停运；--
        --r[4]始发站;r[5]终点站;--
        r[2]列车编号；r[3]车次;
        r[6]出发站;r[7]到达站;r[8]出发时间;r[9]到站时间;r[10]历经时间;r[11] Y 可预定，N 不可预定 IS_TIME_NOT_BUY 时间来不及;
        r[13]日期;
        r[21]高级软卧;r[23]软卧;r[26]无座;
        r[28]硬卧;r[29]硬座;r[30]二等座位;r[31]一等座位;r[32]特等座为;r[33]动卧;软座，其他：没有线索;
        :return: 余票信息
        """
        try:
            # 获取车站的代号
            src_code, dst_code = self.get_station_info(src, 'code'), self.get_station_info(dst, 'code')
        except TypeError:
            raise Exception("城市不存在")
        if src_code == dst_code:
            raise Exception("起始站与到达站不能一样")
        # 12月份url多了一个"Z"
        url = f"https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={date}&leftTicket" + \
              f"DTO.from_station={src_code}&leftTicketDTO.to_station={dst_code}&purpose_codes=ADULT"
        # 添加代理
        if proxy:
            proxy = {"https": "https://" + proxy}
            # 不使用登录状态，以免被封号
            self._session = requests.session()
            if self.if_login:
                self.if_login = False
        try:
            r_json = self._session.get(url, proxies=proxy, headers=self._header)
            r_json.raise_for_status()
        except Exception as E:
            raise Exception("检查日期是否有误，可预定30天内的车票")
        result_dic = json.loads(r_json.text)
        assert result_dic, "查询余票返回空数据"
        # 结果result的key们
        key_lis = ['secretStr', '列车编号', '车次', '出发站代号', '到达站代号', '出发时间', '到站时间', '历经时间',
                    '预定', '日期', '高级软卧', '软卧', '无座', '硬卧', '硬座', '二等座', '一等座', '特等座', '动卧']
        data = []
        for i in result_dic['data']['result']:
            # 数据列表 r
            r = i.split("|")
            # 打印r完整数据并显示数据的下标
            # print({'No.' + str(x): y for x, y in enumerate(r)})
            # 生成结果字典
            result = dict(zip(
                key_lis,
                ([r[0]] + r[2:4] + r[6:12] + [r[13], r[21], r[23], r[26]] + r[28:34])
            ))
            # 将站点代号更换为站点名字
            result['出发站'], result['到达站'] = src, dst
            data.append(result)
        return data

    # 处理验证码
    @staticmethod
    def _yundama():
        """
        调用云打码api
        :return:
        """
        # 打码平台账户
        username = 'swningmeng'
        password = 'wc1255679669'
        appid = 1
        appkey = '22cc5376925e9387a23cf797cb9ba745'
        filename = 'image.png'
        # 打码类型
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

    def captcha(self):
        """
        下载验证码，返回答案
        :return:
        """
        # 获取验证码图片，存入IO
        captch_url = "https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sj" + \
                     f"rand&{str(time.time()).replace('.', '')[:13]}&callback=jQuery19102009320088771318_15428" + \
                     f"20554090&_={str(time.time()).replace('.', '')[:13]}"
        captch_js = self._session.get(captch_url, headers=self._header)
        captch_js.encoding = captch_js.apparent_encoding
        image_str = re.findall(re.compile('"image":"(\S+)"'), captch_js.text)[0]
        image = base64.b64decode(image_str)
        with open('image.png', 'wb') as f:
            f.write(image)
        # 验证码序列对应的坐标
        l1 = {'1': '43%2C43', '2': '117%2C51', '3': '177%2C48', '4': '255%2C48',
              '5': '39%2C115', '6': '110%2C115','7': '180%2C116', '8': '262%2C118'}
        answer = ''
        # 打码平台
        for i in self._yundama():
            answer = answer + l1[i] + '%2C'
        answer = answer[:-3]  # 坐标相应的答案
        # 进行验证
        captch_url = f"https://kyfw.12306.cn/passport/captcha/captcha-check?callback=jQuery19102948558244753501_" + \
                     f"1543233163035&answer={answer}&rand=sjrand&login_site=E&_={str(int(time.time()))}"
        captch = self._session.get(captch_url, headers=self._header)
        captch.encoding = captch.apparent_encoding
        print("验证码验证结果：", captch.text)
        return captch.text, answer

    # 登录操作
    def login_in(self, username, password):
        """
        完成登录流程
        :param username:
        :param password:
        :return:
        """
        # get登录页面，获取cookie，初始化会话
        login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        self._session.get(login_url, headers=self._header)
        # 不断验证验证码，直到验证正确
        while True:
            try:
                captcha_result, answer = self.captcha()
            except (IndexError, KeyError):
                continue
            if "失败" not in captcha_result:
                break
        # 登录请求
        login_url = "https://kyfw.12306.cn/passport/web/login"
        login_data = {"username": username, "password": password, "appid": "otn", "answer": answer}
        login = self._session.post(login_url, data=login_data, headers=self._header)
        login.encoding = login.apparent_encoding
        print("登录申请结果: " + login.text)
        if '错误' in login.text:
            raise Exception("登录出现问题，请联系开发人员")
        # uamtk请求
        uamtk_url = 'https://kyfw.12306.cn/passport/web/auth/uamtk?callback=jQuery19108844914567503552_1543306282686'
        uamtk_data = {"appid": "otn", "_json_att": ""}
        uamtk = self._session.post(uamtk_url, data=uamtk_data, headers=self._header)
        uamtk.encoding = uamtk.apparent_encoding
        print("uamtk结果: " + uamtk.text)
        tk = re.findall(re.compile('"newapptk":"(.+)"'), uamtk.text)[0]
        # uamauthclient请求
        uamauthclient_url = "https://kyfw.12306.cn/otn/uamauthclient"
        uamauthclient_data = {"tk": tk}
        uamauthclient = self._session.post(uamauthclient_url, data=uamauthclient_data, headers=self._header)
        uamauthclient.encoding = uamauthclient.apparent_encoding
        print("uamauthclient结果: " + uamauthclient.text)
        # checkuser请求
        check_user_url = "https://kyfw.12306.cn/otn/login/checkUser?_json_att"
        check_user_response = self._session.post(check_user_url, headers=self._header, )
        print("checkUser: " + check_user_response.text)
        # 标记登录
        self.if_login = True
        return True

    def _get_secret_str(self, train_code, src, dst, date):
        data = self.search(src, dst, date)
        for i in data:
            if i['车次'] == train_code:
                return i['secretStr']
        raise Exception("找不到相关车次")

    def order_ticket(self, train_code, from_station, to_station, date, seat_type, passenger_name):
        """
        完成定票流程
        :param secret_str:
        :param from_station:
        :param to_station:
        :param date:
        :param seat_type:
        :param passenger_name:
        :return:
        """
        secret_str = self._get_secret_str(train_code, from_station, to_station, date)
        # submitOrderRequest
        submit_order_request_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        submit_order_request_data = {
            "secretStr": unquote(secret_str),
            "train_date": date,
            "back_train_date": datetime.datetime.today().strftime("%Y-%m-%d"),
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": from_station,
            "query_to_station_name": to_station,
            "undefined": ""}
        print(submit_order_request_data)
        submit = self._session.post(submit_order_request_url, data=submit_order_request_data, headers=self._header)
        print("submit_order_request结果: " + submit.text)
        # init
        init_dc_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc?_json_att"
        init_dc = self._session.post(init_dc_url, headers=self._header)
        # print("init_dc结果: ", init_dc.text)
        global_repeat_submit_token = re.findall(re.compile("globalRepeatSubmitToken\ =\ \'(.+)\'\;"), init_dc.text)[0]
        # 车票信息
        ticket_info = re.findall(re.compile("ticketInfoForPassengerForm=({.+});"), init_dc.text)[0]
        ticket_info_dic = json.loads(ticket_info.replace("'", '"'))
        seat_type_code = ''
        for i in ticket_info_dic['limitBuySeatTicketDTO']['seat_type_codes']:
            if seat_type == i['value']:
                seat_type_code = i['id']
                break
        if not seat_type_code:
            raise Exception("无相关座位信息，或者有座位时不能选择无座")
        # getPasserngerDTOs
        passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        passenger = self._session.post(
            passenger_url,
            data={'_json_att': '', 'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token},
            headers=self._header)
        passenger.encoding = passenger.apparent_encoding
        print("passenger结果: " + passenger.text)
        passenger_dic = json.loads(passenger.text)
        passenger_detail = ''
        for i in passenger_dic["data"]["normal_passengers"]:
            if i["passenger_name"] == passenger_name:
                passenger_detail = i  # 乘客的相关信息
                break
        if not passenger_detail:
            raise Exception("无相关乘客信息")
        passenger_ticket_str = f'{seat_type_code},0,1,{passenger_detail["passenger_name"]},' + \
                               f'{passenger_detail["passenger_id_type_code"]},{passenger_detail["passenger_id_no"]},' +\
                               f'{passenger_detail["mobile_no"]},N'
        old_passenger_str = f'{passenger_detail["passenger_name"]},{passenger_detail["passenger_id_type_code"]},' + \
                            f'{passenger_detail["passenger_id_no"]},1_'
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
        check_order = self._session.post(check_order_url, data=check_order_data, headers=self._header)
        print("checkOrder结果: " + check_order.text)
        # getQueueCount
        get_queue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        get_queue_data = {
            'train_date': datetime.datetime.strptime(date, '%Y-%m-%d').strftime("%a %b %d %Y") +
                          " 00:00:00 GMT+0800 (中国标准时间)",
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
        get_queue = self._session.post(get_queue_url, data=get_queue_data, headers=self._header)
        print("get_queue结果: " + get_queue.text)
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
        confirm_single = self._session.post(confirm_single_url, data=confirm_single_data, headers=self._header)
        print("confirm_single结果: " + confirm_single.text)
        # waitTime 轮询，直到出现orderId为止
        while True:
            wait_time_url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
            wait_time_data = {
                'random': str(time.time()).replace(".", "")[:13],
                'tourFlag': 'dc',
                '_json_att': '',
                'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
            wait_time = self._session.post(wait_time_url, data=wait_time_data, headers=self._header)
            print("wait_time: " + wait_time.text)
            try:
                order_id = re.findall(re.compile(r'"orderId":"(.+)"},'), wait_time.text)[0]
                break
            except IndexError:
                time.sleep(0.5)
                continue
        print("订单号：" + order_id)
        #  DcQueue
        dc_queue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        dc_queue_data = {
            'orderSequence_no': order_id,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': global_repeat_submit_token}
        dc_queue = self._session.post(dc_queue_url, data=dc_queue_data, headers=self._header)
        print("DcQueue结果：" + dc_queue.text)
        # 完成订单，获取订单信息
        while True:
            complete_url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete?_json_att'
            complete = self._session.get(complete_url, headers=self._header)
            print(complete.text)
            try:
                order_info = json.loads(complete.text)['data']['orderDBList'][0]['tickets'][0]
                print("order_info结果: " + str(order_info))
                return order_info
            except KeyError:
                time.sleep(1)

    def info(self):
        complete_url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete?_json_att'
        complete = self._session.post(complete_url, headers=self._header)
        print(complete.text)
        order_info = json.loads(complete.text)['data']['orderDBList'][0]['tickets'][0]
        print("order_info结果: " + str(order_info))
        return order_info


if __name__ == "__main__":
    d = Spider()
    d.login_in("17610272393", "bunengshuodemi53")
    while True:
        data = d.search("北京", "鞍山", "2019-02-01")
        if isinstance(data, list):
            for i in data:
                print(i)
                if "2549" == i['车次'] and i['硬卧'] != '无':
                    result1 = d.order_ticket("2549", "北京", "鞍山", "2019-02-01", "硬卧", "王晨")
                    SendSMS("17610272393", "订票成功！" + str(result1))
                    result2 = d.order_ticket("2549", "北京", "鞍山", "2019-02-01", "硬卧", "袁家宝")
                    SendSMS("17610272393", "订票成功！" + str(result2))
        print('无票')

