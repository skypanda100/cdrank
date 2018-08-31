import requests
import random
import base64
from lxml import etree
    
def code_ocr():
    code_url='https://flightontime.cn/loginAction.do?method=createValidationCode&d=' + str(random.random())
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
    verify_code=code_ocr()
    post_data={
    'name': 'uea001',
    'password': 'Uea123456',
    'txtValidationCode': verify_code,
    'x':str(random.randint(20,232)),
    'y':str(random.randint(8,23))
    }
    # print(post_data)
    rep=s.post(login_url,headers=headers,data=post_data,allow_redirects=False)
    print(rep.status_code)
    if rep.status_code==302:
        print('登陆成功')
    else:
        while n<3:
            n=+1
            return login()
        
def get_flight_info(page,CallSign,DepAP,ArrAP,start_day,end_day):
    if page>1:
        currentpage=page-1
    else:
        currentpage=page
    url=f'https://flightontime.cn/flightInfoQueryAction.do?method=list&togo={page}&advanceddivdisplay='
    post_data={
    'ScheduledDateFrom': start_day.replace('-',''),
    'ScheduledDateTo': end_day.replace('-',''),
    'CallSign': CallSign.replace('EU','UEA'),
    'ThreeCode': '',
    'DepAP': DepAP,
    'ArrAP': ArrAP,
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
    print(f'\n{CallSign} {DepAP}-{ArrAP} {start_day}-{end_day}')
    return rep.text
    
def paese_page(html):
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
            # item['航班号'] = element.xpath('./td[1]')[0].text.replace('UEA','EU')
            # item['起飞机场'] = element.xpath('./td[2]')[0].text
            # item['降落机场'] = element.xpath('./td[3]')[0].text
            # item['注册号']  = element.xpath('./td[4]')[0].text
            # item['计划离港时间'] = element.xpath('./td[5]')[0].text
            # item['计划到港时间'] = element.xpath('./td[6]')[0].text
            # item['航班性质'] = element.xpath('./td[7]')[0].text
            item['航班正常性'] = element.xpath('./td[8]/input/@value')[0]
            # item['始发正常性'] = element.xpath('./td[9]/input/@value')[0]
            # item['放行正常性'] = element.xpath('./td[10]/input/@value')[0]
            # print(item)
            item_list.append(item)
        print(f'当前{current_page}，总共{pages}页\n')
        return item_list,pages
    
def multi_page(CallSign,DepAP,ArrAP,start_day,end_day):
    html=get_flight_info(1,CallSign,DepAP,ArrAP,start_day,end_day)
    if "pagination" in html:
        item_lists,pages=paese_page(html)
        if int(pages)>=2:
            for page in range(2,int(pages)+1):
                html=get_flight_info(page,CallSign,DepAP,ArrAP,start_day,end_day)
                item_list=paese_page(html)[0]
                item_lists.extend(item_list)
        # print(item_lists)
        return item_lists
    
    
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
        if item['航班正常性'][:2]=='01':
            Reason[Reason1]+=1
        if item['航班正常性'][:2]=='02':
            Reason[Reason2]+=1
        if item['航班正常性'][:2]=='03':
            Reason[Reason3]+=1
        if item['航班正常性'][:2]=='04':
            Reason[Reason4]+=1
        if item['航班正常性'][:2]=='05':
            Reason[Reason5]+=1
        if item['航班正常性'][:2]=='06':
            Reason[Reason6]+=1
        if item['航班正常性'][:2]=='07':
            Reason[Reason7]+=1
        if item['航班正常性'][:2]=='08':
            Reason[Reason8]+=1
        if item['航班正常性'][:2]=='09':
            Reason[Reason9]+=1
        if item['航班正常性'][:2]=='10':
            Reason[Reason10]+=1
        if item['航班正常性'][:2]=='11':
            Reason[Reason11]+=1
            
    # print(Reason)
    return Reason
        
def flight_reason(CallSign,DepAP,ArrAP,start_day,end_day):
    item_lists=multi_page(CallSign,DepAP,ArrAP,start_day,end_day)
    if item_lists:
        reason=reason_count(item_lists)
        return reason
    
s=requests.Session()
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    
if __name__=="__main__":
    
    CallSign,DepAP,ArrAP,start_day,end_day='EU6662','ZSPD','ZUUU','2018-08-01','2018-08-30'
    login()
    # multi_page(CallSign,DepAP,ArrAP,start_day,end_day)
    flight_reason(CallSign,DepAP,ArrAP,start_day,end_day)
    
    
    
    
    