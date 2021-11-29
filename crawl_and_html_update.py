#!/usr/bin/env python
# coding: utf8

import os
import sys
import datetime
import urllib.request
import time
import traceback
from bs4 import BeautifulSoup as bs
from netlify_py import NetlifyPy


sys.path.append("C:\\ProgramData\\Anaconda3\\Lib\\site-packages")
import MOD_common as cm
import MOD_http as http

'''
To do list
    index.html
        V- 확진자 수 crawling
        - 매일 html 업데이트
        
    py
        - netlify 자동 deploy 
        - 에러나면 메일 전송
'''


############# parameters ################
tag_address_full = 'div.occurrenceStatus > div.occur_graph > table.ds_table > tbody > tr > td > span'
idx = 3
list_del_str = ["<span>", "</span>"]


url = "http://ncov.mohw.go.kr/"
#url = "http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=11&ncvContSeq=&contSeq=&board_id=&gubun="
#type = "span"
#list_ClassName = ["before"]
dirname_Proj = "OverseasArrivals_CovidGuide"
fname_Html = "index.html"

#########################################



def main():
    ###### init para ######


    flag_Changed_Day = False
    flag_Changed_ConfirmedCase = False

    # old day 준비
    now_Tmp = datetime.datetime.now()
    old_Day = now_Tmp.day
    
    # old_ConfirmedCase 준비
    #old_ConfirmedCase = http.crawl_table(url, type, list_ClassName)
    #old_ConfirmedCase = old_ConfirmedCase[0]
    #old_ConfirmedCase = old_ConfirmedCase.replace("전일대비 (+ ", "").replace(")", "")
    old_ConfirmedCase = http.crawl_address_full(url, tag_address_full, idx, list_del_str)


    # 코드 바꿀 html 경로
    path_Html = os.path.join(current_path, dirname_Proj, fname_Html)

    while True:
        
        # 년, 일, 월 얻기
        now = datetime.datetime.now()
        now_Year    = now.year
        now_Month   = now.month
        now_Day     = now.day
        now_Hour    = now.hour
        now_Min     = now.minute
        cm.print_and_log('i', logger, f"{now_Year}-{now_Month}-{now_Day} {now_Hour}:{now_Min}")

        ######################################################
        ####################### 크롤링 ########################
        ######################################################
        try:
            #num_ConfirmedCase = http.crawl(url, type, list_ClassName)
            #df_table = http.crawl_table_to_df(url, "ds_table", 0)
            num_ConfirmedCase = http.crawl_address_full(url, tag_address_full, idx, list_del_str)
            num_ConfirmedCase = int(num_ConfirmedCase)
            cm.print_and_log('i', logger, f"num_ConfirmedCase: {num_ConfirmedCase}")
            # 전일대비 (+ 1219) => 1219
            #num_ConfirmedCase = num_ConfirmedCase.replace("전일대비 (+ ", "").replace(")", "")

        except ValueError:
            cm.print_and_log('e', logger, "Failed crawling in the website")
            # send_Alarm()
            assert(False)
        except Exception as e:
            cm.print_and_log('e', logger, e)
            # send_Alarm()
            assert(False)


        ######################################################
        ############ index.html 확진자 수 반영 ################
        ######################################################

        # 주의: 
        #   크롤링 결과와 날짜가 동시에 바뀌지 않을 수 있다.
        #   하나 바뀌면 flag 올리기 -> 또 다른 하나가 마저 바뀌면 flag 올리기 -> 두개 flag &
        #   if (flag & 결과) 업데이트 실행
        #     업데이트 끝나면 둘 다 False 만들기
        # 이렇게 하는 이유:
        #   매분 index.html 다시 쓰지 않도록 하기 위함
        if old_Day != now_Day:
            flag_Changed_Day = True
            cm.print_and_log('i', logger, "Day is changed")
        if old_ConfirmedCase != num_ConfirmedCase:
            flag_Changed_ConfirmedCase = True
            cm.print_and_log('i', logger, "The number of Confirmed case is updated")

        # 날짜가 바뀌고, 크롤링 결과가 둘 다 달라지면
        if flag_Changed_Day and flag_Changed_ConfirmedCase:

            cm.print_and_log('i', logger, f"Updating \"{fname_Html}\"")

            # html에서 text 바꿀 내용 설정
            line_Replace = f'          <h4 class="heading">{now_Year}년 {now_Month}월 {now_Day}일 기준<br>신규 확진자 수: {num_ConfirmedCase}</h4>\n'
            word_Search = "신규 확진자 수"

            # html 파일 로딩
            try:
                cm.print_and_log('i', logger, f"Loading \"{fname_Html}\"")
                fr = open(path_Html, 'r', encoding = "UTF-8")
                lines = fr.readlines()
                for i, line in enumerate(lines):
                    # 키워드 찾아지면 line 교체
                    if word_Search in line:
                        cm.print_and_log('i', logger, f"Found line with keyword \"{word_Search}\"")
                        lines[i] = line_Replace
                        break
                cm.print_and_log('i', logger, f"Context of \"{word_Search}\" is ready")
                # 여기까지 오면 새로운 index.html 내용 준비됨

                # index.html 쓰기
                cm.print_and_log('i', logger, f"Writing new \"{fname_Html}\"")
                with open(path_Html, 'w', encoding = 'UTF-8') as fw:
                    fw.writelines(lines)
                cm.print_and_log('i', logger, f"Writing new \"{fname_Html}\" Completed")

            except Exception as e:
                cm.print_and_log('e', logger, e)
                # send_Alarm()
                assert(False)

            cm.print_and_log('i', logger, f"Updating \"{fname_Html}\" Completed")


            # Netlify deploy
                


                # 성공하면 진행




                # 실패하면 log 남기고 메일 보내기


            

            # 업데이트 성공하면 flag 되돌리기
            flag_Changed_Day = False
            flag_Changed_ConfirmedCase = False

        old_Day = now_Day
        old_ConfirmedCase = num_ConfirmedCase
        time.sleep(10800)  # 3시간마다 refresh


if __name__ == "__main__":
    
    # log 초기화
    current_path = os.getcwd()
    logger = cm.init_logger(current_path)
    main()
