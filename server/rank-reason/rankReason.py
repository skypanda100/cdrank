import requests
import time
import calendar
import json
import os
import re
import csv

from acount import vf_user,vf_pwd
from UnnormalReasonCount import flight_reason
# flight_reason(CallSign,DepAP,ArrAP,start_day,end_day)

def get_date(month=None):
    now_=time.localtime(time.time())
    now_year=now_.tm_year
    now_month=now_.tm_mon
    now_date=now_.tm_mday
    now_hour=now_.tm_hour
    # print(now_year,now_month,now_date)
    year=now_year
    if not month:
        month=now_month
    elif int(month)>now_month:
        print('输入月有误')
        return None
    if month==now_month:
        if now_date==1:
            # 1号选定日期为上月，最后一天
            month=now_month-1
            max_day=calendar.monthrange(year,month)[1]
            # print('本月数据还未统计，无法获取，查找上月数据')
            if now_hour<17:
                # 1号1700前选定日期为上月，倒数第二天
                max_day=max_day-1
        elif now_date==2:
            # 2号1700前，选定日期为上月最后一天
            if now_hour<17:
                month=now_month-1
                max_day=max_day=calendar.monthrange(year,month)[1]
            else:
                max_day=now_date-1
        else:
            max_day=now_date-1
            if now_hour<17:
                max_day=max_day-1
    else:
        max_day=calendar.monthrange(year,month)[1]
    # print(year,month,max_day)
    return year,month,max_day
        
        
    
def login(n=0):
    login_url='http://fisc.variflight.com/v1/user/login'
    post_data={
    'LoginForm[username]':vf_user,
    'LoginForm[password]':vf_pwd
    }
    login_rep= s.post(url=login_url,headers=headers,data=post_data)
    # print(login_rep.content)
    if login_rep.json()["message"]=='Success':
        print('飞常准登录成功\n')
        token=login_rep.json()["data"]
        return token
    else:
        while n<3:
            n=+1
            return login(n)
    
    # 获取单个机场单个时间段的所有相关航班的排名
def get_airport_day_rank(url,start_day,end_day,airport):
    if end_day[8:]=='01':
        minNumber=1
    else:
        minNumber=2
    post_data={
    'airport':airport,
    'flightNumber':'EU',
    'minNumber':minNumber,
    'startDay':start_day,
    'endDay':end_day,
    'cancel':'1',
    }
    # print(post_data)
    rep=s.post(url,headers=headers,data=post_data)
    if rep.status_code==200:
        if rep.json()["message"]=='Success':
            data=rep.json()["data"]
            if type(data)==dict:
                # print(list(data.values()),'\n')
                return list(data.values())
            elif type(data)==list:
                # print(data,'\n')
                return data
                
# 添加原因模块，筛选排名
def rank_add_reason(url,start_day,end_day,airport):
    new_rank_list=[]
    rank_list=get_airport_day_rank(url,start_day,end_day,airport)
    if rank_list:
        for x in rank_list:
            if x['ranking']<=60: #取排名60以内的数据
                x['startDay']=start_day
                x['endDay']=end_day
                x['flight']=f"{x['fnum']} {x['forg']}-{x['fdst']}"
                
                if 'aviation' in url: #仅全国航班统计原因
                    CallSign=x['fnum']
                    DepAP=x['forg']
                    ArrAP=x['fdst']
                    reason=flight_reason(CallSign,DepAP,ArrAP,start_day,end_day)
                    if reason:
                        x.update(reason)
                        new_rank_list.append(x)
                else:
                    new_rank_list.append(x)
                    
    # print(new_rank_list)
    return new_rank_list
    
    # 遍历机场
def get_day_rank_list(url,airport_list,start_day,end_day):
    rank_dict={}
    rank_list=[]
    for airport in airport_list:
        # rank=get_airport_day_rank(url,start_day,end_day,airport)
        rank=rank_add_reason(url,start_day,end_day,airport)
        if rank:
            rank_list.append(rank)
    rank_dict[end_day]=rank_list
    # print(rank_list,'\n')
    # print(rank_dict)
    return rank_dict
    
def old_rank(file):
    if os.path.isfile(file):
    # file为之前日期生成的json文件，rank_data为新抓取的数据
        with open(file,'r',encoding='utf-8') as fp:
            old_rank_data=json.load(fp)
            old_rank_date=list(old_rank_data)
        return old_rank_data,old_rank_date
    else:
        return '',''
            
class New_rank():
    '''
    全局变量：
        east_airport,aviation_airport
        token
        year,month,max_day,target_day
    '''
    def __init__(self,tag):
        self.host="http://fisc.variflight.com"
        self.tag=tag
        if tag=='East':
            self.url=self.host+"/v1/east/index?token="+rank_token
            self.file='/usr/share/nginx/html/data/east_rank_list.json'
            self.airport_list=east_airport
            self.start_month=str(month-2).zfill(2)# 华东从上上月1号开始统计
            
            
        if tag=='Aviation':
            self.url=self.host+"/v1/aviation/index?token="+rank_token
            self.file='/usr/share/nginx/html/data/aviation_rank_list.json'
            self.airport_list=aviation_airport
            self.start_month=str(month).zfill(2)# 全国从当月1号开始统计
            
        self.stop_month=str(month).zfill(2)
        self.start_day=f'{year}-{self.start_month}-01'
   
        
    def get_new_rank(self):
        total_rank_list={}
        # 获取旧数据
        old_rank_data,old_rank_date=old_rank(self.file)
        if old_rank_data:
            total_rank_list.update(old_rank_data)
        # 获取新数据
        for x in range(1,max_day+1):
            x=str(x).zfill(2)
            end_day=f'{year}-{self.stop_month}-{x}'
            if end_day not in old_rank_date:
                print(f'正在下载{end_day}_{self.tag}数据')
                rank_list=get_day_rank_list(self.url,self.airport_list,self.start_day,end_day)
                total_rank_list.update(rank_list)
                with open(self.file,'w',encoding='utf-8') as fp:
                    json.dump(total_rank_list,fp,ensure_ascii=False)
        return total_rank_list
        
    def get_month_rank(self):
        total_rank_list={}
        file='/usr/share/nginx/html/data/east_month_rank.json'
        old_rank_data=old_rank(file)[0]
        if old_rank_data:
            total_rank_list.update(old_rank_data)
        for m in [month-2,month-1,month]:
            start_date1=f'{year}-{str(m).zfill(2)}-01'
            stop_day1=calendar.monthrange(year,m)[1]
            stop_date1=f'{year}-{str(m).zfill(2)}-{stop_day1}'
            print(start_date1,stop_date1)
            rank_list=get_day_rank_list(self.url,self.airport_list,start_date1,stop_date1)
            total_rank_list.update(rank_list)
            with open(file,'w',encoding='utf-8') as fp:
                json.dump(total_rank_list,fp,ensure_ascii=False)
        
'''
    
    # 取得当日航班及当月数据
def rank_filter(total_rank_dict,month):
    total_rank_list=list(total_rank_dict.values())
    total_rank_list=[y for x in total_rank_list for y in x]
    # for x in total_rank_list:
        # print(x,'\n\n')
    Flight_list=set([x.get('flight')for x in total_rank_list if x.get('endDay')==target_day])
    Rank_list=[x for x in total_rank_list if x.get('endDay')[5:7]==str(month).zfill(2)]
    return Flight_list,Rank_list
    
    
    # 取某个航班的月排名数据
def rank_Flight(Rank_list,Flight):
    flight_rank=[x for x in Rank_list if x.get('flight')==Flight]
    # 日期列表
    date_list=[x.get('endDay') for x in flight_rank] # 字符串
    sort_date=sorted((x[8:] for x in date_list)) # 字符串
    # 排名列表
    sort_rank=[x.get('ranking')for x in flight_rank for y in date_list if x['endDay']==y]
    
    sort_date=[int(x) for x in sort_date]
    sort_rank=[int(x) for x in sort_rank]
    print(sort_date)
    print(sort_rank)
    return sort_date,sort_rank
    
    
def rank_csv(rank_all_dict,rank_type):
    os.makedirs('data',exist_ok=True)
    if rank_type=='East':
        rate_type='departRate'
    elif rank_type=='Aviation':
        rate_type='normalRate'
        
    for date,data in rank_all_dict.items():
        data_list=[]
        for x in data:
            rank_data=[x['flight'],x['ranking'],'{:.1%}'.format(x.get(rate_type))]
            data_list.append(rank_data)
            sortedlist = sorted(data_list, key = lambda x: (int(x[1])))
        file_name=f'data\\{rank_type}_{date}.csv'
        if not os.path.isfile(file_name):
            with open(file_name,'a',encoding='utf-8',newline='')as fp:
                writer =csv.writer(fp)
                writer.writerow(('航班','排名','正常率'))
                writer.writerows(sortedlist)
'''
                
s=requests.Session()
headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
rank_token=login()

aviation_airport=[
"ZBAA","ZSPD","ZGGG","ZUUU","ZPPP","ZGSZ","ZSSS","ZLXY","ZUCK","ZSHC",
"ZSAM","ZSNJ","ZGHA","ZHHH","ZHCC","ZSQD","ZWWW","ZBTJ","ZJHK"]

east_airport=["ZSPD","ZSSS","ZSNJ","ZSHC","ZSAM","ZSQD","ZSFZ"]
    
if __name__=='__main__':
    
    
    set_month=''
    # set_month=input('输入需要的月份，不输入则为当月,按回车确认:\n')
    if set_month:
        set_month=int(set_month)
    year,month,max_day=get_date(set_month)
    target_day=f'{year}-{str(month).zfill(2)}-{str(max_day).zfill(2)}'
    # with open('update','w') as f:
        # f.write(target_day)
    print(target_day,'\n')
    if rank_token:
        # host="http://fisc.variflight.com"
        # url=host+"/v1/east/index?token="+token
        # get_day_rank_list(url,east_airport,start_day,end_day)
        east_rank_all=New_rank('East').get_new_rank()
        east_rank_all=New_rank('East').get_month_rank()
        
        aviation_rank_all=New_rank('Aviation').get_new_rank()
        
        
        # rank_csv(aviation_rank_all,'Aviation')
        # rank_csv(east_rank_all,'East')
        
        # east_Flight_list,east_Rank=rank_filter(east_rank_all,month)
        # for east_Flight in east_Flight_list:
            # print('\n华东',east_Flight)
            # sort_date,sort_rank=rank_Flight(east_Rank,east_Flight)
            # draw_pic(sort_date,sort_rank,'East_'+east_Flight+'.png',east_Flight)
            # sort_date=sort_rank=None
        
        # print("\n\n")
        # aviation_Flight_list,aviation_Rank=rank_filter(aviation_rank_all,month)
        # for aviation_Flight in aviation_Flight_list:
            # print('\n总局',aviation_Flight)
            # sort_date,sort_rank=rank_Flight(aviation_Rank,aviation_Flight)
            # draw_pic(sort_date,sort_rank,'Aviation_'+aviation_Flight+'.png',aviation_Flight)
            # sort_date=sort_rank=None
        
        
        

    
    
    
