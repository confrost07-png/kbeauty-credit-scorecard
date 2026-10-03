-- data/processed CSV를 SQLite에 적재한 뒤 실행 (sql/run_sql.py)
-- comparison(종목별 비교표), scorecard(여신 스코어카드)

-- 1) 투자자 순위 vs 은행 순위: 순위가 뒤바뀌는 종목 찾기
SELECT 종목명, 투자자순위, 은행순위, 종합점수, 등급,
       CASE WHEN 투자자순위 <> 은행순위 THEN '순위 바뀜' ELSE '동일' END AS 비교
FROM scorecard
ORDER BY 은행순위;

-- 2) 상환 체력 지표: 이익 점유가 큰 회사가 현금 전환도 좋은가?
SELECT 종목명, 이익점유_TTM, 영업이익률_TTM, 현금전환율, 부채비율, 이자보상배율, 순차입금
FROM comparison
ORDER BY 이익점유_TTM DESC;

-- 3) 운전자본 부담: 매출채권·재고가 현금으로 돌아오는 데 걸리는 일수
SELECT 종목명, 매출채권회전일수, 재고회전일수,
       ROUND(매출채권회전일수 + 재고회전일수, 1) AS 운전자본_회전일수
FROM comparison
ORDER BY 운전자본_회전일수 DESC;
