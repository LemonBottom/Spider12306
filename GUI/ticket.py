# Create time:2019-01-21 01:46
# Author:Chen

import tkinter
from GUI.spider import Spider
from GUI.send_SMS import SendSMS


class App(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # 用户名
        tkinter.Label(self, text="用户名").grid(row=0, column=0)
        self.username = tkinter.Entry(self)
        self.username.grid(row=0, column=1)
        # 密码
        tkinter.Label(self, text="密码").grid(row=1, column=0)
        self.password = tkinter.Entry(self)
        self.password.grid(row=1, column=1)
        # 车次
        tkinter.Label(self, text="车次").grid(row=2, column=0)
        self.train_code = tkinter.Entry(self)
        self.train_code .grid(row=2, column=1)
        # 出发站
        tkinter.Label(self, text="出发站").grid(row=3, column=0)
        self.src = tkinter.Entry(self)
        self.src.grid(row=3, column=1)
        # 到达站
        tkinter.Label(self, text="到达站").grid(row=4, column=0)
        self.dst = tkinter.Entry(self)
        self.dst.grid(row=4, column=1)
        # 日期
        tkinter.Label(self, text="日期").grid(row=5, column=0)
        self.date = tkinter.Entry(self)
        self.date.grid(row=5, column=1)
        # 乘车人
        tkinter.Label(self, text="乘车人").grid(row=6, column=0)
        self.passenger = tkinter.Entry(self)
        self.passenger.grid(row=6, column=1)
        # 座位类型
        tkinter.Label(self, text="密码").grid(row=7, column=0)
        self.seat_type = tkinter.Entry(self)
        self.seat_type.grid(row=7, column=1)
        # 手机号
        tkinter.Label(self, text="密码").grid(row=8, column=0)
        self.phone_number = tkinter.Entry(self)
        self.phone_number.grid(row=8, column=1)
        # 确定按钮
        self.commit = tkinter.Button(self, width=20)
        self.commit['text'] = "确定"
        self.commit['command'] = self.say_hi
        self.commit.grid(row=9, columnspan=2)

    def say_hi(self):
        self.commit.flash()

        username = self.username.get()
        password = self.password.get()
        train_code = self.train_code.get()
        src = self.src
        dst = self.dst
        date = self.date.get()
        passenger = self.passenger.get()
        seat_type = self.seat_type.get()
        phone_number = self.phone_number.get()

        d = Spider()
        d.login_in(username, password)
        result = d.order_ticket(train_code, src, dst, date, seat_type, passenger)
        SendSMS(phone_number, "订票成功！" + str(result))


if __name__ == "__main__":
    t = tkinter.Tk()
    app = App(master=t)
    app.mainloop()
