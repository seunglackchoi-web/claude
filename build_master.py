#!/usr/bin/env python3
# 광고심의 대시보드 master 조립: idx_master.psv + dash_rows_*.csv → master rows
import csv, glob, re, datetime, json

KST = datetime.timezone(datetime.timedelta(hours=9))
HOLIDAYS = {  # 2026 KR (window 05~06)
    datetime.date(2026,5,1), datetime.date(2026,5,5),
    datetime.date(2026,5,24), datetime.date(2026,5,25),
    datetime.date(2026,6,6),
}

def bdays(start, end):
    if not start or not end: return None
    if end < start: return 0
    n=0; d=start
    while d < end:
        d += datetime.timedelta(days=1)
        if d.weekday()<5 and d not in HOLIDAYS: n+=1
    return n

def parse_dt(s):
    s=(s or '').strip()
    if not s: return None
    s=s.replace('오전','AM').replace('오후','PM')
    for fmt in ('%Y-%m-%d %H:%M','%Y-%m-%d %H:%M:%S','%Y-%m-%d'):
        try: return datetime.datetime.strptime(s, fmt)
        except: pass
    return None

def norm_simui(s):
    s=(s or '').strip()
    if not s: return ''
    m=re.search(r'(20\d\d-\d+)', s)
    if not m: return s
    base=m.group(1)
    m2=re.search(r'외\s*(\d+)\s*건', s)
    return base + (f' 외{m2.group(1)}건' if m2 else '')

SQUAD_MAP = {
 '그로스 스쿼드':('그로스 스쿼드','그로스'),'리텐션 스쿼드':('리텐션 스쿼드','그로스'),
 '네비게이션 스쿼드':('네비게이션 스쿼드','그로스'),'브컴':('브컴','브랜드커뮤니케이션'),
 '연금스쿼드':('연금스쿼드','WM·증권'),'WM':('WM','WM·증권'),
 '한국투자증권':('한국투자증권','WM·증권'),'삼성증권':('삼성증권','WM·증권'),
 '아이팀':('아이팀','수신'),'아이스쿼드':('아이팀','수신'),'디파짓':('디파짓','수신'),'디파짓팀':('디파짓','수신'),
 'PL':('PL','여신'),'CL':('CL','여신'),'연계대출':('연계대출','여신'),
 '개인사업자팀':('개인사업자팀','개인사업자'),'송금팀':('송금팀','송금'),'송금':('송금팀','송금'),
 'FX Team':('FX Team','외환'),'체크카드':('체크카드','체크카드'),'토스뱅크 서비스':('토스뱅크 서비스','기타'),
}
def infer_from_title(t):
    t=t or ''
    if 'FX' in t or '외화' in t or '환율' in t or '환전' in t: return ('FX Team','외환')
    if '해외송금' in t or '송금' in t: return ('송금팀','송금')
    if '연금' in t or 'IRP' in t or '세액공제' in t: return ('연금스쿼드','WM·증권')
    if '증권' in t or '주식계좌' in t or 'IMA' in t or '채권' in t: return ('WM','WM·증권')
    if '체크카드' in t or '신용카드' in t or '모임카드' in t: return ('체크카드','체크카드')
    if '햇살론' in t or '사잇돌' in t or '대환' in t or '대출' in t or '갈아타기' in t: return ('PL','여신')
    if '개인사업자' in t or '사장님' in t or '사업소득' in t or '캐시노트' in t: return ('개인사업자팀','개인사업자')
    if '아이' in t or '용돈' in t or '공부하고' in t or '카네이션' in t: return ('아이팀','수신')
    if '적금' in t or '예금' in t or '통장' in t or '저금통' in t or '이자' in t or '돈모으기' in t or '나눠모으기' in t: return ('디파짓','수신')
    if 'GEO' in t or '인스타' in t or '블로그' in t or '바이럴' in t or '콘텐츠' in t or 'SNS' in t or '온드미디어' in t: return ('브컴','브랜드커뮤니케이션')
    if '이벤트' in t or '프로모션' in t or '돈주머니' in t or '미션' in t or '복권' in t: return ('그로스 스쿼드','그로스')
    return ('기타','기타')

def map_squad(tag, title):
    tag=(tag or '').strip()
    if tag in SQUAD_MAP: return SQUAD_MAP[tag]
    if '함께대출' in tag or '연계대출' in tag: return ('연계대출','여신')
    if 'FX' in tag: return ('FX Team','외환')
    if not tag: return infer_from_title(title)
    return ('기타','기타')

# load idx
idx={}
with open('idx_master.psv', encoding='utf-8') as f:
    r=csv.reader(f, delimiter='|'); next(r)
    for row in r:
        if len(row)<8: continue
        idx[row[0]]={'ts':row[1],'신청자':row[2],'제목':row[3],'스쿼드':row[4],'검토라인':row[5],'답글수':row[6],'완료':row[7]}

# load all extraction rows
ext={}
for fn in glob.glob('dash_rows_*.csv'):
    with open(fn, encoding='utf-8') as f:
        r=csv.reader(f, delimiter='|'); hdr=next(r)
        for row in r:
            if not row or not row[0].strip().isdigit(): continue
            d=dict(zip(hdr,row)); ext[row[0].strip()]=d

master=[]
for no in sorted(idx, key=lambda x:int(x)):
    i=idx[no]; e=ext.get(no, {})
    ts=float(i['ts']); dt=datetime.datetime.fromtimestamp(ts, KST)
    sin_dt=dt.replace(tzinfo=None)
    comp=parse_dt(e.get('컴플승인시각'))
    cancel = (e.get('취소여부','').strip().upper()=='Y')
    incomplete = (e.get('미완여부','').strip().upper()=='Y') or (comp is None)
    bd = bdays(sin_dt.date(), comp.date()) if comp else None
    if cancel: speed='취소'
    elif comp is None: speed='미완'
    elif bd is not None and bd<=1: speed='1일내'
    elif bd is not None and bd<=3: speed='3일내'
    else: speed='3일초과'
    sq,dom = map_squad(i['스쿼드'], i['제목'])
    permalink=f"https://tossbank.slack.com/archives/C01RHSGM8UB/p{i['ts'].replace('.','')}"
    def gi(k):
        v=(e.get(k,'') or '').strip()
        try: return int(v) if v else 0
        except: return 0
    master.append({
      'No':no,'광고 제목':i['제목'],'종류':(e.get('종류','') or '기타').strip() or '기타',
      '신청자':i['신청자'],'신청부서(스쿼드)':sq,'상위 도메인':dom,
      '신청일':sin_dt.strftime('%Y-%m-%d'),
      '첫 반응일시':(parse_dt(e.get('소보접수시각')).strftime('%Y-%m-%d') if parse_dt(e.get('소보접수시각')) else ''),
      '소보 완료일':(parse_dt(e.get('소보승인시각')).strftime('%Y-%m-%d') if parse_dt(e.get('소보승인시각')) else ''),
      '컴플 완료일':(comp.strftime('%Y-%m-%d') if comp else ''),
      '검토기간(영업일)':('' if bd is None else bd),
      '처리속도':speed,'취소여부':cancel,
      '질의응답 건수':gi('질의응답건수'),
      'Q_디클·유의사항':gi('Q_디클'),'Q_문구·표현':gi('Q_문구'),'Q_구조·스킴':gi('Q_구조'),
      'Q_대상·조건':gi('Q_대상'),'Q_심의필·법령':gi('Q_심의필'),'Q_기타':gi('Q_기타'),
      '추가정보요청 건수':gi('R_원본')+gi('R_랜딩')+gi('R_데이터')+gi('R_타팀')+gi('R_기타'),
      'R_원본·시안':gi('R_원본'),'R_랜딩화면':gi('R_랜딩'),'R_데이터·근거':gi('R_데이터'),
      'R_타팀확인':gi('R_타팀'),'R_기타':gi('R_기타'),
      '심의필번호':norm_simui(e.get('심의필번호')),
      '월':sin_dt.strftime('%Y-%m'),'스레드':permalink,'비고':(e.get('비고','') or '').strip(),
    })

json.dump(master, open('master.json','w',encoding='utf-8'), ensure_ascii=False, indent=0)
print('총 master 건수:', len(master))
miss=[no for no in idx if no not in ext]
print('추출 누락 No:', miss if miss else '없음')
from collections import Counter
print('처리속도 분포:', dict(Counter(m['처리속도'] for m in master)))
print('월별:', dict(Counter(m['월'] for m in master)))
print('도메인별:', dict(Counter(m['상위 도메인'] for m in master)))
