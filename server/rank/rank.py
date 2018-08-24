# coding=UTF-8
import requests
import time
import calendar
from lxml import etree
import json
import os
import re
import csv

# from filter import rank_filter
# from filter import rank_Flight
# rank_filter(total_rank_dict,month)
# rank_Flight(rank,Flight)

# from draw import draw_pic
# draw_pic(x1,y1,filename) 
# x1,y1分别为x轴y轴的数值列表，filename为保存的文件名

def get_date(month=None):
    now_=time.localtime(time.time())
    now_year=now_.tm_year
    now_month=now_.tm_mon
    now_date=now_.tm_mday
    # print(now_year,now_month,now_date)
    year=now_year
    if not month:
        month=now_month
    elif int(month)>now_month:
        print('输入月有误')
        return None
    if month==now_month:
        if now_date==1:
            # max_day=now_date
            # 如果当日是1号，那么取当天的数据，便于少统计一个月
            month=now_month-1
            max_day=calendar.monthrange(year,month)[1]
            # print('本月数据还未统计，无法获取，查找上月数据')
        else:
            max_day=now_date-1
    else:
        max_day=calendar.monthrange(year,month)[1]
    # print(year,month,max_day)
    return year,month,max_day
        
        
    
def login():
    # token=get_token()
    login_url='http://fisc.variflight.com/v1/user/login'
    login_headers={
    'Origin':'http://fisc.variflight.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer':'http://fisc.variflight.com/fisc/index.html',
    }
    post_data={
    'LoginForm[username]':'cdhk',
    'LoginForm[password]':'cdhk2017'
    }
    login_rep= s.post(url=login_url,headers=login_headers,data=post_data)
    # print(login_rep.content)
    if login_rep.json()["message"]=='Success':
        print('登录成功')
        token=login_rep.json()["data"]
        print(login_rep.json())
        return token
    else:
        return None
    

    
    # 获取单个机场单个时间段的所有相关航班的排名
#def get_airport_day_rank(url,start_day,end_day,airport):
#    headers={
#    'Origin':'http://fisc.variflight.com',
#    'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
#    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
#    }
#    post_data={
#    'airport':airport,
#    'flightNumber':'EU',
#    'minNumber':'4',
#    'startDay':start_day,
#    'endDay':end_day,
#    'cancel':'1',
#    }
#    print(post_data)
#    rep=s.post(url,headers=headers,data=post_data)
#    if rep.status_code==200:
#        if rep.json()["message"]=='Success':
#            data=rep.json()["data"]
#            if type(data)==dict:
#                # print('dict')
#                return list(data.values())
#            elif type(data)==list:
#                # print('list')
#                return data
#            # else:
#                # print('000')
#    
#    
#    # 获取所有机场单个时间段的所有相关航班的排名
#def get_day_rank_list(url,airport_list,start_day,end_day):
#    rank_list=[]
#    for airport in airport_list:
#        rank=get_airport_day_rank(url,start_day,end_day,airport)
#        if rank:
#            rank_list.extend(rank)
#    rank_dict={}
#    rank_dict[end_day]=rank_list
#    # print(rank_dict)
#    return rank_dict
#    
#    
#def old_rank(file):
#    if os.path.isfile(file):
#    # file为之前日期生成的json文件，rank_data为新抓取的数据
#        with open(file,'r',encoding='utf-8') as fp:
#            old_data=json.load(fp)
#        return old_data
#    else:
#        return None
#    
#    
#def get_new_east_rank():
#    host="http://fisc.variflight.com"
#    url=host+"/v1/east/index?token="+token
#    file='east_rank_list.json'
#    total_rank_dict={}
#    
#    # 获取旧数据
#    old_rank_dict=old_rank(file)
#    if old_rank_dict:
#        # print(old_rank_dict)
#        old_rank_date=list(old_rank_dict.keys())
#        total_rank_dict.update(old_rank_dict)
#    else:
#        old_rank_date =''
#        
#    # 华东从上上月1号开始统计
#    start_month=str(month-2).zfill(2)
#    start_day=f'{year}-{start_month}-01'
#    stop_month=str(month).zfill(2)
#    for x in range(1,max_day+1):
#        x=str(x).zfill(2)
#        end_day=f'{year}-{stop_month}-{x}'
#        # print(end_day)
#        
#        if old_rank_date:
#            if end_day in old_rank_date:
#                # print(f'华东{end_day}已有数据')
#                pass
#            else:
#                print(f'华东{end_day}正在下载数据')
#                rank_dict=get_day_rank_list(url,east_airport,start_day,end_day)
#                total_rank_dict.update(rank_dict)
#        else:
#            print(f'华东{end_day}正在下载数据')
#            rank_dict=get_day_rank_list(url,east_airport,start_day,end_day)
#            total_rank_dict.update(rank_dict)
#            
#    with open(file,'w',encoding='utf-8') as fp:
#       json.dump(total_rank_dict,fp,ensure_ascii=False)
#    return total_rank_dict
#    
#    
#def get_new_aviation_rank():
#    host="http://fisc.variflight.com"
#    url=east_url=host+'/v1/aviation/index?token='+token
#    file='aviation_rank_list.json'
#    total_rank_dict={}
#    
#    # 获取旧数据
#    old_rank_dict=old_rank(file)
#    if old_rank_dict:
#        # print(old_rank_dict)
#        old_rank_date=list(old_rank_dict.keys())
#        total_rank_dict.update(old_rank_dict)
#    else:
#        old_rank_date =''
#    
#    # 全国从本月1号开始统计
#    month_=str(month).zfill(2)
#    start_day=f'{year}-{month_}-01'
#    for x in range(1,max_day+1):
#        x=str(x).zfill(2)
#        end_day=f'{year}-{month_}-{x}'
#        # print(end_day)
#        if old_rank_date:
#            if end_day in old_rank_date:
#                # print(f'总局{end_day}已有数据')
#                pass
#            else:
#                print(f'总局{end_day}正在下载数据')
#                rank_dict=get_day_rank_list(url,aviation_airport,start_day,end_day)
#                total_rank_dict.update(rank_dict)
#                with open(file,'w',encoding='utf-8') as fp:
#                    json.dump(total_rank_dict,fp,ensure_ascii=False)
#                
#        else:
#            print(f'总局{end_day}正在下载数据')
#            rank_dict=get_day_rank_list(url,aviation_airport,start_day,end_day)
#            total_rank_dict.update(rank_dict)
#            with open(file,'w',encoding='utf-8') as fp:
#                json.dump(total_rank_dict,fp,ensure_ascii=False)
#               
#    return total_rank_dict
#    
#    
#    # 取得某个月排名在倒数后30以内的排名数据,及航班数据
#def rank_filter(total_rank_dict,month):
#    rank_list=list(total_rank_dict.values())
#    
#    rank_30=[y for x in rank_list for y in x if int(y["Rank"])<=60 and int(y['date'][-5:-3])==month]
#    Flight_list=set([x.get('Flight')for x in rank_30])
#    # print(rank_30)
#        
#    return rank_30,Flight_list
#    
#    
#    # 取某个航班的排名数据
#def rank_Flight(rank,Flight):
#    sort_date=[]
#    sort_rank=[]
#    
#    airport_rank=[x for x in rank if x['Flight']==Flight]
#    # for x in airport_rank:
#        # print(x)
#
#    # 日期列表
#    date_list=[x.get('date')[-2:] for x in airport_rank] # 字符串
#    
#    sort_date=sorted([int(x) for x in date_list]) # 整型
#    
#    # 排名列表
#    sort_rank=[int(x.get('Rank'))for x in airport_rank for y in date_list if x['date'][-2:]==y]
#    # for x in airport_rank:
#        # for y in date_list:
#            # if x['date'][-2:]==y:
#                # sort_rank.append(x.get('Rank')
#    print(sort_date)
#    print(sort_rank)
#    return sort_date,sort_rank
#    
#def today_rank(sort_date,sort_rank):
#    # print(max_day,sort_date[-1])
#    if sort_date[-1]==max_day:
#        return sort_rank[-1]
#    
         
if __name__=='__main__':
    aviation_airport=[
    "ZBAA","ZSPD","ZGGG","ZUUU","ZPPP","ZGSZ","ZSSS","ZLXY","ZUCK","ZSHC",
    "ZSAM","ZSNJ","ZGHA","ZHHH","ZHCC","ZSQD","ZWWW","ZBTJ","ZJHK"
    ]
    east_airport=["ZSPD","ZSSS","ZSNJ","ZSHC","ZSAM","ZSQD","ZSFZ","ZSNT"]
    s=requests.Session()
    token=login()
    print(token)

    set_month=''
    # set_month=input('输入需要的月份，不输入则为当月,按回车确认:\n')
    if set_month:
        set_month=int(set_month)
    year,month,max_day=get_date(set_month)



        

    
    
    
