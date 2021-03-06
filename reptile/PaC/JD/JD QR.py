
#encoding:utf-8

"""
JD online shopping helper tool
-----------------------------------------------------
only support to login by QR code,
username / password is not working now.
"""



import bs4
import requests
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

import os
import time
import json
import random
import argparse
import sys
import importlib
importlib.reload(sys)

# from imp import reload
# import importlib
# import lib.reload(sys)
# from selenium import webdriver
#py3.5不用此设置
#sys.setdefaultencoding('utf-8')

# get function name

#

"""
1. 函数: Python提供许多内建函数,例如: print()
自定义函数:
def 函数名（参数列表）:
    函数体

2. 变量类型:
在 python 中，类型属于对象，变量是没有类型的：
a=[1,2,3]
a="Runoob"
以上代码中，[1,2,3] 是 List 类型，"Runoob" 是 String 类型，而变量 a 是没有类型.
她仅仅是一个对象的引用（一个指针），可以是 List 类型对象，也可以指向 String 类型对象。
3. 可变(mutable)与不可变(immutable)对象
在 python 中，strings, tuples, 和 numbers 是不可变对象(如a = "ss" fun（a）将 a副本传到函数)，而 list,dict 等则是可以修改的对象(变量赋值 la=[1,2,3,4] fun(la),将 la对象/指针传进去)。
4.匿名函数: lambda [arg1 [,arg2,.....argn]]:expression
例如: sum = lambda arg1, arg2: arg1 + arg2;
print ("相加后的值为 : ", sum( 10, 20 ))


 知识点1:
python 使用 lambda 来创建匿名函数(匿名: 不使用 def 标准的形式定义函数)
案例:
sum = lambda arg1, arg2: arg1 + arg2;
print ("相加后的值为 : ", sum( 10, 20 ))
说明:
lambda 只是一个表达式，函数体比 def 简单很多。
lambda 的主体是一个表达式，而不是一个代码块。仅仅能在lambda表达式中封装有限的逻辑进去。
lambda 函数拥有自己的命名空间，且不能访问自有参数列表之外或全局命名空间里的参数。
lambda 函数看起来只能写一行，却不等同于C或C++的内联函数，后者的目的是调用小函数时不占用栈内存从而增加运行效率。

本例: FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
FuncName 函数用于

try:
    .....
except (Exception) as e:
    print ('Exp {0} : {1}'.format(FuncName(), e))

    首先，执行try子句（在关键字try和关键字except之间的语句）
如果没有异常发生，忽略except子句，try子句执行后结束。
如果在执行try子句的过程中发生了异常，那么try子句余下的部分将被忽略。如果异常的类型和 except 之后的名称相符，那么对应的except子句将被执行。最后执行 try 语句之后的代码。
如果一个异常没有与任何的except匹配，那么这个异常将会传递给上层的try中。

解释:
    传入:FuncName(x),x不传,使用默认值 n=0.
    sys._getframe().f_code.co_filename  #当前文件名，可以通过__file__获得
    sys._getframe(0).f_code.co_name  #当前函数名
    sys._getframe(1).f_code.co_name　#调用该函数的函数的名字，如果没有被调用，则返回<module>，貌似call stack的栈低
    sys._getframe().f_lineno #当前行号

"""
def get_cur_info():
    print ('当前路径文件名:',sys._getframe().f_code.co_filename,"哈哈")
    print ('当前函数名:',sys._getframe(0).f_code.co_name)
    print ('调用函数名,没调用 module:',sys._getframe(1).f_code.co_name)
    print ('当前行号:',sys._getframe().f_lineno)


# #打印函数名以及是否调用:
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        # strip(aa) 方法用于移除字符串头尾指定的字符aa（默认为空格）
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''


class JDWrapper(object):
    '''
    This class used to simulate login JD
    '''

    def __init__(self, usr_name=None, usr_pwd=None):
        # cookie info
        self.trackid = ''
        self.uuid = ''
        self.eid = ''
        self.fp = ''

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.interval = 0

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.imag = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'
        # requests.Session()会话对象能够实现跨请求保持某些参数。它也会在同一个 Session 实例发出的所有请求之间保持 cookie
        self.sess = requests.Session()
        self.sess.trust_env = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }

        self.cookies = {

        }

        '''
        try:
            self.browser = webdriver.PhantomJS('phantomjs.exe')
        except Exception, e:
            print 'Phantomjs initialize failed :', e
            exit(1)
        '''

    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if resp_text[0] == '(':
            resp_text = resp_text[1:-1]

        for k, v in json.loads(resp_text).items():
            print (u'%s : %s' , (k, v))

    @staticmethod
    def response_status(resp):
        if resp.status_code != requests.codes.OK:
            print ('Status: %u, Url: %s' , (resp.status_code, resp.url))
            return False
        return True

    def _need_auth_code(self, usr_name):
        # check if need auth code
        #
        auth_dat = {
            'loginName': usr_name,
        }
        payload = {
            'r': random.random(),
            'version': 2015
        }

        resp = self.sess.post(self.auth, data=auth_dat, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            return js['verifycode']

        print (u'获取是否需要验证码失败')
        return False

    """ 获取二维码代码:
    os.path.join(A, B),路径拼接
    os.getcwd() ,返回当前进程的工作目录
    time.time() 返回当前时间的时间戳
    int(time.time() * 1000) 当前时间的毫秒表示
    """

    def _get_auth_code(self, uuid):
        # 图片保存路径:
        image_file = os.path.join(os.getcwd(), 'authcode.jfif')

        payload = {
            'a': 1,
            'acid': uuid,
            'uid': uuid,
            'yys': str(int(time.time() * 1000)),
        }

        # get auth code
        r = self.sess.get(self.imag, params=payload)
        if not self.response_status(r):
            print (u'获取验证码失败')
            return False

        with open(image_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

            f.close()

        os.system('start ' + image_file)
        return str(input('Auth Code: '))

    # random.random()
    # 用于生成一个随机浮点数

    def _login_once(self, login_data):
        # url parameter
        payload = {
            'r': random.random(),
            'uuid': login_data['uuid'],
            'version': 2015,
        }

        resp = self.sess.post(self.login, data=login_data, params=payload)
        if self.response_status(resp):
            js = json.loads(resp.text[1:-1])
            # self.print_json(resp.text)

            if not js.get('success'):
                print  (js.get('emptyAuthcode'))
                return False
            else:
                return True

        return False

    def _login_try(self):
        """ login by username and password, but not working now.

        .. deprecated::
            Use `login_by_QR`
        """
        # get login page
        # resp = self.sess.get(self.home)
        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} > 登陆'.format(time.ctime()))

        try:
            # 2016/09/17 PhantomJS can't login anymore
            self.browser.get(self.home)
            soup = bs4.BeautifulSoup(self.browser.page_source, "html.parser")

            # set cookies from PhantomJS
            for cookie in self.browser.get_cookies():
                self.sess.cookies[cookie['name']] = str(cookie['value'])

            # for (k, v) in self.sess.cookies.items():
            # 	print '%s: %s' % (k, v)



            # response data hidden input == 9 ??. Changed
            inputs = soup.select('form#formlogin input[type=hidden]')
            rand_name = inputs[-1]['name']
            rand_data = inputs[-1]['value']
            token = ''

            for idx in range(len(inputs) - 1):
                id = inputs[idx]['id']
                va = inputs[idx]['value']
                if id == 'token':
                    token = va
                elif id == 'uuid':
                    self.uuid = va
                elif id == 'eid':
                    self.eid = va
                elif id == 'sessionId':
                    self.fp = va

            auth_code = ''
            if self.need_auth_code(self.usr_name):
                auth_code = self.get_auth_code(self.uuid)
            else:
                print (u'无验证码登陆')

            login_data = {
                '_t': token,
                'authcode': auth_code,
                'chkRememberMe': 'on',
                'loginType': 'f',
                'uuid': self.uuid,
                'eid': self.eid,
                'fp': self.fp,
                'nloginpwd': self.usr_pwd,
                'loginname': self.usr_name,
                'loginpwd': self.usr_pwd,
                rand_name: rand_data,
            }

            login_succeed = self.login_once(login_data)
            if login_succeed:
                self.trackid = self.sess.cookies['TrackID']
                print (u'登陆成功 %s' , self.usr_name)
            else:
                print (u'登陆失败 %s' , self.usr_name)

            return login_succeed

        #旧:except Exception, e:
        except (Exception) as e:
            print ('Exception:', e.message)
            raise
        finally:
            self.browser.quit()

        return False

    def login_by_QR(self):
        # jd login by QR code
        try:
            print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print (u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0],
                headers=self.headers
            )
            if resp.status_code != requests.codes.OK:
                print (u'获取登录页失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # step 2: get QR image
            resp = self.sess.get(
                urls[1],
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'appid': 133,
                    'size': 147,
                    't': (int)(time.time() * 1000)
                }
            )
            if resp.status_code != requests.codes.OK:
                print (u'获取二维码失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            ## save QR code
            image_file = 'qr.png'
            with open(image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)

            ## scan QR code with phone
            os.system('start ' + image_file)

            # step 3： check scan result
            ## mush have
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers=self.headers,
                    cookies=self.cookies,
                    params={
                        'callback': 'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': (int)(time.time() * 1000)
                    }
                )

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1 + 1:n2])

                if rs['code'] == 200:
                    print (u'{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    print (u'{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)

            if not qr_ticket:
                print (u'二维码登陆失败')
                return False

            # step 4: validate scan result
            ## must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3],
                headers=self.headers,
                cookies=self.cookies,
                params={'t': qr_ticket},
            )
            if resp.status_code != requests.codes.OK:
                print (u'二维码登陆校验失败: %u' % resp.status_code)
                return False

            ## login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            print (u'登陆成功')
            return True

        except Exception as e:
            print ('Exp:', e)
            raise

        return False

    def good_stock(self, stock_id, good_count=1, area_id=None):
        '''
        33 : on sale,
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        # stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        #   jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        stock_url = 'http://c0.3.cn/stocks'

        payload = {
            'type': 'getstocks',
            'skuIds': str(stock_id),
            'area': area_id or '1_72_2799_0',  # area change as needed
        }

        try:
            # get stock state
            resp = self.sess.get(stock_url, params=payload)
            if not self.response_status(resp):
                print (u'获取商品库存失败')
                return (0, '')

            # return json
            resp.encoding = 'gbk'
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info[stock_id]['StockState'])
            stock_stat_name = stock_info[stock_id]['StockStateName']

            # 33 : on sale, 34 : out of stock, 36: presell
            return stock_stat, stock_stat_name

        except Exception as e:
            print ('Exception:', e)
            time.sleep(5)

        return (0, '')

    def good_detail(self, stock_id, area_id=None):
        # return good detail
        good_data = {
            'id': stock_id,
            'name': '',
            'link': '',
            'price': '',
            'stock': '',
            'stockName': '',
        }

        try:
            # shop page
            stock_link = 'http://item.jd.com/{0}.html'.format(stock_id)
            resp = self.sess.get(stock_link)

            # good page
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # good name
            tags = soup.select('div#name h1')
            if len(tags) == 0:
                tags = soup.select('div.sku-name')
            good_data['name'] = tags_val(tags).strip(' \t\r\n')

            # cart link
            tags = soup.select('a#InitCartUrl')
            link = tags_val(tags, key='href')

            if link[:2] == '//': link = 'http:' + link
            good_data['link'] = link

        except (Exception) as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        # good price
        good_data['price'] = self.good_price(stock_id)

        # good stock
        good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=stock_id, area_id=area_id)
        # stock_str = u'有货' if good_data['stock'] == 33 else u'无货'

        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} >>>>>>>>>>>>>>>>>>>>> 商品详情'.format(time.ctime()))
        print (u'编号：{0}'.format(good_data['id']))
        print (u'库存：{0}'.format(good_data['stockName']))
        print (u'价格：{0}'.format(good_data['price']))
        print (u'名称：{0}'.format(good_data['name']))
        print (u'链接：{0}'.format(good_data['link']))

        return good_data

    def good_price(self, stock_id):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type': 1,
            'pduid': int(time.time() * 1000),
            'skuIds': 'J_' + stock_id,
        }

        price = '?'
        try:
            resp = self.sess.get(url, params=payload)
            resp_txt = resp.text.strip()
            # print resp_txt

            js = json.loads(resp_txt[1:-1])
            # print u'价格', 'P: {0}, M: {1}'.format(js['p'], js['m'])
            price = js.get('p')

        except (Exception) as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        return price

    def buy(self, options):
        # stock detail
        good_data = self.good_detail(options.good)

        # retry until stock not empty
        if good_data['stock'] != 33:
            # flush stock state
            while good_data['stock'] != 33 and options.flush:
                print (u'<%s> <%s>' % (good_data['stockName'], good_data['name']))
                time.sleep(options.wait / 1000.0)
                good_data['stock'], good_data['stockName'] = self.good_stock(stock_id=options.good,
                                                                             area_id=options.area)

                # retry detail
                # good_data = self.good_detail(options.good)

        # failed
        link = good_data['link']
        if good_data['stock'] != 33 or link == '':
            # print u'stock {0}, link {1}'.format(good_data['stock'], link)
            return False

        try:
            # add to cart
            resp = self.sess.get(link, cookies=self.cookies)
            soup = bs4.BeautifulSoup(resp.text, "html.parser")

            # tag if add to cart succeed
            tag = soup.select('h3.ftx-02')
            if tag is None:
                tag = soup.select('div.p-name a')

            if tag is None or len(tag) == 0:
                print (u'添加到购物车失败')
                return False

            print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print (u'{0} >>>>>>>>>>>>>>>>>>>>> 购买详情'.format(time.ctime()))
            print (u'结果：{0}'.format(tags_val(tag)))

            # change count
            self.buy_good_count(options.good, options.count)

        except (Exception) as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))
        else:
            self.cart_detail()
            return self.order_info(options.submit)

        return False

    def buy_good_count(self, good_id, count):
        url = 'http://cart.jd.com/changeNum.action'

        payload = {
            'venderId': '8888',
            'pid': good_id,
            'pcount': count,
            'ptype': '1',
            'targetId': '0',
            'promoID': '0',
            'outSkus': '',
            'random': random.random(),
            'locationId': '1-72-2799-0',  # need changed to your area location id
        }

        try:
            rs = self.sess.post(url, params=payload, cookies=self.cookies)
            if rs.status_code == 200:
                js = json.loads(rs.text)
                if js.get('pcount'):
                    print (u'数量：%s @ %s' % (js['pcount'], js['pid']))
                    return True
            else:
                print (u'购买 %d 失败' % count)

        except (Exception) as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        return False




"""
<div class="item-form">
   <div class="cell p-goods">
   <div class="item-form">
   <div class="item-form">
   <div class="item-form">
   <div class="item-form">
   <div class="item-form">
"""


'''
数据结构:
< div class = "item-form"> 包裹着订单总信息
    <div class = "p-quantity">数量
<div class = "quantity-form">数量
    <input >数量
<div class = "p-price">单价
    <strong>单价</strong>
<div class = "p-sum"> 总价
    <strong>总价</strong>
<div class = "p-goods">商品信息
    <div class = "item-msg">商品名称
        <div class = "p-name">商品名称
            <a>商品名称
'''
def cart_detail(self):
    # list all goods detail in cart
    cart_url = 'https://cart.jd.com/cart.action'
    cart_header = u'购买    数量    价格        总价        商品'
    cart_format = u'{0:8}{1:8}{2:12}{3:12}{4}'

    try:
        resp = self.sess.get(cart_url, cookies=self.cookies)
        resp.encoding = 'utf-8'
        soup = bs4.BeautifulSoup(resp.text, "html.parser")

        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} >>>>>>>>>>>>>>>>>>>>>> 购物车明细'.format(time.ctime()))
        print (cart_header)

        for item in soup.select('div.item-form'):
            check = tags_val(item.select('div.cart-checkbox input'), key='checked')
            check = ' + ' if check else ' - '
            count = tags_val(item.select('div.quantity-form input'), key='value')
            price = tags_val(item.select('div.p-price strong'))
            sums = tags_val(item.select('div.p-sum strong'))
            gname = tags_val(item.select('div.p-name a'))
            #: ￥字符解析出错, 输出忽略￥
            print (cart_format.format(check, count, price[1:], sums[1:], gname))

        t_count = tags_val(soup.select('div.amount-sum em'))
        t_value = tags_val(soup.select('span.sumPrice em'))
        print (u'总数: {0}'.format(t_count))
        print (u'总额: {0}'.format(t_value[1:]))

    except (Exception) as e:
        print ('Exp {0} : {1}'.format(FuncName(), e))

    def order_info(self, submit=False):
        # get order info detail, and submit order
        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} >>>>>>>>>>>>>>>>>>>>> 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid': str(int(time.time() * 1000)),
            }

            # get preorder page
            rs = self.sess.get(order_url, params=payload, cookies=self.cookies)
            soup = bs4.BeautifulSoup(rs.text, "html.parser")

            # order summary
            payment = tag_val(soup.find(id='sumPayPriceId'))
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = tag_val(detail.find(id='sendMobile'))
                snd_add = tag_val(detail.find(id='sendAddr'))

                print (u'应付款：{0}'.format(payment))
                print (snd_usr)
                print (snd_add)

            # just test, not real order
            if not submit:
                return False

            # order info
            payload = {
                'overseaPurchaseCookies': '',
                'submitOrderParam.btSupport': '1',
                'submitOrderParam.ignorePriceChange': '0',
                'submitOrderParam.sopNotPutInvoice': 'false',
                'submitOrderParam.trackID': self.trackid,
                'submitOrderParam.eid': self.eid,
                'submitOrderParam.fp': self.fp,
            }

            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
            rp = self.sess.post(order_url, params=payload, cookies=self.cookies)

            if rp.status_code == 200:
                js = json.loads(rp.text)
                if js['success'] == True:
                    print (u'下单成功！订单号：{0}'.format(js['orderId']))
                    print (u'请前往东京官方商城付款')
                    return True
                else:
                    print (u'下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                print (u'请求失败. StatusCode:', rp.status_code)

        except (Exception) as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        return False

"""
代码中经常会有变量是否为None的判断，有三种主要的写法：
 第一种是`if x is None`；
第二种是 `if not x：`；
第三种是`if not x is None`（这句这样理解更清晰`if not (x is None)`）
结论：
`if x is not None`是最好的写法，清晰，不会出现错误，以后坚持使用这种写法。
使用if not x这种写法的前提是：必须清楚x等于None,  False, 空字符串"", 0, 空列表[], 空字典{}, 空元组()时对你的判断没有影响才行。


while not jd.buy(options) and options.flush:
 ----not jd.buy(options) 为真---- options.flush为真,则执行后边的语句
"""
def main(options):
    #
    jd = JDWrapper()
    if not jd.login_by_QR():
        return

    while not jd.buy(options) and options.flush:
        time.sleep(options.wait / 1000.0)

"""
flush() 方法是用来刷新缓冲区的，即将缓冲区中的数据立刻写入文件，同时清空缓冲区，不需要是被动的等待输出缓冲区写入。
一般情况下，文件关闭后会自动刷新缓冲区，但有时你需要在关闭前刷新它，这时就可以使用 flush() 方法。
"""
if __name__ == '__main__':

    # 编程测试
    get_cur_info()

    # 命令行解析模块: 方便在命令行通过 help 形式展示帮助信息

    # help message
    parser = argparse.ArgumentParser(description='Simulate to login Jing Dong, and buy sepecified good')
    # parser.add_argument('-u', '--username',
    #					help='Jing Dong login user name', default='')
    # parser.add_argument('-p', '--password',
    #					help='Jing Dong login user password', default='')
    parser.add_argument('-a', '--area',
                        help='Area string, like: 1_72_2799_0 for Beijing', default='1_72_2799_0')
    parser.add_argument('-g', '--good',
                        help='Jing Dong good ID', default='')
    parser.add_argument('-c', '--count', type=int,
                        help='The count to buy', default=1)
    parser.add_argument('-w', '--wait',
                        type=int, default=500,
                        help='Flush time interval, unit MS')
    parser.add_argument('-f', '--flush',
                        action='store_true',
                        help='Continue flash if good out of stock')
    parser.add_argument('-s', '--submit',
                        action='store_true',
                        help='Submit the order to Jing Dong')

    # example goods
    hw_watch = '2567304'
    iphone_7 = '3133851'

    get_cur_info()
    options = parser.parse_args()
    print (options)

    # for test
    if options.good == '':
        options.good = iphone_7

    '''
    if options.password == '' or options.username == '':
        print u'请输入用户名密码'
        exit(1)
    '''

    main(options)