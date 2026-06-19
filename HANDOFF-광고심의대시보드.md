# 핸드오프 — 광고심의 대시보드 (새 세션 인계용)

작성: 2026-06-19 · 이전 세션: https://claude.ai/code/session_01DsdVw7oGxDZJrHRHpf3rzL

## 한 줄 요약
Slack 광고심의 접수채널의 **2026-05~06 신청 197건**을 전수 분석해 **Notion 대시보드 DB**로 만드는 작업.
**데이터 분석·계산 100% 완료**(아래 `master.json`). **남은 건 Notion 적재뿐** — 이전 세션에서 Notion MCP 쓰기 권한이
재연결 후 "requires approval"로 막혀 보류됨. **새 세션에서 권한 정상 상태로 적재만 하면 끝.**

## 이미 끝난 산출물 (repo에 커밋되어 있음)
- **`master.json`** — 197행, 모든 컬럼 계산 완료. **이게 적재 소스다.** (영업일·처리속도·부서/도메인·질의분류 전부 포함)
- **`광고심의_대시보드_master.csv`** — 동일 데이터. Notion 페이지에서 `/import`하면 즉시 DB가 됨(가장 빠른 대안).
- **`build_master.py`** — 재생성 스크립트. 단 입력(`dash_rows_*.csv`, `idx_master.psv`)은 gitignore라 새 컨테이너엔 없음
  → **재분석 말고 `master.json`을 그대로 쓸 것.**

## 새 세션에서 할 일 (순서대로)
1. **데이터 확인**: `python3 -c "import json;d=json.load(open('master.json'));print(len(d), d[0].keys())"` → 197 확인.
2. **Notion DB 생성**: `notion-create-database`, parent page_id = `378a360d33e381459cf2c06eed9b052d` (Stanley's Universe). 스키마는 아래 DDL 그대로.
3. **197행 적재**: `master.json` 읽어 `notion-create-pages`로 적재(한 번에 최대 100행 → 2배치). 속성명은 스키마와 1:1. `취소여부`는 boolean, 빈 날짜/숫자는 생략.
4. **뷰 6종 + 요약 페이지** 생성(아래 목록).
5. (선택) WU-2026-0074(그로스 심의 협업) 또는 별도 WU에 DB 링크 기록.

> ⚠️ Notion 쓰기가 또 막히면: 사용자에게 Notion 커넥터 재허용 요청, 또는 `광고심의_대시보드_master.csv`를 `/import`하도록 안내.

## DB 스키마 (DDL — 그대로 복사)
```
CREATE TABLE (
"광고 제목" TITLE,
"종류" SELECT('광고':blue,'상품안내·신상품':green,'이벤트·프로모션':orange,'상품설명서':purple,'기타':gray),
"신청자" RICH_TEXT,
"신청부서(스쿼드)" SELECT('그로스 스쿼드':blue,'리텐션 스쿼드':blue,'네비게이션 스쿼드':blue,'브컴':pink,'연금스쿼드':purple,'WM':purple,'한국투자증권':purple,'삼성증권':purple,'아이팀':green,'디파짓':green,'PL':orange,'CL':orange,'연계대출':orange,'개인사업자팀':yellow,'송금팀':brown,'FX Team':red,'체크카드':red,'토스뱅크 서비스':gray,'기타':gray),
"상위 도메인" SELECT('그로스':blue,'브랜드커뮤니케이션':pink,'WM·증권':purple,'수신':green,'여신':orange,'개인사업자':yellow,'송금':brown,'외환':red,'체크카드':red,'기타':gray),
"신청일" DATE, "첫 반응일시" DATE, "소보 완료일" DATE, "컴플 완료일" DATE,
"검토기간(영업일)" NUMBER,
"처리속도" SELECT('1일내':green,'3일내':blue,'3일초과':red,'취소':gray,'미완':yellow),
"취소여부" CHECKBOX,
"질의응답 건수" NUMBER,
"Q_디클·유의사항" NUMBER,"Q_문구·표현" NUMBER,"Q_구조·스킴" NUMBER,"Q_대상·조건" NUMBER,"Q_심의필·법령" NUMBER,"Q_기타" NUMBER,
"추가정보요청 건수" NUMBER,
"R_원본·시안" NUMBER,"R_랜딩화면" NUMBER,"R_데이터·근거" NUMBER,"R_타팀확인" NUMBER,"R_기타" NUMBER,
"심의필번호" RICH_TEXT, "월" SELECT('2026-05':blue,'2026-06':green), "스레드" URL, "비고" RICH_TEXT
)
```
제목은 "광고심의 대시보드".

## 뷰 6종
1. 전체 테이블 — SORT BY `신청일` DESC
2. 처리속도 보드 — GROUP BY `처리속도`
3. 스쿼드별 보드 — GROUP BY `신청부서(스쿼드)`
4. 도메인별 보드 — GROUP BY `상위 도메인`
5. 월별 — GROUP BY `월`
6. 취소건 — FILTER `취소여부 = true`
+ 요약 페이지(DB 상단 콜아웃): 처리속도 건수·비율 스냅샷. 수치는 아래 "핵심 결과" 사용.

## 분류 택소노미(이미 master.json에 적용됨)
- 질의 Q_: ①디클·유의사항 ②문구·표현 ③구조·스킴 ④대상·조건 ⑤심의필·법령 ⑥기타
- 추가정보 R_: ①원본·시안 ②랜딩화면 ③데이터·근거 ④타팀확인 ⑤기타

## 핵심 결과 (요약 페이지/검증용)
- 총 197건 (5월 120 / 6월 77)
- 처리속도: 1일내 52(26.4%) · 3일내 48(24.4%) · 3일초과 47(23.9%) · 취소 20(10.2%) · 미완 30(15.2%)
- 완료 148건 평균 2.7영업일(최대 13). 도메인: 그로스 46 최다, WM·증권 1.1영업일로 최속, 여신 4.3로 최저속.
- 질의 816건(문구247·구조165·디클151·기타114·대상75·심의필64) / 추가정보 206건(원본73·랜딩53·데이터35·타팀28·기타17)
- 질의 최다: 그로스 "계좌개설 리워드 이벤트"(Q24), 통장개설 유도 인텔리(Q20)

## 데이터 정의/방법 (재현 필요 시에만)
- 소스: 채널 `C01RHSGM8UB`(#internal-광고및상품안내검토요청-bank), oldest=1777561231(2026-05-01) ~ 06-19, 빌더봇 부모메시지 197건.
- 건별 스레드 읽어 추출: 소보 접수/승인, **컴플 승인(=처리완료)**, 취소(요청자 철회 종결만 Y; 중간취소후 재요청완료는 N), 미완, 심의필번호, 질의·추가정보 분류.
- 신청부서: 제목 접두어 `[스쿼드]` → 매핑(공란은 제목 키워드 추론). 스쿼드→도메인 2단계. 매핑 룰은 `build_master.py` 참조.
- 영업일 = 신청일→컴플승인일, 주말+한국 공휴일(2026: 5/1,5/5,5/24,5/25,6/6) 제외.

## 막힌 점 (이번 세션)
- Notion MCP 쓰기(`create-database`,`create-pages`)가 MCP 재연결 이후 전부 "requires approval"로 차단됨(세션 초반 WU 페이지 생성은 성공했음 → 재연결로 권한 리셋 추정).
- 새 세션에서 깨끗한 권한 상태로 재시도하면 해결될 것으로 보임.
