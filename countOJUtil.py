# coding=utf-8

import http.cookiejar
import json
import re

import urllib
from urllib import parse
from urllib import request

__author__ = 'zouxin'


class Crawler:
    '''
    This is the main crawler which contains a dictionary.
    This dictionary's key is the judge name,value is a set that contains each problem that user has ACed.
    As for submit condition , just store the number.
    '''
    name = ''
    dict_name = {}
    acArchive = {}
    submitNum = {}
    # OJ's name : [user,user]
    wrongOJ = {}
    # match dictionary.dict[oj]:[acRegex],[submitRegex]
    matchDict = {}
    supportedOJ = ['poj', 'hdu', 'zoj', 'codeforces', 'fzu', 'acdream', 'bzoj', 'ural', 'csu', 'hust', 'spoj', 'sgu',
                   'vjudge', 'bnu', 'uestc', 'zucc', 'codechef']

    def __init__(self, query_name={}):
        '''
        This is the initial part which describe the crawler opener.
        '''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }
        self.cookie = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie))
        self.dict_name = query_name
        self.name = query_name.get('default')
        '''
        initialize all the data structure
        '''
        for oj in self.supportedOJ:
            # for achive ,use set
            self.submitNum[oj] = 0
            self.acArchive[oj] = set()
            # for problem , use list
            self.wrongOJ[oj] = []

        '''
        read the dictionary which guide spider to browser website and how to match information
        '''

    def getNoAuthRules(self):
        import configparser
        import os
        cf = configparser.ConfigParser()
        config_file_path = os.path.join(os.path.dirname(__file__), "regexDict.ini")
        cf.read(config_file_path)
        # travel all the useable site
        return [(oj, cf.get(oj, 'website'), cf.get(oj, 'acRegex'), cf.get(oj, 'submitRegex')) for oj in cf.sections()]

    def actRegexRules(self, html, acRegex, submitRegex, oj):
        submission = re.findall(submitRegex, html, re.S)
        acProblem = re.findall(acRegex, html, re.S)
        # print '# submission : ', submission
        # print '# problem : ', acProblem
        # for submit
        try:
            self.submitNum[oj] += int(submission[0])
            yield oj, len(set(acProblem)), submission[0]
        except:
            self.wrongOJ[oj].append(self.name)
            yield oj, 0, 0
        # for AC merge all the information
        self.acArchive[oj] = self.acArchive[oj] | set(acProblem)

    def followRules(self, oj, website, acRegex, submitRegex):
        name = self.name
        req = urllib.request.Request(
            url=website % name,
            headers=self.headers
        )
        try:
            html = self.opener.open(req).read(timeout=5)
        except:
            self.wrongOJ[oj].append(name)
            return 0
        submission = re.findall(submitRegex, html, re.S)
        acProblem = re.findall(acRegex, html, re.S)
        print('# submission : ', submission)
        print('# problem : ', acProblem)
        # for submit
        try:
            self.submitNum[oj] += int(submission[0])
        except:
            self.wrongOJ[oj] = name
            return 0
        # for AC merge all the information
        self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
        return html

    def getInfoNoAuth(self, query_name='lqybzx'):
        '''
        This function only browser the website without authentication and also use regex.
        For 'poj','hdu','zoj','fzu','acdream','bzoj','ural','csu','hust','spoj','sgu','vjudge','bnu','cqu','uestc','zucc'
        :param query: query_name
        :return:
        '''
        import configparser
        import os
        if query_name == '':
            name = self.name
        else:
            name = query_name
        cf = configparser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), "regexDict.ini")
        cf.read(configFilePath)
        # travel all the useable site
        for oj in cf.sections():
            website = cf.get(oj, 'website')
            acRegex = cf.get(oj, 'acRegex')
            submitRegex = cf.get(oj, 'submitRegex')
            name = self.getName(oj)
            print(website % name)
            req = urllib.request.Request(
                url=website % name,
                headers=self.headers
            )
            try:
                html = str(self.opener.open(req).read())
            except:
                self.wrongOJ[oj].append(name)
                continue
            submission = re.findall(submitRegex, html, re.S)
            acProblem = re.findall(acRegex, html, re.S)
            print('# submission : ', submission)
            print('# problem : ', acProblem)
            # for submit
            try:
                self.submitNum[oj] += int(submission[0])
            except:
                self.wrongOJ[oj] = name
                continue
            # for AC merge all the information
            self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
            # print submission[0],acProblem
            # return submission[0], acProblem

    def getACdream(self, query_name=''):
        oj = 'acdream'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        req = urllib.request.Request(
            url='http://acdream.info/user/' + name,
            headers=self.headers
        )
        html = ''
        try:
            html = str(self.opener.open(req).read())
        except:
            self.wrongOJ[oj].append(name)
            return 0
        submission = re.findall('Submissions: <a href="/status\?name=.*?">([0-9]*?)</a>', html, re.S)
        linkAddress = re.findall(
            r'List of <span class="success-text">solved</span> problems</div>(.*?)<div class="block block-warning">',
            html, re.S)
        try:
            acProblem = re.findall(r'<a class="pid" href="/problem\?pid=[0-9]*?">([0-9]*?)</a>', linkAddress[0], re.S)
            self.submitNum[oj] += int(submission[0])
        except:
            self.wrongOJ[oj].append(name)
            return 0
        self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
        return submission[0], acProblem

    def getAsyncACdream(self, html, query_name=''):
        oj = 'acdream'
        if query_name == '':
            name = self.name
        else:
            name = query_name
        submission = re.findall('Submissions: <a href="/status\?name=.*?">([0-9]*?)</a>', html, re.S)
        linkAddress = re.findall(
            r'List of <span class="success-text">solved</span> problems</div>(.*?)<div class="block block-warning">',
            html, re.S)
        try:
            acProblem = re.findall(r'<a class="pid" href="/problem\?pid=[0-9]*?">([0-9]*?)</a>', linkAddress[0], re.S)
            self.submitNum[oj] += int(submission[0])
            self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
            yield oj, len(acProblem), submission[0]
        except:
            self.wrongOJ[oj].append(name)
            yield oj, 0, 0

    def showsgu(self, query_name=''):
        oj = 'sgu'
        if query_name == '':
            name = self.name
        else:
            name = query_name
        postData = {
            'find_id': name
        }
        postData = urllib.parse.urlencode(postData).encode('utf-8')
        req = urllib.request.Request(
            url='http://acm.sgu.ru/find.php',
            headers=self.headers,
            data=postData
        )
        html = ''
        try:
            html = str(self.opener.open(req, timeout=5).read())
        except:
            self.wrongOJ[oj].append(name)
            return 0
        sem = re.findall(r'</h5><ul><li>[0-9]*?.*?<a href=.teaminfo.php.id=([0-9]*?).>.*?</a></ul>', html, re.S)
        # print sem
        try:
            temp = sem[0]
            req = urllib.request.Request(
                url='http://acm.sgu.ru/teaminfo.php?id=' + str(temp),
                headers=self.headers
            )
            result = self.opener.open(req, timeout=10)
            html = str(result.read())
            submission = re.findall(r'Submitted: ([0-9]*?)', html, re.S)
            acProblem = re.findall(r'<font color=.*?>([0-9]*?)&#160</font>', html, re.S)
            # get all the information
            self.submitNum[oj] += int(submission[0])
            self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
            return submission[0], acProblem
        except:
            self.wrongOJ[oj].append(name)
            return 0

    def getCodeforces(self, query_name=''):
        '''
        get JSON information from codeforces API and parser it
        :param query_name:
        :return: Boolean value which indicates success
        '''
        oj = 'codeforces'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        print('start ' + oj)
        loopFlag = True
        loopTimes = 0
        count = 200
        startItem = 1 + loopTimes * count
        endItem = (loopTimes + 1) * count
        while loopFlag:
            '''
            use cycle to travel the information
            '''
            loopTimes += 1
            website = 'http://codeforces.com/api/user.status?handle=%s&from=%s&count=%s' % (name, startItem, endItem)
            # try to get information
            startItem = 1 + loopTimes * count
            endItem = count
            # updating data...
            try:
                jsonString = urllib.request.urlopen(website).read().decode('utf-8')
            except:
                self.wrongOJ[oj].append(name)
                return 0
            import json
            data = json.loads(jsonString)
            if data[u'status'] == u'OK':
                if len(data[u'result']) == 0:
                    break
                else:
                    pass
                # store the submit number
                self.submitNum[oj] += len(data[u'result'])
                print(len(data[u'result']))
                # print self.subcf
                for i in data[u'result']:
                    # only accept AC problem
                    if i[u'verdict'] == 'OK':
                        problemInfo = i[u'problem']
                        problemText = '%s%s' % (problemInfo[u'contestId'], problemInfo[u'index'])
                        self.acArchive[oj].add(problemText)
            else:
                break
            print(loopTimes)
        print('end ' + oj)
        return True

    def asyncGetCodeforces(self, query_name=''):
        '''
        get JSON information from codeforces API and parser it
        :param query_name:
        :return: Boolean value which indicates success
        '''
        import tornado.httpclient
        oj = 'codeforces'
        print('start CodeForce')
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        loopFlag = True
        loopTimes = 0
        count = 1000
        startItem = 1 + loopTimes * count
        endItem = (loopTimes + 1) * count
        # init async part
        client = tornado.httpclient.AsyncHTTPClient()

        # loop start
        while loopFlag:
            '''
            use cycle to travel the information
            '''
            loopTimes += 1
            website = 'http://codeforces.com/api/user.status?handle=%s&from=%s&count=%s' % (name, startItem, endItem)
            # try to get information
            startItem = 1 + loopTimes * count
            endItem = (loopTimes + 1) * count
            # updating data...
            try:
                # use async to rewrite the getting process
                req = tornado.httpclient.HTTPRequest(website, headers=self.headers, request_timeout=5)
                # jsonString = urllib2.urlopen(website).read()
                response = yield tornado.gen.Task(client.fetch, req)
                if response.code == 200:
                    jsonString = response.body
                else:
                    # raise a exception
                    raise BaseException
            except:
                self.wrongOJ[oj].append(name)
                return
            import json
            data = json.loads(jsonString)
            if data[u'status'] == u'OK':
                if len(data[u'result']) == 0:
                    break
                else:
                    pass
                # store the submit number
                self.submitNum[oj] += len(data[u'result'])

                # print self.subcf
                for i in data[u'result']:
                    # only accept AC problem
                    if i[u'verdict'] == 'OK':
                        problemInfo = i[u'problem']
                        problemText = '%s%s' % (problemInfo[u'contestId'], problemInfo[u'index'])
                        self.acArchive[oj].add(problemText)
            else:
                break

    def getCodechef(self, query_name=''):
        '''
        get JSON information from codechef Get Request and parser it
        :param query_name:
        :return: Boolean value which indicates success
        '''
        oj = 'codechef'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        req = urllib.request.Request(
            url='https://www.codechef.com/recent/user?page=0&user_handle=%s' % name,
            headers=self.headers
        )
        json_string = ''
        try:
            json_string = self.opener.open(req).read().decode('utf8')
        except:
            self.wrongOJ[oj].append(name)
            return 0
        dataDict = json.loads(json_string)
        max_page = dataDict['max_page']
        if max_page == 0:
            self.submitNum[oj] += 0
            self.acArchive[oj] = self.acArchive[oj] | set()
            return 0
        for page_num in range(0, max_page):
            req = urllib.request.Request(
                url='https://www.codechef.com/recent/user?page={}&user_handle={}'.format(page_num, name),
                headers=self.headers
            )
            json_string = ''
            try:
                json_string = self.opener.open(req).read().decode('utf8')
            except:
                self.wrongOJ[oj].append(name)
                return 0
            dataDict = json.loads(json_string)
            html = str(dataDict['content'])
            acProblems = []
            submitNum = 0
            try:
                submission = re.findall(r'_blank', html, re.S)
                submitNum += len(submission)
                acProblem = re.findall(r"a href='.*?' title='' target='_blank'>.*?</a></td><td ><span title='accepted'",
                                       html, re.S)
                acProblems += [re.findall(r"'.*?'", pro)[0].strip("'") for pro in acProblem]
                print("pages is {}".format(page_num))
            except:
                self.wrongOJ[oj].append(name)
                return 0
                # print(self.acArchive[oj],self.submitNum[oj])
        self.acArchive[oj] = self.acArchive[oj] | set(acProblems)
        self.submitNum[oj] += submitNum
        return len(self.submission[oj])

    def getSpoj(self, query_name=''):
        oj = 'spoj'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        req = urllib.request.Request(
            url='http://www.spoj.com/users/%s' % name,
            headers=self.headers
        )
        html = ''
        try:
            html = str(self.opener.open(req).read())
        except:
            self.wrongOJ[oj].append(name)
            return 0
        submission = re.findall(r'Solutions submitted</dt>.*?<dd>([0-9]*?)</dd>', html, re.S)
        rawinfo = re.findall(r'<table class="table table-condensed">(.*?)</table>', html, re.S)
        try:
            acProblem = re.findall(r'<a href="/status/.*?/">(.*?)</a>', rawinfo[0], re.S)
            self.submitNum[oj] += int(submission[0])
            self.acArchive[oj] = self.acArchive[oj] | set(acProblem)
        except:
            self.wrongOJ[oj].append(name)
            return 0
        return submission[0], acProblem

    def getVjudge(self, query_name=''):
        '''
        We will set up a cache pool to restore the cookie and keep it
        :param query_name:
        :return:
        '''
        import tornado.httpclient
        oj = 'vjudge'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        client = tornado.httpclient.AsyncHTTPClient()
        VJheaders = {
            'Host': 'vjudge.net',
            'Origin': 'http://vjudge.net',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'deflate',
        }
        VJCrawelheaders = {
            'Host': 'vjudge.net',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'deflate',
            'upgrade-insecure-requests': '1'
        }
        publicAccountDict = {
            'username': '2013300116',
            'password': '8520967123'
        }
        loginReq = urllib.request.Request(
            url='https://vjudge.net/user/login',
            data=urllib.parse.urlencode(publicAccountDict).encode("utf-8"),
            headers=VJheaders,
            method='POST'
        )
        cookie = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        try:
            # hold the cookie
            response = opener.open(loginReq, timeout=20).read().decode('utf-8')
        except Exception as e:
            self.wrongOJ[oj] = name
            return
        # query the API
        loopFlag = True
        maxId = ''
        pageSize = 500
        status = '%20'
        while loopFlag:
            req = urllib.request.Request(
                url='https://vjudge.net/user/submissions?username=%s&pageSize=%s&status=%s&maxId=%s' % (
                    name, pageSize, status, maxId),
                headers=VJCrawelheaders
            )
            try:
                # buf = StringIO.StringIO( opener.open(req).read().content)
                # gzip_f = gzip.GzipFile(fileobj=buf)
                jsonString = opener.open(req).read()
                # jsonString = gzip_f.read()
                dataDict = json.loads(jsonString.decode('utf-8'))
                dataList = dataDict['data']
            except Exception as e:
                self.wrongOJ[oj].append(name)
                break
            for vID, orignID, ojName, probID, result, execSeconds, execMemory, languages, codeLength, submitTime in dataList:
                oj = ojName.lower()
                # only extract AC status
                if result == 'AC':
                    self.acArchive['vjudge'].add('{}:{}'.format(ojName, probID))
                    if self.acArchive.get(oj) is not None:
                        self.acArchive[oj].add(probID)
                    else:
                        # initialize the dict, insert value set
                        self.acArchive[oj] = set().add(probID)
                else:
                    pass
                if self.submitNum.get(oj) is None:
                    self.submitNum[oj] = 1
                    if self.acArchive.get(oj) is None:
                        self.acArchive[oj] = set()
                else:
                    self.submitNum[oj] += 1
                # vjudge's submit is not added to total number
                self.submitNum['vjudge'] += 1
            break
        return 1

    def asyncGetVjudge(self, query_name=''):
        '''
        We will set up a cache pool to restore the cookie and keep it
        tornado will use it
        :param query_name:
        :return:
        '''
        import tornado.gen
        oj = 'vjudge'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        VJheaders = {
            'Host': 'vjudge.net',
            'Origin': 'http://vjudge.net',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'deflate',
            # 'Cookie':'ga=GA1.3.1416134436.1469179876',
        }
        VJCrawelheaders = {
            'Host': 'vjudge.net',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'deflate',
            'upgrade-insecure-requests': '1'
            # 'Cookie':'ga=GA1.3.1416134436.1469179876',
        }
        publicAccountDict = {
            'username': '2013300116',
            'password': '8520967123'
        }
        website = 'http://vjudge.net/user/login'
        # init non-block part
        client = tornado.httpclient.AsyncHTTPClient()
        # auth
        authData = urllib.parse.urlencode(publicAccountDict).encode('utf-8')
        req = tornado.httpclient.HTTPRequest(website, headers=self.headers, request_timeout=5, method='POST',
                                             body=authData)

        cookie = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        # client fetch the data
        print('yes')
        response = yield tornado.gen.Task(client.fetch, req)
        # response = client.fetch(req)
        if response.code == 200:
            # auth successfully
            print(response)
            pass
        else:
            print(response)
            self.wrongOJ[oj] = name
            return
        # query the API
        loopFlag = True
        maxId = None
        pageSize = 100
        status = None
        while loopFlag:
            req = urllib.request.Request(
                url='http://vjudge.net/user/submissions?username=%s&pageSize=%s&status=%s&maxId=%s' % (
                    name, pageSize, status, maxId),
                headers=VJheaders
            )
            try:
                jsonString = opener.open(req).read()
                dataDict = json.loads(jsonString)
                dataList = dataDict['data']
            except Exception as e:
                self.wrongOJ[oj].append(name)
                break
            for vID, orignID, ojName, probID, result, execSeconds, execMemory, languages, codeLength, submitTime in dataList:
                oj = ojName.lower()
                # only extract AC status
                if result == 'AC':
                    if oj in self.acArchive:
                        self.acArchive[oj].add(probID)
                    else:
                        # initialize the dict, insert value set
                        self.acArchive[oj] = set().add(probID)
                else:
                    pass
                self.submitNum[oj] += 1
                # vjudge's submit is not added to total number
                self.submitNum['vjudge'] += 1
        return

    def getUestc(self, query_name=''):
        oj = 'uestc'
        if query_name == '':
            name = self.getName(oj)
        else:
            name = query_name
        req = urllib.request.Request(
            url='http://acm.uestc.edu.cn/user/userCenterData/%s' % name,
            headers=self.headers,
        )
        try:
            jsonString = self.opener.open(req).read().decode('utf8')
        except:
            self.wrongOJ[oj].append(name)
            return 0
        dataDict = json.loads(jsonString)
        # detect AC item
        if dataDict['result'] == 'error':
            self.wrongOJ[oj].append(name)
            return 0
        else:
            for dictItem in dataDict['problemStatus']:
                if dictItem['status'] == 1:
                    self.acArchive[oj].add(dictItem['problemId'])
                else:
                    pass
            self.submitNum[oj] += len(dataDict['problemStatus'])
        return 1

    def getAsyncUestc(self, jsonString):
        oj = 'uestc'
        name = self.getName(oj)
        dataDict = json.loads(jsonString)
        # detect AC item
        if dataDict['result'] == 'error':
            self.wrongOJ[oj].append(name)
            yield oj, 0, 0
        else:
            ac = 0
            for dictItem in dataDict['problemStatus']:
                if dictItem['status'] == 1:
                    self.acArchive[oj].add(dictItem['problemId'])
                    ac += 1
                else:
                    pass
            self.submitNum[oj] += len(dataDict['problemStatus'])
            yield oj, ac, len(dataDict['problemStatus'])

    def getTotalACNum(self):
        '''
        get the total number from dictionary that store the AC data.
        :return: the total AC's
        '''
        totalNum = 0
        for key, value in self.acArchive.items():
            # value should be a set
            totalNum += len(value)
        return totalNum

    def getTotalSubmitNum(self):
        '''
        get the total number from dictionary that store the submit data
        :return:
        '''
        totalNum = 0
        for key, value in self.submitNum.items():
            if key != 'vjudge':
                totalNum += int(value)
            else:
                # discard the submission data about vjudge
                pass
        return totalNum

    def changeCurrentName(self, name):
        self.dict_name = name
        self.name = self.dict_name['default']
        return True

    def getName(self, ojName):
        return self.name if self.dict_name.get(ojName) is None else self.dict_name.get(ojName)

    def run(self):
        self.getInfoNoAuth()
        self.getACdream()
        # self.getCodechef()
        self.getCodeforces()
        self.getSpoj()
        self.getUestc()
        self.getVjudge()


if __name__ == '__main__':
    a = Crawler(query_name={'default': 'sillyrobot', 'zucc': '31601185', 'vjudge': 'hxamszi'})
    a.getVjudge()
    # print (a.getNoAuthRules())
    # a.getInfoNoAuth()
    # a.getACdream()
    # print("get Codeforce now")
    # a.getCodeforces()
    # print("get spoj now")
    # a.getSpoj()
    # print("get uestc now")
    # a.getUestc()
    # print("get vj now")
    # a.getVjudge()
    # print(a.acArchive)
    # print(a.submitNum)