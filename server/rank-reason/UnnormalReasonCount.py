import datetime
import requests
import random
import base64
from lxml import etree
import os
import json

from acount import fot_user,fot_pwd
def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates
    
    '''
def get_date(month=None):
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=today-oneday
    
    month_1st=yesterday.replace(day=1)
    # month_1st=datetime.datetime.strptime(month_1st, "%Y%m%d")
    
    print(month_1st,yesterday)
    return month_1st,yesterday
    '''
    
def code_ocr(code_url):
    code_rep=s.get(code_url,headers=headers)
    # with open('verify_code.jpg','wb')as f:
        # f.write(code_rep.content)
    base64_data = base64.b64encode(code_rep.content)
    url='http://aidemo.youdao.com/ocrapi1'
    post_data={
    'imgBase': 'data:image/jpeg;base64,'+str(base64_data,'utf-8'),
    'lang': 'auto',
    'company':''
    }
    rep=s.post(url,headers=headers,data=post_data)
    if rep.json().get('errorCode')=='0':
        verify_code=rep.json().get('lines')[0].get('words')
        # print(verify_code)
        return verify_code

def login(n=0):
    login_url='https://flightontime.cn/loginAction.do?method=logIn'
    code_url='https://flightontime.cn/loginAction.do?method=createValidationCode&d=' + str(random.random())
    verify_code=code_ocr(code_url)
    post_data={
    'name': fot_user,
    'password': fot_pwd,
    'txtValidationCode': verify_code,
    'x':str(random.randint(20,232)),
    'y':str(random.randint(8,23))
    }
    # print(post_data)
    rep=s.post(login_url,headers=headers,data=post_data,allow_redirects=False)
    print(rep.status_code)
    if rep.status_code==302:
        print('正常统计系统登录成功')
    else:
        while n<3:
            n=+1
            return login(n)
        
def get_flight_info(page,start_day,end_day):
    if page>1:
        currentpage=page-1
    else:
        currentpage=page
    url=f'https://flightontime.cn/flightInfoQueryAction.do?method=list&togo={page}&advanceddivdisplay='
    post_data={
    'ScheduledDateFrom': start_day.replace('-',''),
    'ScheduledDateTo': end_day.replace('-',''),
    'CallSign': 'UEA',
    'ThreeCode': '',
    'DepAP': '',
    'ArrAP': '',
    'RegCode': '',
    'adjudicate': '',
    'isnormalid': '2',
    'isInitNormalid': '',
    'isReleaseNormalid': '',
    'delayTimeStatisticid': '',
    'currentpage': currentpage,
    'togo': ''
    }
    # print(post_data)
    rep=s.post(url,headers=headers,data=post_data)
    # print(rep.text)
    return rep.text
    
def one_page(page,start_day,end_day):
    html=get_flight_info(page,start_day,end_day)
    if "pagination" in html:
        html=etree.HTML(html)
        # print(etree.tostring(html).decode())
        pages=html.xpath('//div[@class="pagination"]/ul/li/text()')[0]
        current_page=pages.split('/')[0]
        pages=pages.split('/')[-1][1:-1]
        elements=html.xpath('//tbody[@id="query_result_body"]/tr[@class]')
        item_list=[]
        for element in elements:
            item={}
            item['fnum'] = element.xpath('./td[1]')[0].text.replace('UEA','EU')
            item['forg'] = element.xpath('./td[2]')[0].text
            item['fdst'] = element.xpath('./td[3]')[0].text
            # item['注册号']  = element.xpath('./td[4]')[0].text
            item['ScheduledDepTime'] = element.xpath('./td[5]')[0].text
            item['ScheduledDate'] = item['ScheduledDepTime'][:10]
            # item['计划到港时间'] = element.xpath('./td[6]')[0].text
            item['properties'] = element.xpath('./td[7]')[0].text
            item['UnnormalReason'] = element.xpath('./td[8]/input/@value')[0]
            # item['始发正常性'] = element.xpath('./td[9]/input/@value')[0]
            # item['放行正常性'] = element.xpath('./td[10]/input/@value')[0]
            if item['properties'] =='正班飞行 W/Z 正班':
                # print(item)
                item_list.append(item)
        # print(f'当前{current_page}，总共{pages}页\n',item_list,'\n\n')
        return item_list,pages
    else:
        return '',0
    
def multi_page(start_day,end_day):
    item_lists,pages=one_page(1,start_day,end_day)
    if int(pages)>=2:
        for page in range(2,int(pages)+1):
            item_list=one_page(page,start_day,end_day)[0]
            item_lists.extend(item_list)
    # print(item_lists)
    return item_lists
    
        
class NewData():
    def __init__(self,date_seg1,date_seg2):
        self.file='/usr/share/nginx/html/data/UnnormalReason.json'
        self.date_seg1=date_seg1
        self.date_seg2=date_seg2
        
    def old_data(self):
        if os.path.isfile(self.file):
        # file为之前日期生成的json文件，rank_data为新抓取的数据
            with open(self.file,'r',encoding='utf-8') as fp:
                old_data=json.load(fp)
                old_dates=[x.get('ScheduledDate') for x in old_data]
            return old_data,old_dates
        else:
            return '',''
            
    def get_new_data(self):
        total_list=[]
        old_data,old_dates=self.old_data()
        # 获取旧数据
        if old_data:
            total_list.extend(old_data)
        # 获取新数据
        dates=dateRange(self.date_seg1,self.date_seg2)
        for date in dates:
            if date not in old_dates:
                print(f'正在下载{date}数据')
                data_list=multi_page(date,date)
                total_list.extend(data_list)
                with open(self.file,'w',encoding='utf-8') as fp:
                    json.dump(total_list,fp,ensure_ascii=False)
        return total_list
        
    
def reason_count(item_list):
    Reason1,Reason2,Reason3,Reason4,Reason5,Reason6,='天气','公司','流量','军事活动','空管','机场'
    Reason7,Reason8,Reason9,Reason10,Reason11='联检','油料','离港系统','旅客','公共安全'
    Reason={
    Reason1:0,
    Reason2:0,
    Reason3:0,
    Reason4:0,
    Reason5:0,
    Reason6:0,
    Reason7:0,
    Reason8:0,
    Reason9:0,
    Reason10:0,
    Reason11:0,
    }
    for item in item_list:
        if item['UnnormalReason'][:2]=='01':
            Reason[Reason1]+=1
        if item['UnnormalReason'][:2]=='02':
            Reason[Reason2]+=1
        if item['UnnormalReason'][:2]=='03':
            Reason[Reason3]+=1
        if item['UnnormalReason'][:2]=='04':
            Reason[Reason4]+=1
        if item['UnnormalReason'][:2]=='05':
            Reason[Reason5]+=1
        if item['UnnormalReason'][:2]=='06':
            Reason[Reason6]+=1
        if item['UnnormalReason'][:2]=='07':
            Reason[Reason7]+=1
        if item['UnnormalReason'][:2]=='08':
            Reason[Reason8]+=1
        if item['UnnormalReason'][:2]=='09':
            Reason[Reason9]+=1
        if item['UnnormalReason'][:2]=='10':
            Reason[Reason10]+=1
        if item['UnnormalReason'][:2]=='11':
            Reason[Reason11]+=1
            
    # print(Reason)
    return Reason
    
    
###---对外接口---###
##查某航班的某航段的某个时间段内各个延误原因次数
def flight_reason(CallSign,DepAP,ArrAP,beginDate,endDate):
    total_list=NewData(beginDate,endDate).get_new_data()
    new_dates=dateRange(beginDate, endDate)
    new_list=[]
    for item in total_list:
        if item['ScheduledDate'] in new_dates:
            if item['fnum']==CallSign and item['forg']==DepAP and item['fdst']==ArrAP:
                # print(item)
                new_list.append(item)
    if new_list:
        reason=reason_count(new_list)
        print(f'{CallSign} {DepAP}-{ArrAP} {beginDate}-{endDate}\n    {reason}')
        return reason
        
        
        
        
s=requests.Session()
headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
login()
if __name__=="__main__":
    # login()
    # multi_page()
    # get_date()
    # month_data=NewData('2018-08-01','2018-08-31').get_new_data()
    CallSign,DepAP,ArrAP,beginDate,endDate='EU6661','ZUUU','ZSPD','2018-08-01','2018-09-03'
    flight_reason(CallSign,DepAP,ArrAP,beginDate,endDate)
    
    
    
    
