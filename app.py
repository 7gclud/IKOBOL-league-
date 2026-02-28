import streamlit as st
import pandas as pd

# --- [1. 설정] 연대별 구글 시트 ID (데이터 총괄 관리 구역) ---
# 각 연대별(10년 단위) 구글 시트 파일의 ID를 여기에 입력하세요.
SHEET_MAP = {
    "2010": "여기에_2010년대_시트_ID_입력",
    "2020": "여기에_2020년대_시트_ID_입력",
    "2030": "여기에_2030년대_시트_ID_입력",
    "2040": "여기에_2040년대_시트_ID_입력",
    "2050": "여기에_2050년대_시트_ID_입력",
    "2060": "여기에_2060년대_시트_ID_입력",
    "2070": "여기에_2070년대_시트_ID_입력"
}

def get_sheet_url(year, sheet_type):
    decade = str(year)[:3] + "0"
    sheet_id = SHEET_MAP.get(decade)
    if not sheet_id or "여기에" in sheet_id:
        return None
    # 탭 규칙: 2026_T, 2026_P, 2026_R, 2026_A
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={year}_{sheet_type}"

@st.cache_data(ttl=300) # 5분간 캐시 유지
def load_all_history(start_year, end_year):
    all_t, all_p = [], []
    for y in range(start_year, end_year + 1):
        url_t = get_sheet_url(y, "T")
        url_p = get_sheet_url(y, "P")
        
        try:
            if url_t:
                t = pd.read_csv(url_t)
                t['시즌'] = y
                all_t.append(t)
            if url_p:
                p = pd.read_csv(url_p)
                p['시즌'] = y
                all_p.append(p)
        except:
            continue # 데이터가 없는 연도는 건너뜁니다.
            
    full_t = pd.concat(all_t) if all_t else pd.DataFrame()
    full_p = pd.concat(all_p) if all_p else pd.DataFrame()
    return full_t, full_p

# --- [2. 레이아웃 설정] ---
st.set_page_config(page_title="IKBOL ARCHIVE", layout="wide")
st.title("⚾ IKBOL LEAGUE OFFICIAL ARCHIVE")

# 데이터 로드 (2016년부터 2077년까지 전체 로드)
full_t_df, full_p_df = load_all_history(2016, 2077)

# --- [3. 상단 고정 검색창] ---
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 20px !important; height: 52px !important; border: 2px solid #1f77b4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

search_name = st.text_input("🔍 선수 이름을 입력하여 통산 성적과 히스토리를 확인하세요", placeholder="예: 박선우")

if search_name:
    st.divider()
    t_res = full_t_df[full_t_df['이름'].str.contains(search_name, na=False)] if not full_t_df.empty else pd.DataFrame()
    p_res = full_p_df[full_p_df['이름'].str.contains(search_name, na=False)] if not full_p_df.empty else pd.DataFrame()

    if not t_res.empty or not p_res.empty:
        st.header(f"👤 {search_name} 선수의 Career-Path")
        
        # 통산 요약
        if not t_res.empty:
            st.subheader("📊 Career Totals (Batting)")
            c_t = t_res.groupby('이름').agg({'G':'sum','AB':'sum','H':'sum','HR':'sum','RBI':'sum','SB':'sum'}).reset_index()
            c_t['AVG'] = (c_t['H'] / c_t['AB']).round(3)
            st.table(c_t)
        
        # 연도별 상세 (스크롤)
        st.write("**시즌별 상세 기록**")
        if not t_res.empty: st.dataframe(t_res.sort_values('시즌', ascending=False), use_container_width=True)
        if not p_res.empty: st.dataframe(p_res.sort_values('시즌', ascending=False), use_container_width=True)
    else:
        st.warning(f"'{search_name}' 선수의 데이터가 시트에 없습니다.")
    st.divider()

# --- [4. 메인 메뉴] ---
tab_archive, tab_legend, tab_team = st.tabs(["📚 IKBOL ARCHIVE", "🏆 LEAGUE LEGENDARY", "🚩 TEAM HISTORY"])

with tab_archive:
    # 연도 선택 (2077년부터 역순)
    years = list(range(2077, 2015, -1))
    
    col_rank, col_award, col_stats = st.columns([1, 1, 2.5])
    
    with col_rank:
        st.subheader("📅 Season & Ranking")
        selected_year = st.selectbox("시즌 선택", years, label_visibility="collapsed")
        url_r = get_sheet_url(selected_year, "R")
        try:
            rank_df = pd.read_csv(url_r)
            st.write(f"**{selected_year} 최종 순위**")
            st.table(rank_df.head(10)[['순위', '팀명', '승률']])
        except: st.info(f"{selected_year}년 순위 데이터 업데이트 대기 중")

    with col_award:
        st.subheader("🏅 Major Awards")
        url_a = get_sheet_url(selected_year, "A")
        try:
            award_df = pd.read_csv(url_a)
            st.success(f"**MVP**\n\n{award_df.iloc[0]['MVP']}")
            st.info(f"**신인왕**\n\n{award_df.iloc[0]['신인왕']}")
        except: st.write("시상 내역 준비 중")

    with col_stats:
        st.subheader("📈 Title Holders (TOP 3)")
        y_t = full_t_df[full_t_df['시즌'] == selected_year] if not full_t_df.empty else pd.DataFrame()
        y_p = full_p_df[full_p_df['시즌'] == selected_year] if not full_p_df.empty else pd.DataFrame()
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**[타율 / 평자]**")
            if not y_t.empty: st.dataframe(y_t.sort_values('AVG', ascending=False).head(3)[['이름', 'AVG']], hide_index=True)
            if not y_p.empty: st.dataframe(y_p.sort_values('ERA', ascending=True).head(3)[['이름', 'ERA']], hide_index=True)
        with c2:
            st.write("**[홈런 / 탈삼진]**")
            if not y_t.empty: st.dataframe(y_t.sort_values('HR', ascending=False).head(3)[['이름', 'HR']], hide_index=True)
            if not y_p.empty: st.dataframe(y_p.sort_values('K', ascending=False).head(3)[['이름', 'K']], hide_index=True)
        with c3:
            st.write("**[도루 / 다승]**")
            if not y_t.empty: st.dataframe(y_t.sort_values('SB', ascending=False).head(3)[['이름', 'SB']], hide_index=True)
            if not y_p.empty: st.dataframe(y_p.sort_values('W', ascending=False).head(3)[['이름', 'W']], hide_index=True)

with tab_legend:
    st.header("🏆 LEAGUE LEGENDARY")
    st.write("IKBOL 리그 역대 최고 기록 (업데이트 예정)")

with tab_team:
    st.header("🚩 TEAM HISTORY")
    st.write("각 구단의 연대기와 역사를 기록하는 공간입니다. (모집 중인 '리그 사관'이 관리)")

# --- [5. Footer (운영진 정보)] ---
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        <p><b>IKBOL ARCHIVE Operations Team</b></p>
        <p>CDO (Data 총괄): 모집 중 | Creative: 모집 중 | System: 모집 중 | Historian (사관): 모집 중</p>
    </div>
    """, unsafe_allow_html=True)
