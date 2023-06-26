import argparse
import json
import os.path
from robobrowser import RoboBrowser
import requests
import click
import time
import ssl
import sys 
import os

# 命令行参数（自行修改）
cpp = [
    "-std=c++11",
    '-lpthread'
]
java = []
python = []


cur_path = os.path.abspath(__file__)
dir_path = os.path.abspath(os.path.dirname(cur_path) + os.path.sep + ".")
prj_path = os.path.abspath(os.path.dirname(dir_path) + os.path.sep + ".")
psn_path = os.getcwd()
browser = None

login_once = False

# 用户信息 ('username', 'password', 'contest_id')
info_data = {}

from html.parser import HTMLParser

# 从 <div class="input"> 或者 <div class="output"> 中解析样例
class SampParser(HTMLParser):
    def __init__(self, folder, file):
        HTMLParser.__init__(self)
        self.folder = folder
        self.file = file
        self.sam_in_text = None
        self.in_pre = False
    def handle_starttag(self, tag, attrs):
        if tag == 'pre':
            self.sam_in_text = open('%s/%s' % (self.folder, self.file), 'wb')
            self.in_pre = True
    def handle_endtag(self, tag):
        if tag == 'br':
            if self.in_pre:
                self.sam_in_text.write('\n'.encode('utf-8'))
        elif tag == 'div':
            if self.in_pre:
                self.sam_in_text.write('\n'.encode('utf-8'))
        elif tag == 'pre':
            if self.in_pre:
                self.sam_in_text.close()
                self.in_pre = False
    def handle_data(self, data):
        if self.in_pre:
            self.sam_in_text.write(data.encode('utf-8'))

class RankParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.conti = False
        self.in_td = False
        self.td_str = ''
        self.first_tr = True
        self.row_lst = []
        self.is_myself = False
    def handle_starttag(self, tag, attrs):
        if self.conti:
            return
        if tag == 'td' or tag == 'th':
            self.in_td = True
    def handle_endtag(self, tag):
        if tag == 'tr':
            if not self.conti:
                if self.first_tr:
                    self.first_tr = False
                    for i in range(0, len(self.row_lst)):
                        if i == 0:
                            print('+----------', end='')
                        elif i == 1:
                            print('+------------------', end='')
                        elif i == 2:
                            print('+-----', end='')
                        elif i == 3:
                            print('+-----------', end='')
                        else:
                            print('+-----', end='')
                    print('+')
                for i in range(0, len(self.row_lst)):
                    if self.is_myself:
                        print('\033[42m',end='')
                    if i == 0:
                        print('|{:^10}'.format(self.row_lst[i]), end='')
                    elif i == 1:
                        print('|{:^18}'.format(self.row_lst[i]), end='')
                    elif i == 2:
                        print('|{:^5}'.format(self.row_lst[i]), end='')
                    elif i == 3:
                        print('|{:^11}'.format(self.row_lst[i]), end='')
                    else:
                        print('|{:^5}'.format(self.row_lst[i]), end='')
                print('|',end='')
                if self.is_myself:
                    print('\033[0m',end='')
                print()
                for i in range(0, len(self.row_lst)):
                    if i == 0:
                        print('+----------', end='')
                    elif i == 1:
                        print('+------------------', end='')
                    elif i == 2:
                        print('+-----', end='')
                    elif i == 3:
                        print('+-----------', end='')
                    else:
                        print('+-----', end='')
                print('+')
                
            self.row_lst = []
            self.conti = False
            self.is_myself = False
        if self.conti:
            return
        if tag == 'td' or tag == 'th':
            self.in_td = False
            self.td_str = self.td_str.strip()
            if len(self.td_str) == 0:
                self.row_lst.append(self.td_str)
            elif self.td_str[0] == '+' or self.td_str[0] == '-' or '\n' in self.td_str or '\r' in self.td_str:
                self.row_lst.append(self.td_str.split('\n')[0].split('\r')[0])
            else:
                self.row_lst.append(self.td_str)
            self.td_str = ''
    def handle_data(self, data):
        if self.conti:
            return
        if self.in_td == True:
            if info_data['username'] in data:
                self.is_myself = True
            if '*' in data and len(data) != 1:
                self.conti = True
            elif 'Accept' in data:
                self.conti = True
            else:
                self.td_str += data
# https://codeforces.com/contest/<contest_id> 的解析
class IndexParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.accepted_problem = False
        self.row_lst = []
        self.td_str = ''
        self.in_td = False
        self.in_script = False
        self.first_line = True
    def handle_starttag(self, tag, attrs):
        if tag == 'td' or tag == 'th':
            self.in_td = True
        if tag == 'tr' and ('class', 'accepted-problem') in attrs:
            self.accepted_problem = True  
        if tag == 'script':
            self.in_script = True          
    def handle_endtag(self, tag):
        if tag == 'tr':
            if self.first_line:
                print('+-----+--------------------------------------------------+---------+')
                self.first_line = False
            if self.accepted_problem:
                print('\033[42m', end='')
            for i in range(0, len(self.row_lst)):
                if i == 2:
                    continue
                if i == 0:
                    print('|{:^5}'.format(self.row_lst[i]), end='')
                elif i == 1:
                    print('|{:^50}'.format(self.row_lst[i]), end='')
                else:
                    print('| {:<8}'.format(self.row_lst[i]), end='')
            print('|', end='')
            if self.accepted_problem:
                print('\033[0m', end='')
            print('\n+-----+--------------------------------------------------+---------+')
            self.accepted_problem = False
            self.row_lst = []
        elif tag == 'td' or tag == 'th':
            self.td_str = self.td_str.strip()
            if '\r' in self.td_str or '\n' in self.td_str:
                self.td_str = self.td_str.split('\n')[0].split('\r')[0]
            self.row_lst.append(self.td_str)
            self.td_str = ''
            self.in_td = False
        elif tag == 'script':
            self.in_script = False
    def handle_data(self, data):
        if self.in_td and not self.in_script:
            self.td_str += data

# https://codeforces.com/contest/<contest_id> 的解析
class SubmissionParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.accepted_problem = False
        self.row_lst = []
        self.td_str = ''
        self.in_td = False
        self.in_script = False
        self.first_line = True
    def handle_starttag(self, tag, attrs):
        if tag == 'td' or tag == 'th':
            self.in_td = True
        if tag == 'script':
            self.in_script = True          
    def handle_endtag(self, tag):
        if tag == 'tr':
            if self.first_line:
                for i in range(0, len(self.row_lst)):
                    if i == 2:
                        continue
                    if i == 0:
                        print('+----------', end='')
                    elif i <= 2:
                        print('+--------------------', end='')
                    elif i == 3:
                        print('+---', end='')
                    elif i == 4:
                        print('+---------------', end='')
                    elif i == 5:
                        print('+-----------------------------------', end='')
                    else:
                        print('+---------', end='')
                print('+')
                self.first_line = False
            if self.accepted_problem:
                print('\033[42m', end='')
            for i in range(0, len(self.row_lst)):
                if i == 2:
                    continue
                if i == 0:
                    print('|{:^10}'.format(self.row_lst[i]), end='')
                elif i <= 2:
                    print('|{:^20}'.format(self.row_lst[i]), end='')
                elif i == 3:
                    print('|{:^3}'.format(self.row_lst[i][0]), end='')
                elif i == 4:
                    print('|{:^15}'.format(self.row_lst[i]), end='')
                elif i == 5:
                    print('|{:^35}'.format(self.row_lst[i]), end='')
                else:
                    print('| {:^8}'.format(self.row_lst[i]), end='')
            print('|', end='')
            if self.accepted_problem:
                print('\033[0m', end='')
            print()
            for i in range(0, len(self.row_lst)):
                if i == 2:
                    continue
                if i == 0:
                    print('+----------', end='')
                elif i <= 2:
                    print('+--------------------', end='')
                elif i == 3:
                    print('+---', end='')
                elif i == 4:
                    print('+---------------', end='')
                elif i == 5:
                    print('+-----------------------------------', end='')
                else:
                    print('+---------', end='')
            print('+')
            self.accepted_problem = False
            self.row_lst = []
        elif tag == 'td' or tag == 'th':
            self.td_str = self.td_str.strip()
            if '\r' in self.td_str or '\n' in self.td_str:
                self.td_str = self.td_str.split('\n')[0].split('\r')[0]
            if 'Accepted' in self.td_str or 'passed' in self.td_str:
                self.accepted_problem = True
            self.row_lst.append(self.td_str)
            self.td_str = ''
            self.in_td = False
        elif tag == 'script':
            self.in_script = False
    def handle_data(self, data):
        if self.in_td and not self.in_script:
            self.td_str += data


def handle_Login (username, password):
    print("%s> \033[33mLogining...\033[0m"%info_data['username'])
    global browser
    global login_once

    import requests
    from robobrowser import RoboBrowser

    browser = RoboBrowser(history=True, parser='lxml')
    browser.open('https://codeforces.com/enter')
    enter_form = browser.get_form('enterForm')
    enter_form['handleOrEmail'] = username
    enter_form['password'] = password
    browser.submit_form(enter_form)

    # 侧边栏是否存在用户名，存在则表示登陆成功
    div_sidbar_tags = browser.find_all('div', {'class': 'caption titled'})
    for div_sidbar_tag in div_sidbar_tags:
        if username in div_sidbar_tag.text:
            login_once = True
            return 1
    print('\033[31mError: \033[0m[{0}] Login failed!'.format(username))
    return 0

# 从特定题目中加载样例
def handle_LoadSamples (prob_id):
    # 先登录，不然进入正常的比赛了话样例出不来
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return

    browser.open('https://codeforces.com/contest/%s/problem/%s' % (info_data['contest_id'], prob_id))
    # 文件夹没有就建
    if not os.path.exists('%s'%info_data['contest_id']):
        os.mkdir('%s'%info_data['contest_id'])
    os.chdir('%s'%info_data['contest_id'])
    if not os.path.exists('%s'%prob_id):
        os.mkdir('%s'%prob_id)
    os.chdir('%s'%prob_id)

    # 先加载输入样例
    samp_id = 1
    for input_html in browser.find_all('div', {'class': 'input'}):
        sip = SampParser('%s/%s/%s'%(psn_path, info_data['contest_id'], prob_id), 'sample%s.in'%samp_id)
        sip.feed('%s'%input_html)
        samp_id += 1
    # 再加载输出样例
    samp_id = 1
    for output_html in browser.find_all('div', {'class': 'output'}):
        sip = SampParser('%s/%s/%s'%(psn_path, info_data['contest_id'], prob_id), 'sample%s.out'%samp_id)
        sip.feed('%s'%output_html)
        samp_id += 1
    os.chdir('../..')

    # URL 不存在，体现为啥都没拉进来
    if not os.path.exists('%s/%s/sample1.in'%(info_data['contest_id'], prob_id)):
        print('url: https://codeforces.com/contest/%s/problem/%s not found' % (info_data['contest_id'], prob_id))
        os.rmdir('%s/%s'%(info_data['contest_id'], prob_id))
        exit()

# 比对两个文件在清除掉 \n \t 空格 后是否相同
def file_cmp_should_block (file_path1, file_path2):
    file1 = open(file_path1, encoding='utf-8')
    file2 = open(file_path2, encoding='utf-8')
    s1 = file1.read()
    s2 = file2.read()
    s1 = s1.replace(' ', '')
    s1 = s1.replace('\n', '')
    s1 = s1.replace('\t', '')
    s2 = s2.replace(' ', '')
    s2 = s2.replace('\n', '')
    s2 = s2.replace('\t', '')
    return s1 == s2

# 测试 filename 能否解决 prob_id
def handle_Test (filename, prob_id, sample_id):
    # 加载样例
    if not os.path.exists('%s/%s'%(info_data['contest_id'], prob_id)):
        handle_LoadSamples(prob_id)
    
    # 编译 filename
    ext = filename.rsplit('.')[1]
    filename_without_ext = filename.rsplit('.')[0]
    if ext == 'cpp':
        cmd = 'g++ %s -o %s' % (filename, filename_without_ext)
        for s in cpp:
            cmd += ' %s'%s
        os.system(cmd)
    elif ext == 'java':
        cmd = 'javac %s'%filename
        for s in java:
            cmd += ' %s'%s
        os.system(cmd)

    # 单测样例
    if sample_id != None:
        if not os.path.exists('%s/%s/%s.in'%(info_data['contest_id'], prob_id, sample_id)) or not os.path.exists('%s/%s/%s.out'%(info_data['contest_id'], prob_id, sample_id)):
            print('Sample file {0}.in or {0}.out not exist ...'.format(sample_id))
            return
        file = '%s.in'%sample_id
        samp_name = (('%s/%s/%s/%s'%(psn_path, info_data['contest_id'], prob_id, file)).rsplit('.')[0])
        f = open(samp_name + "_my.out", 'w')
        f.close()
        if ext == 'cpp':
            cmd = '{0}/{1} <\"{2}.in\" >\"{2}_my.out\"'.format(psn_path, filename_without_ext, samp_name)
            os.system(cmd)
        elif ext == 'java':
            cmd = 'java {0} <\"{1}.in\" >\"{1}_my.out\"'.format(filename_without_ext, samp_name)
            os.system(cmd)
        elif ext == 'py':
            cmd = 'python %s/%s'%(psn_path, filename)
            for s in python:
                cmd += ' %s'%s
            cmd += ' <\"{0}.in\" >\"{0}_my.out\"'.format(samp_name)
            os.system(cmd)
        print('==========================[%s]'%(file.rsplit('.')[0]))
        if file_cmp_should_block(samp_name + '.out', samp_name + '_my.out'):
            print(" >> \033[1;32mAccept\033[0m\n")
        else:
            print(" >> \033[1;31mWrong Answer\033[0m\n")
            inf = open('%s.in'%samp_name)
            myf = open('%s_my.out'%samp_name)
            trf = open('%s.out'%samp_name)
            print("--- \033[1mInput:\033[0m")
            print(inf.read())
            print("--- \033[1mTrue Answer:\033[0m")
            print(trf.read())
            print("--- \033[1mYour Answer:\033[0m")
            print(myf.read())
        print()
        return

    # 多测样例，运行 filename 并比对
    for file in os.listdir('%s/%s'%(info_data['contest_id'], prob_id)):
        if file.rsplit('.')[1] == 'in':
            samp_name = (('%s/%s/%s/%s'%(psn_path, info_data['contest_id'], prob_id, file)).rsplit('.')[0])
            f = open(samp_name + "_my.out", 'w')
            f.close()
            if ext == 'cpp':
                cmd = '{0}/{1} <\"{2}.in\" >\"{2}_my.out\"'.format(psn_path, filename_without_ext, samp_name)
                os.system(cmd)
            elif ext == 'java':
                cmd = 'java {0} <\"{1}.in\" >\"{1}_my.out\"'.format(filename_without_ext, samp_name)
                os.system(cmd)
            elif ext == 'py':
                cmd = 'python %s/%s'%(psn_path, filename)
                for s in python:
                    cmd += ' %s'%s
                cmd += ' <\"{0}.in\" >\"{0}_my.out\"'.format(samp_name)
                os.system(cmd)
            print('==========================[%s]'%(file.rsplit('.')[0]))
            if file_cmp_should_block(samp_name + '.out', samp_name + '_my.out'):
                print(" >> \033[1;32mAccept\033[0m\n")
            else:
                print(" >> \033[1;31mWrong Answer\033[0m\n")
                inf = open('%s.in'%samp_name)
                myf = open('%s_my.out'%samp_name)
                trf = open('%s.out'%samp_name)
                print("--- \033[1mInput:\033[0m")
                print(inf.read())
                print("--- \033[1mTrue Answer:\033[0m")
                print(trf.read())
                print("--- \033[1mYour Answer:\033[0m")
                print(myf.read())
            print()

# 交题
def handle_Submit (filename, prob_id):
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return
        
    print("%s> \033[33mUploading file %s, please wait....\033[0m"%(info_data['username'], filename))
    browser.open('https://codeforces.com/contest/%s/problem/%s'%(info_data['contest_id'], prob_id))
    form = browser.get_form(class_ = 'submitForm')
    try:
        form['sourceFile'] = filename
    except Exception as e:
        print('file\'%s\' or url\'https://codeforces.com/contest/%s/problem/%s\' not found!'%(filename, info_data['contest_id'], prob_id))
        return
    ext = filename.rsplit('.')[1]
    if ext == 'cpp':
        form['programTypeId'] = '73'
    elif ext == 'java':
        form['programTypeId'] = 60
    elif ext == 'py':
        form['programTypeId'] = 31
    browser.submit_form(form)
    if browser.url != 'https://codeforces.com/contest/%s/my'%info_data['contest_id']:
        print('%s> Duplicate filed!'%info_data['username'])
        return
    # 等待结果
    while True:
        browser.open('https://codeforces.com/contest/%s/my'%info_data['contest_id'])
        fir_submit = browser.find('td', {'class', 'status-cell status-small status-verdict-cell'})
        status = fir_submit.text
        status = status.strip()
        print('                                                         ', end='\r')
        if 'Wrong' in status:
            print('%s> ❗ \033[31m%s\033[0m'%(info_data['username'], status), end='\r')
        elif 'passed' in status or 'Accept' in status:
            print('%s> 🎉 \033[32m%s\033[0m'%(info_data['username'], status), end='\r')
        elif 'exceeded' in status:
            print('%s> ⚠️  \033[33m%s\033[0m'%(info_data['username'], status), end='\r')
        else:
            print(info_data['username'] + '> ' + status, end='\r')
        if fir_submit['waiting'] == 'false':
            print()
            break
        time.sleep(0.5)

def handle_Rankshow ():
    # 先登录，不然进入正常的比赛了话样例出不来
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return

    browser.open('https://codeforces.com/contest/%s/standings/friends/true' % (info_data['contest_id']))
    table = browser.find('table', {'class', 'standings'})
    rp = RankParser()
    rp.feed('%s'%table)

def handle_Problemshow ():
    # 先登录，不然进入正常的比赛了话样例出不来
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return

    browser.open('https://codeforces.com/contest/%s'%info_data['contest_id'])
    table = browser.find('table', {'class', 'problems'})
    ip = IndexParser()
    ip.feed('%s'%table)

def handle_Submissionshow ():
    # 先登录，不然进入正常的比赛了话样例出不来
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return

    browser.open('https://codeforces.com/contest/%s/my'%info_data['contest_id'])
    for table in browser.find_all('table', {'class', 'status-frame-datatable'}):
        ip = SubmissionParser()
        ip.feed('%s'%table)

def handle_oneSubmission (contest_id, submission_id):
    # 先登录，不然进入正常的比赛了话样例出不来
    if not login_once:
       if not  handle_Login(info_data['username'], info_data['password']):
            print("%s> Login error: username or password wrong"%info_data['username'])
            return
    
    browser.open('https://codeforces.com/contest/%s/submission/%s'%(contest_id, submission_id))
    # print(browser.find('html'))
    code = browser.find('pre', {'class', 'program-source'})
    print('// ================================ Source Code ')
    print(code.text)

# acforces 
#     - <filename> <contest_id> <question_id>
#                                             - s
#                                             - t <samp_name> / <>
#     - race <contest_id>
#     - r <contest_id>
#     - p <contest_id>
#     - s <contest_id>
#     - l <contest_id> <submission_id>
@click.command()
@click.argument('filename',required=False, default=None)
@click.argument('contest_id',required=False, default=None)
@click.argument('problem_id',required=False, default=None)
@click.argument('opt',required=False, default=None)
@click.argument('sample_id',required=False, default=None)
def main (filename, contest_id, problem_id, opt, sample_id):
    global info_data
    """数据恢复"""
    info_file = open(dir_path + '/info.json', 'r')
    info_data = json.load(info_file)
    info_data['contest_id'] = contest_id

    if filename and contest_id and problem_id and opt:
        if opt == 's':
            handle_Submit(filename, problem_id)
        elif opt == 't':
            handle_Test(filename, problem_id, sample_id)
    elif filename and filename == 'r':
        handle_Rankshow()
    elif filename and filename == 'p':
        handle_Problemshow()
    elif filename and filename == 's':
        handle_Submissionshow()
    elif filename == 'l' and contest_id and problem_id:
        handle_oneSubmission(contest_id, problem_id)
    elif filename == 'race':
        if not login_once:
            if not handle_Login(info_data['username'], info_data['password']):
                print("%s> Login error: username or password wrong"%info_data['username'])
                return
        browser.open('https://codeforces.com/contest/%s'%info_data['contest_id'])
        for i in browser.find_all('td', {'class', 'id'}):
            prob_id = ('%s'%i.text).strip()
            handle_LoadSamples(prob_id)



    """数据备份"""
    info_json = json.dumps(info_data, sort_keys=False, indent=4, separators=(',', ': '))
    info_file = open(dir_path + '/info.json', 'w')
    info_file.write(info_json)
