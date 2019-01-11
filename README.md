# Spider12306
订票与抢票

简述：     
本爬虫实现了基本的订票与抢票功能，抢票功能初步完成逻辑上的实现，还有待进一步优化，目前加入了celery异步处理，这样可以同时进行多个抢票任务。
为了实现用户交互功能，我用django实现了简单的web界面，余票展示界面套用了12306的css，模仿了12306的风格。无论是订票还是抢票，都加入了短信通知功能。验证码我使用了云打码平台来处理。
12306在post请求方面，并不是很难，就是流程有点多，只要耐心足，终究能找到post需要的那些字段。

执行：     
tasks/spider.py文件，是订票逻辑的核心封装，如果不需要web界面，完全可以通过实例化Spider类来完成订票操作
另外要注意的是，车站名与代号是要有个转换的，比如北京站--BJP。为了方便，我将车站的代号信息存入了mysql。12306的做法是存入了js文件，我将这个文件拷贝了下来（station_name_v10014.js），可以通过重写Spider的get_station_info方法来完成站名与代号的转换。
在执行django之前，先执行命令 manage.py celery worker --loglevel=info 启动celery，当然启动redis也是需要的。

结果：  
![image](https://github.com/LemonBottom/Spider12306/blob/master/Screen1.png?raw=true)
![image](https://github.com/LemonBottom/Spider12306/blob/master/Screen2.png?raw=true)
![image](https://github.com/LemonBottom/Spider12306/blob/master/message.jpeg?raw=true)


