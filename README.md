
> 最近想抓取一下教务网成绩，刚好学习了python，就用它来实现

# 前置条件

1. 基本的JavaScript、html知识，用于分析网站和网络请求
2. python
3. chrome 或者其他浏览器的开发者工具
4. 浙江工商大学学生账号密码

# 实现步骤

## 发起请求并获取信息

最后打印的html就是网页的源代码或是接口返回的信息

```
import urllib
import urllib2
import cookielib
import re
import sys
import zlib

self.loginUrl = 'http://124.160.64.163/jwglxt/xtgl/login_login.html'
self.cookies = cookielib.CookieJar()
self.postdata = urllib.urlencode({
    'yhm':self.username,
    'mm':self.mypassword,
    'yzm':''
})
self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
request  = urllib2.Request(
    url = self.loginUrl,
    data = self.postdata)
request.add_header('Accept-encoding', 'gzip')
response = self.opener.open(request)
html = response.read()
print html
```

## 分析请求

### 第一步 —— 登录

教务网的入口网址是

`http://124.160.64.163/jwglxt/xtgl/login_login.html`

* 打开chorme的`developer tools`

* 在登录页面输入账号密码，点击登录![](https://cl.ly/2e3Q1b362I2K)

* 此时查看developer tools里面的`network`选项,`hearder`里的`form data`告诉我们登录请求的参数是`yhm/mm/yzm`,其中yzm传空![](https://d17oy1vhnax1f7.cloudfront.net/items/25421L3U051j2W0c2702/A4E301AF-3684-4547-8BB9-94319AD78C6A.png?v=405cebbf)

### 第二步 —— 通知页面

成功登录以后就要跳转到通知页面，这时候我们需要知道点击『已阅读』按钮以后发生了什么，那就继续观察，发现请求网址是`http://124.160.64.163/jwglxt/xtgl/login_loginIndex.html`，没有参数，这时候点击『知道了』按钮，跳转到主页。这时候地址栏显示为`http://124.160.64.163/jwglxt/xtgl/index_initMenu.html?t=`，但是事实上如果通过这个网址发送参数也会失败，再次分析请求，发现实际上点击按钮之后，登录的是`http://124.160.64.163/jwglxt/xtgl/login_loginIndex.html`,没有参数。通过这个地址，我们就可以得到主页面的内容。

### 第三步 —— 主页面

加载到主页面以后，就开始比较复杂了，这时候我们需要跳转到成绩查询页面，因为新开了一个页面，所以看似是直接跳转新页面的网址`http://124.160.64.163/jwglxt/xtgl/init_cxGnPage.html`就可以，但是实际操作发现，会报`HTTP请求参数gnmkdm不能为空!`的错误。因此我们需要分析主页的源代码, 发现了这么一段``，于是发现这其实是需要向接口发送特定参数来获得不同的页面。这时候我的请求其实是``, 这个操作可以写死。

### 第四步 —— 请求成绩

加载好成绩页面之后，我们就需要告诉服务器我们需要的请求的学年和学期，那么至少有两个参数`学期`和`学年`，但是通过分析发现，除了这些还需要的参数包括每一页显示几张，当前多少页已经一些排序相关的参数，这些对我们不重要，只需要依样画葫芦就可以了。这其中有一个叫做`nd`的参数让我非常头疼，不过好在后来发现直接抄录也没有问题，惊险过关。

## 获取成绩

这时候已经分析完毕，只欠代码实现了，但是首先我们需要知道，学校服务器是通过cookie来记录登录状态的，所以我们只需要保存一份cookie就可以保持登录。

### 登录

```
self.username = username
self.mypassword = password
self.loginUrl = 'http://124.160.64.163/jwglxt/xtgl/login_login.html'
self.cookies = cookielib.CookieJar()
self.postdata = urllib.urlencode({
	'yhm':self.username,
	'mm':self.mypassword,
	'yzm':''
})
self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
request  = urllib2.Request(
url = self.loginUrl,
data = self.postdata)
request.add_header('Accept-encoding', 'gzip')
response = self.opener.open(request)
```

只有在登录这一步的时候需要新建一个cookie，其他步骤直接调用就可以了

### 通知页面

从这里开始直接写url和参数

`http://124.160.64.163/jwglxt/xtgl/login_loginIndex.html`

```
self.postdata = None
```

### 主页面

`http://124.160.64.163/jwglxt/xtgl/init_cxGnPage.html`

```
mkName = '学生成绩查询'
self.postdata = urllib.urlencode({
    'gnmkdm':'N305005',
    'dyym':'/cjcx/cjcx_cxDgXscj.html',
    'gnmkmc':urllib2.quote(mkName.encode("utf-8")),
    'sfgnym':'null'
})
```

### 成绩查询页

`http://124.160.64.163/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdmKey=N305005&sessionUserKey='+self.username`

```
if semester == '1':
    semester = '3'
elif semester == '2':
    semester = '12'
self.postdata = urllib.urlencode({
    'xnm':year,
    'xqm':semester,
    'nd':'1485587502806',
    'queryModel.showCount':'1000',
    'queryModel.currentPage':'1',
    'queryModel.sortName':'',
    'queryModel.sortOrder':'asc',
    'time':'1'
})
```

由此就拿到了成绩的json串

## 解析

拿到json串之后就需要解析并且处理显示想要的结果,非常简单，只是考虑到学生有重修的情况，需要记得相同科目取最大值列入计算。

```
data = json.loads(html)
countAll = 0
countGpaAll = 0
countAllDefualt = 0
mydic = {}

if len(data['items']) == 0:
print 'No data'
exit(0)

for x in data['items']:
    if mydic.has_key(x['kcmc']):
        if float(mydic[x['kcmc']])<float(x['cj']):
            countAllDefualt-=float(self.gpaCounterDefault(mydic[x['kcmc']]))*float(x['xf'])
            countAllDefualt+=float(self.gpaCounterDefault(x['cj']))*float(x['xf'])
            countAll-=float(self.gpaCounter(mydic[x['kcmc']]))*float(x['xf'])
            countAll+=float(self.gpaCounter(x['cj']))*float(x['xf'])
            mydic[x['kcmc']] = x['cj']
    else:
        mydic[x['kcmc']] = x['cj']
        countAll+= float(self.gpaCounter(x['cj']))*float(x['xf'])
        countAllDefualt+= float(self.gpaCounterDefault(x['cj']))*float(x['xf'])
        countGpaAll += float(x['xf'])


for z in mydic:
    print ' '+z+' '+mydic[z]

print '\n学分(基于wes算法): '+ str(countAll/countGpaAll)
print '\n学分(基于标准算法): '+ str(countAllDefualt/countGpaAll)
```

由此就实现了从教务网查询成绩并且打印学分

# 命令行参数

现在这个程序还差灵活性，最好是通过命令行参数来录入账号密码和学期学年，并且学期学年可以缺省，这时候就需要`argparse`这个库来帮助了,使用也非常简单。

```
parser = argparse.ArgumentParser(description='')
parser.add_argument('-u', dest='username', type=str, help='Your username',required = True)
parser.add_argument('-p', dest='password', type=str, help='Your password',required = True)
parser.add_argument('-y', dest='year', type=str, help='Your school year,like [2016]',required = False,default='')
parser.add_argument('-s', dest='semester', type =str, help='Your semester [1]or[2]',required = False,default='')

myUserName = None
myPassword = None
myYear = None
mySemester = None

try:
    options = parser.parse_args()
    myUserName = options.username
    myPassword = options.password
    myYear = options.year
    mySemester = options.semester
except:
    print(parser.parse_args(['-h']))
    exit(0)
```

# 结果

![](https://d3uepj124s5rcx.cloudfront.net/items/2I0Z3A2c1g1K3I2E3e2O/IMG_1688.JPG?v=d3d0dfd8)

# 完整代码（含bug修复)

[ZJGSU-GPACounter](https://github.com/pthtc/ZJGSU-GPACounter)
