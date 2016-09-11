import requests
import re
import time
from bs4 import BeautifulSoup
import urllib.parse
import os

class ucas(object):
    userName='userName' #用户名
    password='password' #密码
    def __init__(self):
        self.savefile='C:\\Users\\wqs\\Desktop\\wqs\\' #保存路径
        self.session=requests.session()
        self.headers={
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encodin':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Host':'sep.ucas.ac.cn',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36',
            "Connection": "keep-alive",
        }

    #登陆主页
    def login(self):
        url='http://sep.ucas.ac.cn/slogin'
        post_data={
            'userName':self.userName,
            'pwd':self.password,
            'sb':'sb'
        }

        self.session.post(url,data=post_data,headers=self.headers)

    #跳转到选课系统
    def login_jwxk(self):
        url='http://sep.ucas.ac.cn/portal/site/226/821'
        s=r = self.session.get(url, headers=self.headers)
        id=re.findall(r'Identity=(.*)"',s.text)[0]
        url='http://jwxk.ucas.ac.cn/login?Identity='+id
        self.headers['Host']='jwxk.ucas.ac.cn'
        s=self.session.get(url, headers=self.headers)

    #查看已选课程，未完成
    def selectedCourse(self):
        url='http://jwxk.ucas.ac.cn/courseManage/selectedCourse'
        s = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(s.text, 'html.parser')
        #print(soup.prettify())
        credit=soup.find_all('strong', class_='m-font-red')
        print(credit)
        #print('总学分:' + credit(1), end='\n')

    # 查看通知，未完成
    def notice(self):
        url='http://jwxk.ucas.ac.cn/notice/view/1'
        s = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(s.text, 'html.parser')
        soup.find('table',class_="table table-striped table-bordered table-advance table-hover")

    # 下载课件，完成90%，没有处理课件中包含文件夹的情况
    def login_course(self):
        url='http://sep.ucas.ac.cn/portal/site/16/801'
        s = r = self.session.get(url, headers=self.headers)
        id = re.findall(r'Identity=(.*)"', s.text)[0]
        url = 'http://course.ucas.ac.cn/portal/plogin?Identity=' + id
        self.headers['Host'] = 'course.ucas.ac.cn'

        html=self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        s=soup.find('frame',title='mainFrame')['src']
        html=self.session.get('http://course.ucas.ac.cn/'+s, headers=self.headers)
        #s = soup.find('frame', title='bottomFrame')['src']
        #html = self.session.get('http://course.ucas.ac.cn/' + s, headers=self.headers)

        html=self.session.get('http://course.ucas.ac.cn/portal/site/~201628015029023/page/',headers=self.headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        one = soup.find('ul', id='siteLinkList')
        two=soup.find('div',id='selectNav')

        base = 'http://course.ucas.ac.cn/access/content/group/'
        course = dict()

        w = one.find_all('a')
        for i in w[1:]:
            j = i['href'].find('/site/')
            course[base + i['href'][j + 6:]] = i['title']


        w=two.find_all('a')
        for i in w:
            j = i['href'].find('/site/')
            course[base + i['href'][j + 6:]]=i['alt']

        for i, j in course.items():
            path=self.savefile+j
            html=self.session.get(i, headers=self.headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            href = soup.findAll('a')

            if not os.path.exists(path):
                os.makedirs(path)

            for k in href:
                print(i+'/'+k['href'],end='\n')
                file= self.session.get(i+'/'+k['href'], stream=True)
                ppath=path+'\\'+k.string
                if not os.path.exists(ppath):  # To prevent download exists files
                    with open(ppath, 'wb') as f:
                        for chunk in file.iter_content(chunk_size=1024):
                            if chunk:  # filter out keep-alive new chunks
                                f.write(chunk)
                                f.flush()
        print('over...')

def main():
    wqs=ucas()
    wqs.login()
    #wqs.login_jwxk()
    #wqs.selectedCourse()

    wqs.login_course()

if __name__=='__main__':
    main()