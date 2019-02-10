# 오픈 라이브러리
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
client = MongoClient()
from datetime import datetime, timedelta
import requests
import json
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)

## 시각화
import pandas as pd
pd.set_option('display.float_format', '{:.2f}'.format)
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', family='AppleGothic')
from pandas.plotting import table
import matplotlib
matplotlib.style.use('ggplot')


# 나의 라이브러리
import __pymongo as mg
import __list as lh
import debugger as dbg


# 프로젝트 라이브러리
from __lib__ import *
db = client[DB]

# 전역변수
원화기준환율_컬럼순서 = ['날짜','KRW_EUR','KRW_GBP']




def 타화폐_컬럼을_KRW로_환산(df, 환율계산컬럼_li=['입금','출금','잔액'], 타화폐단위='EUR', 날짜컬럼명='거래일시'):
    print('\n'+'='*60+inspect.stack()[0][3])
    df = df.assign(거래일= lambda x: x['거래일시'] )
    df['거래일'] = df['거래일'].apply(lambda x: x.date())

    df1 = 단위화폐당_원화환율_로딩(True)
    df1['날짜'] = df1['날짜'].apply(lambda x: x.date())
    df = df.join(df1.set_index('날짜'), on='거래일')
    del(df['거래일'])

    for col in 환율계산컬럼_li:
        df[col] = df[col] * df[타화폐단위]
    del(df[타화폐단위])

    return df




def 업뎃수집할_최근날짜li():
    최종저장날짜 = sorted(db['단위화폐당_원화환율'].distinct('날짜'), reverse=True)[0]
    수집할_최근날짜_li = sorted(pd.date_range(start=최종저장날짜+timedelta(days=+1), end=datetime.now()+timedelta(days=-1)))
    pp.pprint({
        inspect.stack()[0][3]:{'수집할_최근날짜_li':수집할_최근날짜_li}
    })
    return 수집할_최근날짜_li

def 원화환율로_변환할_날짜li():
    기준환율_날짜li = list( db['USD기준환율'].distinct('날짜') ) + list( db['EUR기준환율'].distinct('날짜') )
    기준환율_날짜li = sorted(기준환율_날짜li)

    원화환율_날짜li = list( db['단위화폐당_원화환율'].distinct('날짜'))

    변환할_원화환율_날짜li = lh.리스트1로부터_리스트2를_제거(기준환율_날짜li, 원화환율_날짜li)
    pp.pprint({
        inspect.stack()[0][3]:{'변환할_원화환율_날짜li':변환할_원화환율_날짜li}
    })
    return 변환할_원화환율_날짜li

def 원하는_수집날짜li(시작_isostr, 종료_isostr):
    원하는_수집날짜li = sorted(pd.date_range(start=시작_isostr, end=종료_isostr))

    원화환율_날짜li = list( db['단위화폐당_원화환율'].distinct('날짜'))

    원하는_수집날짜li = lh.리스트1로부터_리스트2를_제거(원하는_수집날짜li, 원화환율_날짜li)
    pp.pprint({
        inspect.stack()[0][3]:{'원하는_수집날짜li':원하는_수집날짜li}
    })
    return 원하는_수집날짜li

def fixer_환율_수집(date_isostr):
    try:
        r = requests.get('http://data.fixer.io/api/'+date_isostr+'?access_key=ca4eb3c29ccb1cebba1f84caae5d75f9')
    except Exception as e:
        db.errlog.insert_one({
            '함수명':inspect.stack()[0][3],
            '입력':{'date_str':date_isostr},
            '출력':e,
            '발생일시':datetime.now() })
        r = None
    finally:
        return r

def 기준환율_수집후_저장(수집할날짜_li):
    if len(수집할날짜_li) == 0:
        pass
    else:
        for 날짜 in 수집할날짜_li:
            date_isostr = 날짜.isoformat()[0:10]

            # 수집
            r = fixer_환율_수집(date_isostr)

            # 파싱
            if r.status_code == 200:
                js = r.json()
                if r.json()['success'] == True:
                    js = r.json()
                    기준화폐 = js['base']
                    df = pd.DataFrame(js)
                    df['화폐'] = df.index
                    df = df.rename(columns={'rates':'환율','date':'날짜'})
                    df = df.reindex(columns=['날짜','화폐','환율'])
                    df['날짜'] = df['날짜'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
            # 저장
                    tbl명 = 기준화폐+'기준환율'
                    db[tbl명].insert_many(df.to_dict('records'))
                else:
                    human_requests_r_확인(r)
            else:
                human_requests_r_확인(r)

        # 백업
        mg.테이블의_백업csv_생성(db, tbl명, data_path)

def 단위화폐당_원화환율로_변환후_저장(날짜_li, 기준환율_tbl명='EUR기준환율'):
    tbl명 = '단위화폐당_원화환율'

    df = pd.DataFrame(list( db[기준환율_tbl명].find({'날짜':{'$in':날짜_li}}) ))
    if len(df)==0:
        pass
    else:
        pvt = pd.pivot_table(df, index='날짜', columns='화폐', values='환율')
        for col in pvt:
            if col == 'KRW':
                pass
            else:
                pvt[col] = pvt['KRW'] / pvt[col]
        pvt = pvt.rename(columns={'KRW':'USD'})

        #__저장, 백업
        pvt['날짜'] = pvt.index
        db[tbl명].insert_many(pvt.to_dict('records'))
        mg.테이블의_백업csv_생성(db, tbl명, data_path)

def 기준환율_수집_원화환율_변환(최근날짜=True, 시작종료_isostr_tpl=None):
    if 최근날짜 == True:
        날짜_li = 업뎃수집할_최근날짜li()
    else:
        날짜_li = 누락된_원화환율_날짜li()
    if 시작종료_isostr_tpl != None:
        날짜_li = 원하는_수집날짜li('2014-01-01', '2015-12-31')


    if len(날짜_li) == 0:
        pass
    else:
        #return 날짜_li
        기준환율_수집후_저장(날짜_li)
        #return pd.DataFrame(list( db['EUR기준환율'].find({'날짜':{'$in':날짜_li}}) ))
        단위화폐당_원화환율로_변환후_저장(날짜_li)

def 단위화폐당_원화환율_로딩(하나은행_송금환율적용=False):
    print('\n'+'='*60+inspect.stack()[0][3])
    기준환율_수집_원화환율_변환()
    df = pd.DataFrame(list( db['단위화폐당_원화환율'].find({}, {'_id':False}).sort('날짜',ASCENDING) ))

    if 하나은행_송금환율적용 == True:
        df = df.loc[:,['날짜','EUR']]
        df.index = df['날짜']
        del(df['날짜'])

        df1 = 하나은행_해외송금환율_기준으로_단위화폐당_원화환율_로딩()
        df1.index = df1['날짜']
        del(df1['날짜'])

        df.update(df1)
        df['날짜'] = df.index
        df.index = range(len(df))
    else:
        pass
    return df

def 하나은행_해외송금환율_기준으로_단위화폐당_원화환율_로딩():
    df = pd.DataFrame(list(db.하나은행_해외송금_환율.find({},{'_id':False})))

    li = list(db['하나은행_해외송금_환율'].find({},{'_id':False}))
    li.append({'날짜':str(datetime.today())[0:10]})

    df_li = []
    for i in range(len(li)-1):
        start = li[i]['날짜']
        next_start = li[i+1]['날짜']
        next_start = pd.Period(next_start, freq='D')
        end = str(next_start -1)

        df = pd.DataFrame({'날짜': pd.date_range(start, end, freq='D')})
        df['EUR'] = li[i]['EUR']
        df_li.append(df)

    df = pd.concat(df_li)
    df['날짜'] = df['날짜'].apply(lambda x: x.date())
    return df
