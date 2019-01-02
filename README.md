# Spider12306
订票与抢票

简述： 
本爬虫实现了基本的订票与抢票功能，抢票功能初步完成逻辑上的实现，还有待进一步优化。
为了实现用户交互功能，我用django实现了简单的web界面，余票展示界面套用了12306的css，模仿了12306的风格。无论是订票还是抢票，都加入了短信通知功能。验证码我使用了云打码平台来处理。
12306在post请求方面，并不是很难，就是流程有点多，只要耐心足，终究能找到post需要的那些字段。

结果：  
![image](https://github.com/LemonBottom/Spider12306/blob/master/Screen1.png?raw=true)
![image](https://github.com/LemonBottom/Spider12306/blob/master/Screen2.png?raw=true)
![image](https://github.com/LemonBottom/Spider12306/blob/master/message.jpeg?raw=true)


