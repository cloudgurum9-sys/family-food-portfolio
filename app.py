import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="훼미리식품 재무/재고 통합 대시보드", layout="wide")

# 2. 세션 상태 초기화 (메뉴를 이동해도 데이터가 유지되게 함)
if 'erp_data' not in st.session_state:
    st.session_state['erp_data'] = []

# 3. 사이드바 메뉴 구성
st.sidebar.title("🚀 구민준의 포트폴리오")
st.sidebar.info("회계 기본기와 Python 역량을 결합한 하이브리드 재무 인재")

menu = st.sidebar.radio(
    "프로젝트를 선택하세요:",
    ["[Project 1] 미니 ERP 시스템", 
     "[Project 2] 미수금(AR) 대사 대시보드", 
     "[Project 3] 재고(Inventory) 대사 자동화"]
)

st.sidebar.divider()
st.sidebar.caption("Contact: minjoon@email.com")

# ---------------------------------------------------------
# [Project 1] 미니 ERP 시스템
# ---------------------------------------------------------
if menu == "[Project 1] 미니 ERP 시스템":
    st.title("🏭 제조업 맞춤형 미니 ERP 시스템")
    st.markdown("매입/매출 전표 입력 시 **복식부기 분개**와 **부가세**가 자동 계산되는 로직입니다.")
    
    tabs = st.tabs(["📝 전표 입력", "📊 통합 분개장"])
    
    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            trans_type = st.selectbox("거래 유형", ["매입 (원재료 구매)", "매출 (제품 납품)"])
            client = st.selectbox("거래처", ["CJ제일제당", "삼양사", "해태제과", "이마트(PB)"])
        with col2:
            date = st.date_input("거래 일자", datetime.now())
            qty = st.number_input("수량(EA/Kg)", min_value=1, value=100)
            price = st.number_input("단가(공급가액)", min_value=0, value=10000, step=1000)

        supply_value = qty * price
        vat = int(supply_value * 0.1)
        total_amount = supply_value + vat

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("공급가액", f"{supply_value:,} 원")
        c2.metric("부가세(10%)", f"{vat:,} 원")
        c3.metric("합계금액", f"{total_amount:,} 원")

        if st.button("ERP 전표 저장"):
            if "매입" in trans_type:
                debit, credit = "원재료 / 부가세대급금", "매입채무(외상매입금)"
            else:
                debit, credit = "매출채권(외상매출금)", "매출액 / 부가세예수금"
            
            st.session_state['erp_data'].append({
                "일자": date, "구분": trans_type, "거래처": client,
                "공급가액": supply_value, "부가세": vat, "합계": total_amount,
                "차변계정": debit, "대변계정": credit
            })
            st.success("✅ 전표가 성공적으로 저장되었습니다.")

    with tabs[1]:
        if st.session_state['erp_data']:
            df = pd.DataFrame(st.session_state['erp_data'])
            st.dataframe(df.style.format({'공급가액': '{:,.0f}', '부가세': '{:,.0f}', '합계': '{:,.0f}'}), width='stretch')
        else:
            st.info("입력된 데이터가 없습니다.")

# ---------------------------------------------------------
# [Project 2] 미수금(AR) 대사 대시보드
# ---------------------------------------------------------
elif menu == "[Project 2] 미수금(AR) 대사 대시보드":
    st.title("💸 B2B 거래처 미수금(AR) 자동 대사")
    st.markdown("ERP 청구액과 은행 실입금액을 **자동 매칭**하여 미수 잔액을 추적합니다.")

    # 가상 데이터 생성
    inv_df = pd.DataFrame({
        '거래처명': ['해태제과', '해태제과', '크라운제과', '이마트(PB)'],
        '청구금액': [20000000, 30000000, 30000000, 20000000]
    })
    bank_df = pd.DataFrame({
        '입금자명': ['해태제과', '크라운제과'],
        '실제입금액': [30000000, 30000000]
    })

    # 대사 로직
    res_df = pd.merge(inv_df.groupby('거래처명').sum().reset_index(), 
                      bank_df.groupby('입금자명').sum().reset_index(), 
                      left_on='거래처명', right_on='입금자명', how='outer').fillna(0)
    res_df['미수잔액'] = res_df['청구금액'] - res_df['실제입금액']

    st.subheader("🚨 실시간 미수 잔액 현황")
    st.dataframe(res_df[['거래처명', '청구금액', '실제입금액', '미수잔액']].style.applymap(
        lambda x: 'background-color: #ffcccc' if x > 0 else '', subset=['미수잔액']
    ).format('{:,.0f}', subset=['청구금액', '실제입금액', '미수잔액']), width='stretch')

    # 시각화
    chart_data = res_df[res_df['미수잔액'] > 0]
    chart = alt.Chart(chart_data).mark_bar(color="#ff4b4b", size=60).encode(
        x=alt.X('거래처명', axis=alt.Axis(labelAngle=0)),
        y='미수잔액'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------------------
# [Project 3] 재고(Inventory) 대사 자동화
# ---------------------------------------------------------
elif menu == "[Project 3] 재고(Inventory) 대사 자동화":
    st.title("📦 WMS vs ERP 재고 대사 자동화")
    st.markdown("공장 실사 데이터(WMS)와 본사 장부(ERP)의 **재고 차이**를 즉시 식별합니다.")

    # 가상 데이터
    wms_df = pd.DataFrame({'품목명': ['홈런볼', '에이스', '오예스', '버터링'], '실사(WMS)': [5000, 3200, 1500, 4000]})
    erp_df = pd.DataFrame({'품목명': ['홈런볼', '에이스', '오예스', '버터링'], '장부(ERP)': [5000, 3500, 1500, 3900]})

    merged = pd.merge(erp_df, wms_df, on='품목명')
    merged['재고차이'] = merged['실사(WMS)'] - merged['장부(ERP)']

    st.subheader("🔍 품목별 재고 검증 결과")
    st.dataframe(merged.style.apply(lambda row: 
        ['background-color: #ffcccc' if row['재고차이'] < 0 else 
         'background-color: #fff0b3' if row['재고차이'] > 0 else ''] * len(row), axis=1
    ).format('{:,.0f}', subset=['장부(ERP)', '실사(WMS)', '재고차이']), width='stretch')

    st.info("💡 빨간색: 실사 부족(분실/파손) | 노란색: 실사 초과(입고전표 누락)")