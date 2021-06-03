
import pandas as pd
import os
import urllib.parse
import PublicDataReader as pdr # 공공데이터(부동산)
import glob
import math
import numbers
import ast

test = "1111111111111"
print(test)
test2 = test
print(test2)
test = "111111222111111"
print(test)
print(test2)

link = "c:\\dev\\bigdata\\"
cc = link + "temp\\"
cr = link + "result\\"
res = link + "res\\"

donglist = pd.read_csv(res+'code_G1.csv', encoding="utf-8-sig")
print(donglist.to_string())

a = donglist[donglist['폐지여부']=="폐지"].index
donglist = donglist.drop(a)
print(donglist.to_string())

donglist.reset_index(drop=True,inplace=True)

donglist['code'] = 0
for i in range(len(donglist.index)):
    a = donglist.loc[i, '법정동코드']
    a = str(a)
    a = a[:5]
    donglist.loc[i, 'code'] = a
print(donglist)

# 5자리 코드가 같은 코드 하나만 남기고 삭제
donglist = donglist.drop_duplicates('code')
donglist.reset_index(drop=True, inplace=True)
print(donglist)

govkey = "aChH8Qt2QCyTJbd4Ull9aQZsjMDShkeAFGI6IsY1bA8VzKASfanujsvKt190YMGdSoHUhz8imsHU3%2BmF9cqKpA%3D%3D"

year = [202012, 202101, 202102] 
py_min = 72
py_max = 99

# API객체 만들기
AptTrade = pdr.Transaction(govkey)

## 해당 법정동 코드에 대한 거래내용 받아오기
for i in range(len(donglist.index)):
    for j in range(len(year)):
        a = str(donglist.loc[i, 'code'])
        b = str(year[j])

        # API데이터 요청/수신
        df = AptTrade.AptTradeDetail(a, b)

        # 어떤 형태로 받는지 확인
        print(df)
        
        if len(df.index) == 0:
            pass
        else:
            # 자료를 임시폴더에 csv파일로 저장
            df.to_csv(str(cc + "\\" + str(donglist.loc[i, '법정동명']) + str(b) + '.csv'), encoding='utf-8-sig')