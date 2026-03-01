import streamlit as st
import pandas as pd

# --- [설정] 본인의 구글 시트 ID를 입력하세요 ---
SHEET_ID = "여기에_구글_시트_ID_입력" 

def get_sheet_url(tab_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab_name}"

@st.cache_data(ttl=60) # 1분마다 데이터 갱신
def load_data():
    t_df = pd.read_csv(get_sheet_url("Total_T"))
    p_df = pd.read_csv(get_sheet_url("Total_P"))
    a_df = pd.read_csv(get_sheet_url("Total_A"))
    return t_df, p_df, a_df

st.set_page_config(page_title="IKBOL 아카이브", layout="wide")
st.title("⚾ IKBOL LEAGUE OFFICIAL ARCHIVE")

t_df, p_df, a_df = load_data()

# --- [선수 검색] ---
search_name = st.text_input("🔍 선수 이름을 입력하세요 (예: 구찬성, 양의지)")

if search_name:
    # 데이터 필터링
    t_res = t_df[t_df['이름'] == search_name]
    p_res = p_df[p_df['이름'] == search_name]
    a_res = a_df[a_df['이름'] == search_name]

    if not t_res.empty or not p_res.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(f"👤 {search_name} 통산 기록")
            if not t_res.empty:
                st.subheader("타자 성적")
                st.dataframe(t_res.sort_values('시즌', ascending=False), hide_index=True)
            if not p_res.empty:
                st.subheader("투수 성적")
                st.dataframe(p_res.sort_values('시즌', ascending=False), hide_index=True)
        
        with col2:
            st.header("🏆 Honor Roll")
            for _, row in a_res.sort_values('시즌', ascending=False).iterrows():
                st.success(f"**{int(row['시즌'])} {row['구분']}** ({row['팀명']})")
    else:
        st.error("데이터가 없습니다.")
