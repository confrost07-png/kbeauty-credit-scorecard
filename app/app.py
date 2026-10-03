# Streamlit 앱 — 실행: streamlit run app/app.py
# 데이터는 source/mini_project.ipynb 를 끝까지 실행하면 data/processed/ 에 만들어짐
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'

NAMES = ['아모레퍼시픽', '코스맥스', '에이피알']
COLORS = {'에이피알': '#2a78d6', '아모레퍼시픽': '#eb6834', '코스맥스': '#1baf7a'}
COLOR_SCALE = alt.Scale(domain=list(COLORS), range=list(COLORS.values()))
MARKET = {'아모레퍼시픽': '코스피(유가증권시장)', '코스맥스': '코스피(유가증권시장)', '에이피알': '코스피(유가증권시장)'}
NAVY = '#1E2B4A'

st.set_page_config(page_title='K-뷰티 수출 붐, 은행의 눈으로 본 3사', page_icon='📊', layout='wide')


@st.cache_data
def load():
    comp = pd.read_csv(PROC / 'comparison_data.csv', dtype={'종목코드': str})
    qfin = pd.read_csv(PROC / 'quarterly_financials.csv', dtype={'종목코드': str})
    price = pd.read_csv(PROC / 'cleaned_price.csv', dtype={'종목코드': str}, parse_dates=['날짜'])
    sc_path = PROC / 'scorecard.csv'
    scorecard = pd.read_csv(sc_path) if sc_path.exists() else None
    return comp, qfin, price, scorecard


if not (PROC / 'comparison_data.csv').exists():
    st.error('비교 데이터가 없습니다. source/mini_project.ipynb 를 먼저 끝까지 실행하세요.')
    st.stop()

comp, qfin, price, scorecard = load()
comp = comp.set_index('종목명').reindex(NAMES)
LATEST_Q = sorted(qfin['기간'].dropna().unique())[-1]


def fmt(v, unit='', digits=1):
    return '—' if pd.isna(v) else f'{v:,.{digits}f}{unit}'


# ── 사이드바: 종목 선택 · 기준 ──
st.sidebar.header('종목 선택')
name = st.sidebar.selectbox('분석할 종목', NAMES, index=NAMES.index('에이피알'))
row = comp.loc[name]
ACCENT = COLORS[name]


def style_page(accent):
    '''화면 꾸미기 — 남색 사이드바, 카드형 지표(칸마다 테두리), 선택한 회사 색으로 강조'''
    st.markdown(f"""<style>
    .stApp {{ background: #F3F5F9; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] [role="radiogroup"] label div:first-child {{ border-color: #9DB4E0 !important; }}
    [data-testid="stSidebar"] {{ background: {NAVY}; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] strong {{ color: #EEF2F9 !important; }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color: #A9B6CE !important; }}
    [data-testid="stSidebar"] [data-baseweb="select"] * {{ color: #1D1D1B !important; }}
    .cobox {{ background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.16); border-left: 5px solid {accent};
              border-radius: 10px; padding: 10px 12px; margin: 4px 0 12px; }}
    .cobox .nm {{ font-size: 1.15rem; font-weight: 700; color: #FFFFFF; }}
    .cobox .cd {{ font-size: .85rem; color: #C9D3E6; margin-top: 2px; }}
    .cobox .vc {{ display: inline-block; margin-top: 8px; font-size: .8rem; font-weight: 700; color: {NAVY};
                  background: #DCE7F7; border-radius: 999px; padding: 2px 10px; }}
    .hero {{ background: linear-gradient(120deg, {NAVY} 0%, #2B4677 100%); border-radius: 14px;
             padding: 20px 26px; margin: 0 0 8px; }}
    .hero .k {{ color: #9DB4E0; font-size: .82rem; font-weight: 700; letter-spacing: .02em; }}
    .hero h1 {{ color: #FFFFFF; font-size: 2.0rem; margin: 4px 0 0; padding: 0; }}
    .hero p {{ color: #D5DAE3; margin: 8px 0 0; font-size: .95rem; }}
    .sec {{ display: flex; align-items: center; gap: 10px; margin: 26px 0 10px; flex-wrap: wrap; }}
    .sec .bar {{ width: 6px; height: 26px; background: {accent}; border-radius: 3px; }}
    .sec .t {{ font-size: 1.3rem; font-weight: 700; color: #1D1D1B; }}
    .sec .tag {{ font-size: .8rem; color: #3A4458; background: #E3E9F3; padding: 2px 10px; border-radius: 999px; }}
    [data-testid="stMetric"] {{ background: #FFFFFF; border: 1px solid #DFE4EE; border-top: 4px solid {accent};
                                border-radius: 12px; padding: 12px 16px 10px; box-shadow: 0 1px 3px rgba(20,27,45,.06); }}
    [data-testid="stMetricLabel"] p {{ color: #5B6475 !important; font-size: .85rem; font-weight: 600; }}
    [data-testid="stMetricValue"] {{ color: #1D1D1B; font-weight: 700; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; flex-wrap: wrap; }}
    .stTabs [data-baseweb="tab"] {{ background: #E3E9F3; border-radius: 8px 8px 0 0; padding: 6px 14px; }}
    .stTabs [aria-selected="true"] {{ background: {NAVY}; }}
    .stTabs [aria-selected="true"] p {{ color: #FFFFFF !important; font-weight: 700; }}
    </style>""", unsafe_allow_html=True)


def sec(title, tag=None):
    '''구역 제목 — 왼쪽 색 막대 + 제목 + 작은 태그'''
    st.markdown(f"<div class='sec'><div class='bar'></div><div class='t'>{title}</div>"
                + (f"<span class='tag'>{tag}</span>" if tag else '') + "</div>", unsafe_allow_html=True)


style_page(ACCENT)
st.sidebar.markdown(f"<div class='cobox'><div class='nm'>{name}</div>"
                    f"<div class='cd'>종목코드 {row['종목코드']} · {MARKET.get(name, '').split('(')[0]} 상장</div>"
                    f"<div class='vc'>{row['밸류체인']}</div></div>", unsafe_allow_html=True)
st.sidebar.caption('밸류체인 위치는 주 수익원(매출이 주로 어디서 나오는가) 기준')
if '주수익원' in row and pd.notna(row['주수익원']):
    st.sidebar.caption(f"주 수익원: {row['주수익원']}")
basis = st.sidebar.radio('실적 기준', ['2026년 2분기', '최근 4분기 합계'], horizontal=False)
st.sidebar.caption(row['기준'])
st.sidebar.caption(f"수집 시각: {row['수집일시']}")

# ── 제목 ──
st.markdown("<div class='hero'><div class='k'>MODULE 04 · MINI PROJECT 01 · 2조</div>"
            "<h1>K-뷰티 수출 붐, 은행의 눈으로 본 3사</h1>"
            "<p>화장품 수출 붐을 만드는 3사는 은행 입장에서 믿을 만한 고객인가 — 브랜드(아모레퍼시픽) · ODM(코스맥스) · "
            "D2C 출발 글로벌 브랜드(에이피알)</p></div>", unsafe_allow_html=True)

# ── 1. 주요 시세 ──
sec(f'{name} · 주요 시세', f"{row['종목코드']} · {MARKET.get(name, '')}")
c = st.columns(3)
c[0].metric('현재가(종가)', fmt(row['현재가'], '원', 0), fmt(row['등락률'], '%', 2), delta_color='off')
c[1].metric('거래량', fmt(row['거래량'], '주', 0))
c[2].metric('시가총액', fmt(row['시가총액'] / 10000 if pd.notna(row['시가총액']) else None, '조원'))
c = st.columns(3)
c[0].metric('52주 최고', fmt(row['52주최고'], '원', 0))
c[1].metric('52주 최저', fmt(row['52주최저'], '원', 0))
c[2].metric('1년 수익률', fmt(row['1년수익률'], '%'))

# ── 2. 주요 재무지표 ──
if basis == '2026년 2분기':
    sales, op, ni = row['매출액'], row['영업이익'], row['순이익']
    s_share, p_share = row['매출점유'], row['이익점유']
else:
    recent4 = ['2025Q3', '2025Q4', '2026Q1', '2026Q2']
    t = qfin[qfin['기간'].isin(recent4)].groupby('종목명')[['매출액', '영업이익', '당기순이익']].sum(min_count=4)
    sales, op, ni = t.loc[name, '매출액'], t.loc[name, '영업이익'], t.loc[name, '당기순이익']
    s_share, p_share = row['매출점유_TTM'], row['이익점유_TTM']

sec(f'{name} · 주요 재무지표', f'{basis} · 연결')
c = st.columns(4)
c[0].metric('매출액', fmt(sales, '억원', 0))
c[1].metric('영업이익', fmt(op, '억원', 0))
c[2].metric('당기순이익', fmt(ni, '억원', 0))
c[3].metric('영업이익률', fmt(op / sales * 100 if pd.notna(op) and pd.notna(sales) else None, '%'))
c = st.columns(4)
c[0].metric('매출 점유(3사 중)', fmt(s_share, '%'))
c[1].metric('이익 점유(3사 중)', fmt(p_share, '%'))
c[2].metric('ROE(최근 4분기)', fmt(row['ROE'], '%'))
c[3].metric('해외 매출 비중', fmt(row['해외비중'], '%'))
c = st.columns(4)
c[0].metric('PER', fmt(row['PER'], '배', 2))
c[1].metric('추정 PER', fmt(row['추정PER'], '배', 2))
c[2].metric('PBR', fmt(row['PBR'], '배', 2))
c[3].metric('PEG', fmt(row['PEG'], '', 2))
sec(f'{name} · 은행 여신 지표', f'{LATEST_Q}말 잔액 · 최근 4분기 손익·현금흐름')
net_cash = pd.notna(row.get('순차입금')) and row.get('순차입금') < 0
c = st.columns(4)
c[0].metric('부채비율', fmt(row.get('부채비율'), '%'), help='부채총계 ÷ 자본총계. 낮을수록 빚 부담이 적다')
c[1].metric('유동비율', fmt(row.get('유동비율'), '%'), help='유동자산 ÷ 유동부채. 100% 미만이면 1년 안에 갚을 빚이 1년 안에 현금이 될 자산보다 많다')
c[2].metric('차입금의존도', fmt(row.get('차입금의존도'), '%'), help='총차입금 ÷ 자산총계')
c[3].metric('순차입금', '순현금' if net_cash else fmt(row.get('순차입금'), '억원', 0),
            fmt(row.get('순차입금'), '억원', 0) if net_cash else None, delta_color='off', help='총차입금 − 현금및현금성자산. 음수면 순현금')
c = st.columns(4)
c[0].metric('이자보상배율', fmt(row.get('이자보상배율'), '배'), help='영업이익 ÷ 이자비용 (최근 4분기)')
c[1].metric('현금전환율', fmt(row.get('현금전환율'), '%'), help='영업활동현금흐름 ÷ 영업이익 (최근 4분기). 이익이 실제 현금으로 들어오는 정도')
c[2].metric('순차입금/EBITDA', fmt(row.get('순차입금_EBITDA'), '배'), help='몇 년 벌어야 빚을 갚나. 음수면 순현금')
if scorecard is not None and name in set(scorecard['종목명']):
    s_row = scorecard.set_index('종목명').loc[name]
    c[3].metric('여신 스코어카드', f"{s_row['종합점수']:.2f}점 · {s_row['등급']}", help='과제용 단순 기준 (실제 은행 기준 아님)')

st.info('매출·이익 점유는 **분석 대상 3사 합계 안에서의 구성비**입니다. K-뷰티 산업 전체 점유율이 아닙니다.')

# ── 3. 비교 차트 ──
sec('3사 비교', '탭을 눌러 차트 전환')
tabs = st.tabs(['① 이익 점유', '② 분기 추이', '③ 성장성 × 수익성', '④ 밸류에이션', '⑤ 1년 주가', '⑥ 비교 테이블', '⑦ 여신 스코어카드', '⑧ 인사이트'])
highlight = alt.condition(alt.datum['종목명'] == name, alt.value(1.0), alt.value(0.45))

with tabs[0]:
    cols = ('매출점유', '이익점유') if basis == '2026년 2분기' else ('매출점유_TTM', '이익점유_TTM')
    share = comp.reset_index()[['종목명', *cols]].melt('종목명', var_name='구분', value_name='비중')
    share['구분'] = share['구분'].map({cols[0]: '매출 점유', cols[1]: '영업이익 점유'})
    share['순서'] = share['종목명'].map({n: i for i, n in enumerate(NAMES)})
    bars = alt.Chart(share).mark_bar(stroke='white', strokeWidth=2).encode(
        y=alt.Y('구분:N', title=None, sort=['매출 점유', '영업이익 점유']),
        x=alt.X('sum(비중):Q', title='3사 합계 = 100%', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=alt.Legend(orient='bottom', title=None)),
        order=alt.Order('순서:Q'),
        opacity=highlight,
        tooltip=['종목명', '구분', alt.Tooltip('비중:Q', format='.1f', title='비중(%)')],
    )
    share = share.sort_values(['구분', '순서'])
    share['중간'] = share.groupby('구분')['비중'].cumsum() - share['비중'] / 2   # 라벨 위치 = 막대 가운데
    labels = alt.Chart(share).mark_text(color='#0b0b0b', fontSize=13).encode(
        y=alt.Y('구분:N', sort=['매출 점유', '영업이익 점유']),
        x='중간:Q',
        text=alt.Text('비중:Q', format='.1f'),
    )
    st.altair_chart((bars + labels).properties(height=220), use_container_width=True)
    apr = comp.loc['에이피알']
    a, b = (apr[cols[0]], apr[cols[1]])
    if pd.notna(a) and pd.notna(b):
        st.markdown(f'**에이피알은 매출 {a:.1f}%로 3사 영업이익의 {b:.1f}%를 가져갔습니다** (이익 점유 ÷ 매출 점유 = {b / a:.2f}배).')

with tabs[1]:
    labels = {'이익점유_4Q': '이익 점유(최근 4분기 합산)', '매출점유_4Q': '매출 점유(최근 4분기 합산)',
              '이익점유': '이익 점유(분기)', '매출점유': '매출 점유(분기)', '영업이익': '영업이익', '매출액': '매출액',
              '영업이익률': '영업이익률', '부채비율': '부채비율', '유동비율': '유동비율'}
    labels = {k: v for k, v in labels.items() if k in qfin.columns}
    metric = st.radio('지표', list(labels), format_func=labels.get, horizontal=True)
    q = qfin.dropna(subset=[metric])
    line = alt.Chart(q).mark_line(point=alt.OverlayMarkDef(size=60, filled=True), strokeWidth=2).encode(
        x=alt.X('기간:N', title=None, sort=sorted(q['기간'].unique()), axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f'{metric}:Q', title=labels[metric] + (' (억원)' if metric in ('영업이익', '매출액') else ' (%)')),
        color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=alt.Legend(orient='bottom', title=None)),
        opacity=highlight,
        tooltip=['종목명', '기간', alt.Tooltip(f'{metric}:Q', format=',.1f')],
    ).properties(height=360)
    st.altair_chart(line, use_container_width=True)
    st.caption('한 분기만 고른 결과가 아닌지 확인하는 차트. "최근 4분기 합산"은 각 시점마다 직전 4개 분기를 합쳐 일회성 손익의 영향을 줄인 값입니다.')

with tabs[2]:
    sc = comp.reset_index()[['종목명', '매출성장률_YoY', '영업이익률', '시가총액']].dropna(subset=['매출성장률_YoY', '영업이익률'])
    sc['시가총액(조)'] = (sc['시가총액'] / 10000).round(1)
    base = alt.Chart(sc).encode(
        x=alt.X('매출성장률_YoY:Q', title='매출 성장률(전년 동기 대비, %)'),
        y=alt.Y('영업이익률:Q', title='영업이익률(%)'),
    )
    pts = base.mark_circle(stroke='white', strokeWidth=2).encode(
        size=alt.Size('시가총액(조):Q', scale=alt.Scale(range=[300, 3000]), legend=None),
        color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=alt.Legend(orient='bottom', title=None)),
        opacity=highlight,
        tooltip=['종목명', alt.Tooltip('매출성장률_YoY:Q', format='.1f', title='매출 성장률(%)'),
                 alt.Tooltip('영업이익률:Q', format='.1f', title='영업이익률(%)'), '시가총액(조)'],
    )
    txt = base.mark_text(dy=-28, fontSize=13, color='#0b0b0b').encode(text='종목명:N')
    st.altair_chart((pts + txt).properties(height=380), use_container_width=True)
    st.caption('점 크기 = 시가총액. 오른쪽 위로 갈수록 빠르게 크면서 많이 남기는 회사.')

with tabs[3]:
    val = comp.reset_index()[['종목명', 'PER', 'PEG', 'PBR', '예상EPS증가율']]
    cols3 = st.columns(3)
    for col, (metric, title) in zip(cols3, [('PER', 'PER(배)'), ('PBR', 'PBR(배)'), ('PEG', 'PEG = PER ÷ 예상 EPS 증가율')]):
        data = val.dropna(subset=[metric])
        x = alt.X('종목명:N', title=None, sort=NAMES, axis=alt.Axis(labelAngle=0))
        ch = alt.Chart(data).mark_bar(stroke='white', strokeWidth=2).encode(
            x=x, y=alt.Y(f'{metric}:Q', title=title),
            color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=None),
            opacity=highlight,
            tooltip=['종목명', alt.Tooltip(f'{metric}:Q', format='.2f')],
        )
        lbl = alt.Chart(data).mark_text(dy=-8, color='#0b0b0b').encode(
            x=x, y=f'{metric}:Q', text=alt.Text(f'{metric}:Q', format='.2f'))
        col.altair_chart((ch + lbl).properties(height=280), use_container_width=True)
    st.caption('PEG의 증가율은 증권사 컨센서스 기준(추정EPS ÷ 현재EPS − 1). 이익 감소가 예상되면 PEG를 계산하지 않습니다. 1보다 작을수록 성장 대비 낮게 평가된다는 뜻이며, 투자 권유가 아닙니다.')

with tabs[4]:
    p = price[price['종목명'].isin(NAMES)]
    line = alt.Chart(p).mark_line(strokeWidth=2).encode(
        x=alt.X('날짜:T', title=None),
        y=alt.Y('정규화지수:Q', title='시작일 = 100', scale=alt.Scale(zero=False)),
        color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=alt.Legend(orient='bottom', title=None)),
        opacity=highlight,
        tooltip=['종목명', alt.Tooltip('날짜:T', format='%Y-%m-%d'), alt.Tooltip('종가:Q', format=','),
                 alt.Tooltip('정규화지수:Q', format='.1f')],
    ).properties(height=380)
    rule = alt.Chart(pd.DataFrame({'y': [100]})).mark_rule(strokeDash=[4, 4], color='#52514e').encode(y='y:Q')
    st.altair_chart(line + rule, use_container_width=True)

with tabs[5]:
    for extra in ('주수익원', '부채비율', '유동비율', '영업이익률_TTM', '차입금의존도', '순차입금', '이자보상배율',
                  '순차입금_EBITDA', '현금전환율', '매출채권회전일수', '재고회전일수'):
        if extra not in comp.columns:
            comp[extra] = float('nan')
    show = comp.reset_index()[['종목명', '밸류체인', '주수익원', '현재가', '등락률', '시가총액', '매출액', '영업이익', '순이익',
                               '영업이익률', '영업이익률_TTM', '매출성장률_YoY', 'ROE',
                               '부채비율', '유동비율', '차입금의존도', '순차입금', '이자보상배율', '순차입금_EBITDA', '현금전환율',
                               '매출채권회전일수', '재고회전일수',
                               'PER', '추정PER', 'PBR', '예상EPS증가율', 'PEG', '해외비중',
                               '매출점유', '이익점유', '매출점유_TTM', '이익점유_TTM']]
    money = ['현재가', '시가총액', '매출액', '영업이익', '순이익', '순차입금']
    table = show.set_index('종목명').copy()
    for col_name in table.columns:
        if col_name in ('밸류체인', '주수익원'):
            table[col_name] = table[col_name].fillna('—').astype(str)
            continue
        digits = 0 if col_name in money else 2 if col_name in ('PER', '추정PER', 'PBR', 'PEG', '등락률') else 1
        table[col_name] = table[col_name].map(lambda v, d=digits: fmt(v, '', d))
    st.dataframe(table.T.astype(str), use_container_width=True)
    st.caption('단위: 현재가 원 · 시가총액/매출액/이익 억원 · 비율 % · PER/PBR 배')
    st.download_button('비교 데이터 CSV 내려받기', (PROC / 'comparison_data.csv').read_bytes(),
                       file_name='comparison_data.csv', mime='text/csv')

with tabs[6]:
    if scorecard is None:
        st.caption('data/processed/scorecard.csv 가 없습니다. 노트북의 스코어카드 셀을 먼저 실행하세요.')
    else:
        st.markdown('**여신 스코어카드** — 과제용 단순 기준이며 실제 은행 여신 심사 기준이 아닙니다. '
                    '가중치를 움직이면 종합점수·등급·은행 순위가 바로 다시 계산됩니다.')
        AREAS = [('상환 능력', '이자보상배율', 30), ('재무 안정성', '부채비율', 20), ('현금 창출', '현금전환율', 20),
                 ('수익성', '영업이익률·최근 4분기', 20), ('편중 리스크', '해외 매출 비중', 10)]
        wcols = st.columns(len(AREAS))
        weights = {area: col.slider(f'{area} ({label})', 0, 100, default, 5, key=f'w_{area}')
                   for (area, label, default), col in zip(AREAS, wcols)}
        sc = scorecard.set_index('종목명').reindex(NAMES)
        rows = []
        for n in NAMES:
            got = [(weights[a], sc.loc[n, f'{a}_점수']) for a, _, _ in AREAS if pd.notna(sc.loc[n, f'{a}_점수'])]
            den = sum(w for w, _ in got)
            total = sum(w * s for w, s in got) / den if den else float('nan')
            rows.append({'종목명': n, '종합점수': round(total, 2),
                         '등급': '—' if pd.isna(total) else 'A' if total >= 4 else 'B' if total >= 3 else 'C',
                         **{a: sc.loc[n, f'{a}_점수'] for a, _, _ in AREAS}})
        res = pd.DataFrame(rows)
        res['은행 순위'] = res['종합점수'].rank(ascending=False, method='min').astype('Int64')
        res['투자자 순위'] = res['종목명'].map(sc['투자자순위'])
        base = alt.Chart(res).encode(
            y=alt.Y('종목명:N', sort=NAMES, title=None),
            x=alt.X('종합점수:Q', scale=alt.Scale(domain=[0, 5]), title='종합점수 (5점 만점)'))
        bars = base.mark_bar(height=28).encode(
            color=alt.Color('종목명:N', scale=COLOR_SCALE, legend=None), opacity=highlight)
        text = base.mark_text(align='left', dx=6, fontSize=14).encode(
            text=alt.Text('label:N')).transform_calculate(label="format(datum['종합점수'], '.2f') + '점 · ' + datum['등급'] + '등급'")
        rules = alt.Chart(pd.DataFrame({'x': [3, 4]})).mark_rule(strokeDash=[4, 4], color='#52514e').encode(x='x:Q')
        st.altair_chart((bars + text + rules).properties(height=200), use_container_width=True)
        st.caption('점선: 3점(C|B), 4점(B|A) 경계')
        view = res.set_index('종목명')[[a for a, _, _ in AREAS] + ['종합점수', '등급', '투자자 순위', '은행 순위']]
        st.dataframe(view.T.astype(str), use_container_width=True)
        detail = sc[[f'{a}_지표값' for a, _, _ in AREAS]].copy()
        detail.columns = [f'{a} · {label}' for a, label, _ in AREAS]
        st.markdown('**채점에 쓴 지표값**')
        st.dataframe(detail.T.map(lambda v: fmt(v)).astype(str), use_container_width=True)

with tabs[7]:
    insight_path = ROOT / 'output' / 'insights.md'
    if insight_path.exists():
        st.markdown(insight_path.read_text(encoding='utf-8').split('\n', 1)[-1])
    else:
        st.caption('output/insights.md 가 없습니다. 노트북의 인사이트 셀을 먼저 실행하세요.')

with st.expander('데이터 출처와 해석 범위'):
    st.markdown(
        '- **시세**: 네이버증권 차트 데이터(일별 시세), 네이버증권 종목분석(FnGuide 제공) — 시총·PER·PBR은 KRX 기준\n'
        '- **재무**: 금융감독원 OpenDART 단일회사 주요계정(연결). 4분기는 연간 − 3분기 누적으로 역산\n'
        '- **은행 여신 지표**: OpenDART 전체 재무제표(연결). 계정 이름이 회사마다 달라 이름 규칙으로 찾음 → 사용 계정은 data/processed/bank_metrics.csv\n'
        '- **여신 스코어카드**: 과제용 단순 기준이며 실제 은행 여신 심사 기준이 아님\n'
        '- **해외 매출 비중**: 각 사 2026년 2분기 실적 발표(코스맥스는 해외 법인 매출 합산 참고치)\n'
        '- 점유율은 3사 합계 기준이며, 3사 사이에 제조·판매 거래가 있을 수 있어 산업 전체 매출로 해석하지 않습니다.\n'
        '- 에이피알의 높은 이익률을 유통 구조(D2C) 하나로 단정할 수 없습니다.\n'
        '- 수업 과제용 분석이며 투자 권유 목적이 아닙니다.'
    )
