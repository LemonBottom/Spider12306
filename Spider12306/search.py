# Create time:2018/11/22 11:52 PM
# Author:Chen

import requests
import json
import MySQLdb
import random


class Search:

	def __init__(self, src, dst, date, session=None, header=None):
		"""
		:param src: 出发站
		:param dst: 终点站
		:param date: 日期
		"""
		self.src = src
		self.dst = dst
		self.date = date
		if not session:
			self.session = requests.session()
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
			del ua
		else:
			self.session = session
			self.header = header

	@staticmethod
	def mysql_execute(data, t):
		"""
		从mysql拿取站点代号数据
		:param data:
		:param t: 查询类型，1是通过name查nick，2是通过nick查name
		:return: 查询结果
		"""
		con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='123', db='12306db', charset='utf8')
		cur = con.cursor()
		# t=1 查询Nickname， t=2查询name
		if t == 1:
			cur.execute(f"select nick from station_name where name='{data}';")
		else:
			cur.execute(f"select name from station_name where nick='{data}';")
		r = cur.fetchone()[0]
		con.close()
		return r

	def crawl(self):
		"""
		爬取12306的余票信息
		:return: 余票信息
		"""
		try:
			src_nick = self.mysql_execute(self.src, 1)
			dst_nick = self.mysql_execute(self.dst, 1)
		except TypeError as Exception:
			# "城市不存在"
			raise Exception
		# session = requests.Session()
		ua = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1"
		r = self.session.get(
			f"https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={self.date}&leftTicketDTO.from_station={src_nick}&leftTicketDTO.to_station={dst_nick}&purpose_codes=ADULT",
			headers=self.header)
		r.encoding = r.apparent_encoding
		# print(r.cookies)
		result_dic = json.loads(r.text)
		para_lis = ['secretStr', '列车编号', '车次', '出发站', '到达站', '出发时间', '到站时间', '历经时间', '预定', '日期', '高级软卧', '软卧', '无座', '硬卧',
		            '硬座', '二等座', '一等座', '特等座', '动卧', 'unknown']
		data = []
		for i in result_dic['data']['result']:
			'''
			--r[0]secretStr，r[1]是否停运；--
			--r[4]始发站;r[5]终点站;--

			r[2]列车编号；r[3]车次;
			r[6]出发站;r[7]到达站;r[8]出发时间;r[9]到站时间;r[10]历经时间;r[11] Y 可预定，N 不可预定 IS_TIME_NOT_BUY 时间来不及;
			r[13]日期;
			r[21]高级软卧;r[23]软卧;r[26]无座;
			r[28]硬卧;r[29]硬座;r[30]二等座位;r[31]一等座位;r[32]特等座为;r[33]动卧;软座，其他：没有线索;
			'''
			r = i.split("|")
			# 打印r完整数据并显示数据的下标
			# print({'No.' + str(x): y for x, y in enumerate(r)})
			result = dict(zip(para_lis, ([r[0]] + r[2:4] + r[6:12] + [r[13], r[21], r[23], r[26]] + r[28:34] + [r[12]])))  # 剔除没有线索的信息并聚合需要的信息
			# 将站点代号更换为站点名字
			result['出发站代号'] = result['出发站']
			result['到达站代号'] = result['到达站']
			result['出发站'] = self.mysql_execute(result['出发站'], 2)
			result['到达站'] = self.mysql_execute(result['到达站'], 2)
			data.append(result)
		return data


if __name__ == "__main__":
	session = requests.session()
	header = {
		'Host': 'kyfw.12306.cn',
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0",
		'Accept': '*/*',
		'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
		'Accept-Encoding': 'gzip, deflate',
		'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E5%8C%97%E4%BA%AC,BJP&ts=%E4%B8%8A%E6%B5%B7,SHH&date=2018-11-27&flag=N,N,Y',
		'Connection': 'keep-alive',
		'origrn': "https://kyfw.12306.con"
	}
	for i in Search('北京', '广州', '2018-11-30', session, header).crawl():
		print(i)

'''
密码组成：
secretStr 好像每次都不一样
, start_time , train_no , from_station_telecode , to_station_telecode
RIqS2oA8vVhAngKNdKq558GE7oWg%2FFT5aqP6P96%2Fj0uz3OWCSUZP7WezvkSq43ZMS3kJUG6KN2LP%0AoEB6npy%2FT64XzQFY7Gve%2FCH%2Fww1TfwDNlRzB6eFe%2BWdZmkaayDls0wI1x4E8PeT8IJzlbYLwKy1N%0AQn1PV4jdtXaV3XA%2FyyfM%2BnLtG4bNadIP9FEx6i5KxViwybrMvjJasp1A33ZnqCaTOHgZajdkOZRX%0A0cqcBvxteBU1f%2FYtxtvI5AVoNBwERIsDxd%2FPb24%3D
05:14,330000K5980Z,BXP,GZQ
'''