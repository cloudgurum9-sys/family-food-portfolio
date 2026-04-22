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

menu = st.sidebar.radio(
    "프로젝트를 선택하세요:",
    ["[Project 1] 미니 ERP 시스템", 
     "[Project 2] 미수금 대사 대시보드", 
     "[Project 3] 재고(Inventory) 대사 자동화"]
)

st.sidebar.divider()
st.sidebar.caption("Contact: alswns0712@naver.com")

# ---------------------------------------------------------
# [Project 1] 미니 ERP 시스템
# ---------------------------------------------------------
if menu == "[Project 1] 미니 ERP 시스템":
    st.title("🏭 제조업 맞춤형 미니 ERP 시스템")
    st.markdown("매입/매출 전표 입력 시 **복식부기 분개**와 **부가세**가 자동 계산되는 로직입니다.")
    
    tabs = st.tabs(["📝 전표 입력", "📊 통합 분개장"])
    
    with tabs[0]:
        col_type, col_date = st.columns(2)
        with col_type:
            trans_type = st.selectbox("거래 유형", ["매입 (원재료 구매)", "매출 (제품 납품)"])
        with col_date:
            date = st.date_input("거래 일자", datetime.now())

        col_client, col_item = st.columns(2)
        with col_client:
            if "매입" in trans_type:
                client = st.selectbox("거래처(매입처)", ["CJ제일제당", "삼양사", "대한제분"])
            else:
                client = st.selectbox("거래처(매출처)", ["해태제과식품", "크라운제과", "이마트(PB)"])
        with col_item:
            if "매입" in trans_type:
                item = st.selectbox("품목(원자재)", ["강력밀가루", "정제설탕", "가공유지"])
            else:
                item = st.selectbox("품목(제품)", ["홈런볼(납품용)", "에이스(납품용)", "오예스(수출용)"])

        col_qty, col_price = st.columns(2)
        with col_qty:
            qty = st.number_input("수량(EA/Kg)", min_value=1, value=100)
        with col_price:
            price = st.number_input("단가(공급가액/VAT별도)", min_value=0, value=20000, step=1000)

        supply_value = qty * price
        vat = int(supply_value * 0.1)
        total_amount = supply_value + vat

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("공급가액", f"{supply_value:,} 원")
        c2.metric("부가세(10%)", f"{vat:,} 원")
        c3.metric("합계금액", f"{total_amount:,} 원")

        if st.button("전표 저장 및 ERP 전송"):
            if "매입" in trans_type:
                debit_acc, credit_acc = "원재료", "매입채무(외상매입금)"
                vat_acc = "부가세대급금" 
                
                debit_entry = f"{debit_acc} ({supply_value:,} 원)\n{vat_acc} ({vat:,} 원)"
                credit_entry = f"{credit_acc} ({total_amount:,} 원)"

            else:
                debit_acc, credit_acc = "매출채권(외상매출금)", "매출액"
                vat_acc = "부가세예수금" 

                debit_entry = f"{debit_acc} ({total_amount:,} 원)"
                credit_entry = f"{credit_acc} ({supply_value:,} 원)\n{vat_acc} ({vat:,} 원)"
            
            st.session_state['erp_data'].append({
                "일자": date, "구분": trans_type, "거래처": client, "품목": item, "수량": qty,
                "공급가액": supply_value, "부가세": vat, "합계": total_amount,
                "차변분개": debit_entry, "대변분개": credit_entry
            })
            st.success("✅ 전표가 ERP에 등록되었습니다.")

    with tabs[1]:
        if st.session_state['erp_data']:
            df = pd.DataFrame(st.session_state['erp_data'])
            cols = ['일자', '구분', '거래처', '품목', '수량', '공급가액', '부가세', '합계', '차변분개', '대변분개']
            df = df[cols]
            st.dataframe(df.style.format({'수량': '{:,.0f}', '공급가액': '{:,.0f}', '부가세': '{:,.0f}', '합계': '{:,.0f}'}), width='stretch')
        else:
            st.info("입력된 데이터가 없습니다.")

# ---------------------------------------------------------
# [Project 2] 미수금(AR) 대사 대시보드
# ---------------------------------------------------------
elif menu == "[Project 2] 미수금 대사 대시보드":
    st.title("💸 B2B 거래처 미수금 자동 대사")
    st.markdown("ERP 청구액과 은행 실입금액을 **자동 매칭**하여 미수 잔액을 추적합니다.")

    inv_data = {
        '거래처명': ['해태제과', '해태제과', '크라운제과', '이마트(PB)'],
        '발행일자': ['2026-03-10', '2026-04-05', '2026-04-10', '2026-02-15'],
        '청구금액(VAT포함)': [20000000, 30000000, 30000000, 20000000] 
    }
    inv_df = pd.DataFrame(inv_data)

    bank_data = {
        '입금자명': ['해태제과', '크라운제과'],
        '입금일자': ['2026-04-15', '2026-04-20'], 
        '실제입금액': [30000000, 30000000] 
    }
    bank_df = pd.DataFrame(bank_data)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🧾 [ERP 데이터] 총 청구 내역")
        st.dataframe(inv_df.style.format({'청구금액(VAT포함)': '{:,.0f}'}), width='stretch')

    with col2:
        st.subheader("🏦 [Bank 데이터] 실제 입금 내역")
        st.dataframe(bank_df.style.format({'실제입금액': '{:,.0f}'}), width='stretch')

    st.divider() 

    invoice_grouped = inv_df.groupby('거래처명')['청구금액(VAT포함)'].sum().reset_index()
    bank_grouped = bank_df.groupby('입금자명')['실제입금액'].sum().reset_index()
    df_merged = pd.merge(invoice_grouped, bank_grouped, left_on='거래처명', right_on='입금자명', how='outer').fillna(0)

    df_merged['거래처명'] = df_merged['거래처명'].fillna(df_merged['입금자명'])
    df_merged['미수잔액'] = df_merged['청구금액(VAT포함)'] - df_merged['실제입금액']

    st.subheader("🚨 거래처별 미수금 자동 대사 결과")
    st.dataframe(df_merged[['거래처명', '청구금액(VAT포함)', '실제입금액', '미수잔액']].style.map(
        lambda x: 'background-color: #ffcccc' if x > 0 else '', subset=['미수잔액']
    ).format('{:,.0f}', subset=['청구금액(VAT포함)', '실제입금액', '미수잔액']), width='stretch')

    st.divider() 

    st.subheader("📊 미수 잔액 시각화")
    chart_data = df_merged[df_merged['미수잔액'] > 0][['거래처명', '미수잔액']]

    if not chart_data.empty:
        chart = alt.Chart(chart_data).mark_bar(color="#ff4b4b", size=80).encode(
            x=alt.X('거래처명', axis=alt.Axis(labelAngle=0)), 
            y=alt.Y('미수잔액')
        ).properties(height=400)

        st.altair_chart(chart, use_container_width=True)
    else:
        st.success("🎉 현재 모든 거래처의 미수금이 0원입니다!")

# ---------------------------------------------------------
# [Project 3] 재고(Inventory) 대사 자동화
# ---------------------------------------------------------
elif menu == "[Project 3] 재고(Inventory) 대사 자동화":
    st.title("📦 WMS vs ERP 재고 대사 자동화")
    st.markdown("공장 실사 데이터(WMS)와 본사 장부(ERP)의 **재고 차이**를 즉시 식별합니다.")

    # 🎯 [핵심 복구 1] 원본 데이터 세팅 (품목코드 포함)
    wms_data = {
        '품목코드': ['P001', 'P002', 'P003', 'P004'],
        '품목명': ['홈런볼(납품용)', '에이스(납품용)', '오예스(수출용)', '버터링(납품용)'],
        '실사재고(WMS)': [5000, 3200, 1500, 4000]
    }
    df_wms = pd.DataFrame(wms_data)

    erp_data = {
        '품목코드': ['P001', 'P002', 'P003', 'P004'],
        '장부재고(ERP)': [5000, 3500, 1500, 3900]
    }
    df_erp = pd.DataFrame(erp_data)

    # 🎯 [핵심 복구 2] UI 가로 배치 (WMS 표 vs ERP 표)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏭 [WMS] 공장 실사 재고")
        st.dataframe(df_wms.style.format({'실사재고(WMS)': '{:,.0f}'}), width='stretch')
    with col2:
        st.subheader("💻 [ERP] 재무팀 장부 재고")
        st.dataframe(df_erp.style.format({'장부재고(ERP)': '{:,.0f}'}), width='stretch')

    st.divider()

    # 🎯 [핵심 복구 3] 데이터 병합 및 상태 로직
    df_merged = pd.merge(df_erp, df_wms, on='품목코드', how='outer')
    cols = ['품목코드', '품목명', '장부재고(ERP)', '실사재고(WMS)']
    df_merged = df_merged[cols]

    df_merged['재고차이'] = df_merged['실사재고(WMS)'] - df_merged['장부재고(ERP)']

    # 상태 분류 함수
    def check_status(diff):
        if diff == 0:
            return "✅ 정상"
        elif diff < 0:
            return "🚨 부족 (분실/파손 의심)"
        else:
            return "⚠️ 초과 (입고 전표 누락 의심)"

    df_merged['상태'] = df_merged['재고차이'].apply(check_status)

    st.subheader("🔍 품목별 재고 대사 결과")

    # 불일치 항목 색상 강조 함수
    def highlight_diff(row):
        if row['재고차이'] < 0:
            return ['background-color: #ffcccc'] * len(row) # 빨간색 (부족)
        elif row['재고차이'] > 0:
            return ['background-color: #fff0b3'] * len(row) # 노란색 (초과)
        else:
            return [''] * len(row)

    st.dataframe(df_merged.style.apply(highlight_diff, axis=1).format({
        '장부재고(ERP)': '{:,.0f}',
        '실사재고(WMS)': '{:,.0f}',
        '재고차이': '{:,.0f}'
    }), width='stretch')
