
#####  부동산 데이터수집 및 분석하기 학습용
'''
(목표) 본 교육의 외부로부터 부동산 데이터를 수집하여 이를 파이썬으로 분석하기 위한 분석기법을 학습하는 것이다.

(학습 주제) 본 과정의 학습은 아래의 주제 별로 코드 작업 및 산출물을 획득한다.

    ● 부동산 거래금액의 시각화
    ● 인근 저가 부동산 탐색
    ● 지역별 수익률 분석
    ● 지역별 GAP 분석
    ● 지역별 전·월세 변환률 분석

(진행 방식) 각 주제별 학습은 아래의 순서대로 진행한다.

    1. 사전준비: 파이썬 설치, 공공데이터포털 인증키 신청(아파트 거래가격, 아파트 전월세가격, 공시지가 등), 브이월드 주소별 좌표정보 인증키 신청
    2. 원하는 지역의 코드(서울시만 대상으로 함) 획득 (행정표준코드 관리시스템_법정동코드 전체자료 다운로드)
    3. 결과 저장폴더, 중간 임시폴더(필요성, 생성모듈) 생성, 지정(모듈OS)
    4. API요청, 수신자료 이해(외부 모듈 다운로드_PublicDataReader)
    5. 데이터(CSV)의 가공
    6. 데이터 가공을 위한 templete 구상(모듈Pandas, DataFrame, DF 이용 함수 이해)

'''

##### 2. 데이터 수집하기
##### (1) 서울시 법정동 코드 가져오기
#!pip install PublicDataReader

import pandas as pd
import os
import urllib.parse
import PublicDataReader as pdr # 공공데이터(부동산)
import glob
import math
import numbers
import ast

##문서읽기  https://github.com/WooilJeong/PublicDataReader 

link = "c:\\dev\\PublicDataReader\\"
cc = "c:\\dev\\PublicDataReader\\temp\\"
cr = "c:\\dev\\PublicDataReader\\result\\"
res = "c:\\dev\\PublicDataReader\\res\\"

# 다운로드 받은 법정동코드 txt자료를 엑셀에서 불러와 구분기호로 자르고 csv파일로 저장함(영문이름)
donglist = pd.read_csv(res+'code_G1.csv', encoding="utf-8-sig")

# 서울특별시 강남3구만을 대상으로 하기
a = donglist[donglist['폐지여부']=="폐지"].index
donglist = donglist.drop(a)
print(len(donglist.index))

# 폐지된 행 숫자가 사라져 있으므로 오류 가능성을 줄이기 위해 리스트 리셋
donglist.reset_index(drop=True,inplace=True)

# 공공데이터포털에 이용하기 위한 코드 분리(코드 앞 5자리)작업
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


##### 4. API자료 수신 실습
##### (1) 공공데이터포털
# 공공데이터포털 자료는 XML로 수신하는데 이에 대해 자세히 배우고싶으면 구글에 정말 잘 나와있음, 여기에서는 다른사람이 만든 모듈 이용

# 기본 정보 셋팅
govkey = "aChH8Qt2QCyTJbd4Ull9aQZsjMDShkeAFGI6IsY1bA8VzKASfanujsvKt190YMGdSoHUhz8imsHU3%2BmF9cqKpA%3D%3D"

year = [202102] # 공공데이터포털 안내문에 요청자료 참고
# 30평대의 전용면적은 72~99제곱미터
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

##### 5. csv데이터의 합체
## 임시폴더에 저장된 csv자료 확인하고 합치기
input_path = str(cc + "\\")
output_file = str(cr + "\\trade_data.csv")

all_files = glob.glob(os.path.join(input_path, '*'))
all_data_frames = []

for file in all_files:
    data_frame = pd.read_csv(file, index_col=None, engine='python', encoding='utf-8-sig')
    all_data_frames.append(data_frame)

data_frame_concat = pd.concat(all_data_frames, axis=0, ignore_index=True)
data_frame_concat.reset_index(drop=True, inplace=True)
data_frame_concat.to_csv(output_file, index=False, encoding='utf-8-sig')

# 결과 저장파일 불러오기
trad = pd.read_csv(str(cr + "\\trade_data.csv"), encoding='utf-8-sig')
trad.reset_index(drop=True,inplace=True)


##### 6. 데이터의 가공
# 데이터 분석을 위해 면적기준으로 1차 소팅, 같은 단지 내 여러개의 거래금액을 평균내어서 이용

# 데이터 분석을 위해 면적별로 데이터
trad_test = pd.DataFrame(data=trad)

# 범위 외 면적 버리기
a = trad_test[trad_test['전용면적'] < py_min].index
trad_test = trad_test.drop(a)
a = trad_test[trad_test['전용면적'] > py_max].index
trad_test = trad_test.drop(a)

# 인덱스 리셋
trad_test.reset_index(drop=True, inplace=True)

# 면적 소팅된 자료 저장
trad_test.to_csv(str(cr + "\\trad_result(area).csv"), encoding='utf-8-sig')


# 주소를 브이월드에서 검색가능하도록 합치기
for i in range(len(trad_test.index)):
    a = str(trad_test.loc[i, '법정동']) + " " + str(trad_test.loc[i, '지번'])
    trad_test.loc[i, '주소'] = a
trad_test.reset_index(drop=True, inplace=True)


# 주소를 좌표로 넣기
for i in range(len(trad_test.index)):
    address = trad_test.loc[i, '주소']
    ApiKey = "65D4F499-6461-32DB-BA23-D419124165D6"  # 브이월드 국가지도api
    apiUrl = 'http://api.vworld.kr/req/address?service=address&request=getCoord&key=' + ApiKey + '&'
    values = {'address': address, 'type': 'PARCEL'}
    param = urllib.parse.urlencode(values)

    Adding = apiUrl + param

    req = urllib.request.Request(Adding)
    res = urllib.request.urlopen(req)

    respon_data = res.read().decode()
    DataDict = ast.literal_eval(respon_data)
    v_check = DataDict['response']['status']
    print(i,"/",len(trad_test.index),"_",address)

    try:
        result = DataDict['response']['result']['point']
        trad_test.loc[i, 'x'] = result['x']
        trad_test.loc[i, 'y'] = result['y']
    except:
        pass

trad_test = trad_test.sort_values(by='거래금액', ascending=False)
trad_test.to_csv(str(cr+"\\trad_xy.csv"),encoding='utf-8-sig')


######### [추가학습: 데이터분석] 인근 저평가 아파트 찾기
'''
부동산 실거래가 리스트를 가지고 인근 범위 내 아파트 중에서 기준률 이하의 아파트를 찾아보기
'''

기준거리 = 0.5 #단위는 km
가격cut = 0.3 #단위는 비율

# 좌표가 표시된 거래자료 가져오기
trad_test = pd.read_csv(str(cr+"\\trad_xy.csv"), encoding="utf-8-sig", index_col=0)
trad_test = trad_test.reset_index(drop=True)
trad_test = trad_test.fillna(0)
print("분 시작")

# class 이해하기
class GeoUtil:
    @staticmethod
    def degree2radius(degree):
        return degree * (math.pi / 180)

    @staticmethod
    def get_harversion_distance(x1, y1, x2, y2, round_decimal_digits=5):
        """
        경위도 (x1,y1)과 (x2,y2) 점의 거리를 반환
        Harversion Formula 이용하여 2개의 경위도간 거래를 구함(단위:Km)
        """
        if x1 is None or y1 is None or x2 is None or y2 is None:
            return None
        assert isinstance(x1, numbers.Number) and -180 <= x1 and x1 <= 180
        assert isinstance(y1, numbers.Number) and -90 <= y1 and y1 <= 90
        assert isinstance(x2, numbers.Number) and -180 <= x2 and x2 <= 180
        assert isinstance(y2, numbers.Number) and -90 <= y2 and y2 <= 90

        R = 6371  # 지구의 반경(단위: km)
        dLon = GeoUtil.degree2radius(x2 - x1)
        dLat = GeoUtil.degree2radius(y2 - y1)

        a = math.sin(dLat / 2) * math.sin(dLat / 2) \
            + (math.cos(GeoUtil.degree2radius(y1)) \
               * math.cos(GeoUtil.degree2radius(y2)) \
               * math.sin(dLon / 2) * math.sin(dLon / 2))
        b = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * b, round_decimal_digits)

#저평가 아파트 찾으면 적어둘 DF
list = pd.DataFrame()
for i in range(len(trad_test.index)):
    print(trad_test.loc[i,'아파트'])
    x_1 = float(trad_test.loc[i,'x'])
    y_1 = float(trad_test.loc[i,'y'])

    a = pd.DataFrame()
    a = trad_test
    a['거리'] = 0
    a = a.fillna(0)

    for j in range(len(a.index)):
        x_2 = float(a.loc[j, 'x'])
        y_2 = float(a.loc[j, 'y'])
        #print(x_1,y_1,x_2,y_2)
        a.loc[j,'거리'] = GeoUtil.get_harversion_distance(x_1, y_1, x_2, y_2)

    b = a[a['거리'] > 기준거리].index
    a = a.drop(b)
    a.reset_index(inplace = True, drop = True)
    k = a['거래금액'].idxmin()

    price1 = trad_test.loc[i,'거래금액']
    price2 = a.loc[k,'거래금액']
    d = (price1-price2)/price1
    
    if d > 가격cut:
        b = a[a.index !=k].index
        a = a.drop(b)
        list = pd.concat([list,a])
        print(list)
    else: pass

b = list[list['거리'] == 0].index
list = list.drop(b)
list.reset_index(drop=True, inplace=True)

list.to_csv(str(cr+"\\lowprice_result.csv"), encoding = "utf-8-sig")