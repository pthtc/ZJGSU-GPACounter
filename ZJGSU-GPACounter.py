#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib
import urllib2
import cookielib
import re
import argparse
import sys
import zlib
import json
import time
from flask import Flask, request, render_template

app = Flask(__name__)


class GradeGetter:

    def __init__(self):
        pass

    def gpaCounterAve(self,grade):
        if grade == '优秀':
            return 90
        if grade == '良好':
            return 80
        if grade == '中等':
            return 70
        if grade == '及格':
            return 60
        if grade == '不及格':
            return 0
        if grade == '因故缺考':
            return 0
        if grade == '':
            return 0
        return grade

    def gpaCounterDefault(self,grade):
        if grade == '优秀':
            return 4
        if grade == '良好':
            return 3
        if grade == '中等':
            return 2
        if grade == '及格':
            return 1
        if grade == '不及格':
            return 0
        if grade == '因故缺考':
            return 0
        if grade == '':
            return 0

        g = float(grade)
        if g >=90:
            return 4
        elif g>=80:
            return 3
        elif g>=70:
            return 2
        elif g>=60:
            return 1
        else:
            return 0

    def gpaCounter(self,grade):
        if grade == '优秀':
            return 4
        if grade == '良好':
            return 3
        if grade == '中等':
            return 2
        if grade == '及格':
            return 1
        if grade == '不及格':
            return 0
        if grade == '因故缺考':
            return 0
        if grade == '':
            return 0

        g = float(grade)
        if g >=85:
            return 4
        elif g>=75:
            return 3
        elif g>=60:
            return 2
        else:
            return 1

    def beginProcess(self,username,password,year = '',semester = ''):
        ctemp = None
        with open('count.txt', 'r') as f:
            if str(f.read()) == '':
                with open('count.txt', 'w') as f:
                    f.write('0')
            else:
                with open('count.txt', 'r') as f:
                    ctemp = int(f.read())+1
                with open('count.txt', 'w') as f:
                    f.write(str(ctemp))

        with open('log.txt', 'a') as f:
            f.write('____________________________________________________________\n\n\nusername: '+username)

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
        html = response.read()
        self.loginUrl = 'http://124.160.64.163/jwglxt/xtgl/login_loginIndex.html'
        self.postdata = None
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        request  = urllib2.Request(
            url = self.loginUrl,
            data = self.postdata)
        request.add_header('Accept-encoding', 'gzip')
        response = self.opener.open(request)
        html = response.read()
        self.loginUrl = 'http://124.160.64.163/jwglxt/xtgl/init_cxGnPage.html'
        mkName = '学生成绩查询'
        self.postdata = urllib.urlencode({
            'gnmkdm':'N305005',
            'dyym':'/cjcx/cjcx_cxDgXscj.html',
            'gnmkmc':urllib2.quote(mkName.encode("utf-8")),
            'sfgnym':'null'
         })
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        request  = urllib2.Request(
            url = self.loginUrl,
            data = self.postdata)
        request.add_header('Accept-encoding', 'gzip')
        response = self.opener.open(request)
        html = response.read()
        self.loginUrl = 'http://124.160.64.163/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdmKey=N305005&sessionUserKey='+self.username
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
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        request  = urllib2.Request(
            url = self.loginUrl,
            data = self.postdata)
        request.add_header('Accept-encoding', 'gzip')
        response = self.opener.open(request)
        html = response.read()

        try:
            data = json.loads(html)
            countAll = 0
            countGpaAll = 0
            countAllDefualt = 0
            allGrade = 0
            allGradeNoGpa = 0
            mydic = {}
            count = 0
            if len(data['items']) == 0:
                with open('log.txt', 'a') as f:
                    f.write('no data\n')
                return ['错误','错误','错误','错误']
                exit(0)

            for x in data['items']:
                if mydic.has_key(x['kcmc']):
                    if x.has_key('cj'):
                        if float(mydic[x['kcmc']])<float(self.gpaCounterAve(x['cj'])):
                            allGradeNoGpa-=float(self.gpaCounterAve(mydic[x['kcmc']]))
                            allGradeNoGpa+=float(self.gpaCounterAve(x['cj']))
                            countAllDefualt-=float(self.gpaCounterDefault(mydic[x['kcmc']]))*float(x['xf'])
                            countAllDefualt+=float(self.gpaCounterDefault(x['cj']))*float(x['xf'])
                            countAll-=float(self.gpaCounter(mydic[x['kcmc']]))*float(x['xf'])
                            countAll+=float(self.gpaCounter(x['cj']))*float(x['xf'])
                            allGrade-= float(self.gpaCounterAve(mydic[x['kcmc']]))*float(x['xf'])
                            allGrade+= float(self.gpaCounterAve(x['cj']))*float(x['xf'])
                            mydic[x['kcmc']] = x['cj']
                else:
                    count+=1
                    if x.has_key('cj'):
                        mydic[x['kcmc']] = self.gpaCounterAve(x['cj'])
                        allGrade+= float(self.gpaCounterAve(x['cj']))*float(x['xf'])
                        allGradeNoGpa+=float(self.gpaCounterAve(x['cj']))
                        countAll+= float(self.gpaCounter(x['cj']))*float(x['xf'])
                        countAllDefualt+= float(self.gpaCounterDefault(x['cj']))*float(x['xf'])
                        countGpaAll += float(x['xf'])

            with open('log.txt', 'a') as f:
                f.write(str(countAll/countGpaAll)+'  '+str(countAllDefualt/countGpaAll)+'  '+str(allGrade/countGpaAll)+'  '+str(allGradeNoGpa/count)+'\n')
            return [str(countAll/countGpaAll),str(countAllDefualt/countGpaAll),str(allGrade/countGpaAll),str(allGradeNoGpa/count)]
        except:
            with open('log.txt', 'a') as f:
                f.write('error\n')
            return ['错误','错误','错误','错误']



@app.route('/', methods=['GET'])
def signin_form():
    count = None
    with open('count.txt', 'r') as f:
        count = f.read()

    r = '''<h2>浙江工商大学学分计算</h2>
              <form action="/" method="post">

              <p>账号<input name="username"></p>
              <p>密码<input name="password" type="password"></p>
              <p><button type="submit">查询</button></p>
              </form>
              <h4>如果出现错误，请检查账号密码或评价情况</h4>
              <h4>相同科目取最高者，请放心使用</h4>
              <h6>by 彭天浩</h6>
              <h6>QQ 461923603</h6>'''
    return r+'<h4> </h4><h4> </h4><h4> </h4><h4> </h4><h4> </h4><h4>已经被使用'+str(count)+'次</h4>'

@app.route('/', methods=['POST'])
def signin():
    getter = GradeGetter()
    arr = getter.beginProcess(request.form['username'],request.form['password'])
    string = '<h3>'+'学分(基于wes算法):'+arr[0]+'</h3>'+'<h3>'+'学分(基于标准算法): '+arr[1]+'</h3>'+'<h3>'+'加权平均分: '+arr[2]+'</h3>'+'<h3>'+'算数平均分: '+arr[3]+'</h3>'+'<a href="http://timpeng.top:5000"><input type="button" value="后退"></input></a>'  

    return string

def main():
    app.run(host='0.0.0.0')

if __name__ == '__main__':
    main()


