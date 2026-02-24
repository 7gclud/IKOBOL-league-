import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# --- 설정 ---
# 구글 시트 주소창 d/ 뒤의 긴 문자열을 입력하세요
SHEET_ID = "여기에_구글시트_ID_입력" 

def get_sheet_url(sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=60)
def load_data(year):
    try:
        t_df = pd.read_csv(get_sheet_url(f"{year}_T"))
        p_df = pd.read_csv(get_sheet_url(f"{year}_P"))
        # 타율 및 방어율 자동 계산
        t_df['AVG'] = (t_df['H'] / t_df['AB']).fillna(0).round(3)
        p_df['ERA'] = (p_df['ER'] * 9 / p_df['IP']).fillna(0).round(2)
        return t_df, p_df
    except:
        return None, None

st.set_page_config(page_title="OOTP 리그 아카이브", layout="wide")
st.title("⚾ OOTP 연도별 공식 기록실")

# 연도 선택 메뉴 (시트에 추가할 연도를 계속 적어주세요)
selected_year = st.sidebar.selectbox("📅 시즌 선택", ["2025", "2026"])
t_df, p_df = load_data(selected_year)

if t_df is not None:
    tab1, tab2 = st.tabs(["🔍 선수 검색 및 순위", "📸 랭킹 짤 생성"])

    with tab1:
        # 검색 기능
        search_name = st.text_input("찾고 싶은 선수 이름을 입력하세요.")
        if search_name:
            res_t = t_df[t_df['이름'].str.contains(search_name, na=False)]
            res_p = p_df[p_df['이름'].str.contains(search_name, na=False)]
            if not res_t.empty: st.subheader("🏏 타자 상세"), st.dataframe(res_t)
            if not res_p.empty: st.subheader("🥎 투수 상세"), st.dataframe(res_p)
            if res_t.empty and res_p.empty: st.warning("결과가 없습니다.")
        else:
            # 기본 화면: TOP 10 순위표
            st.subheader(f"🏆 {selected_year} 시즌 주요 부문 순위")
            c1, c2 = st.columns(2)
            c1.write("타자 (타율 순)")
            c1.table(t_df.sort_values("AVG", ascending=False).head(10)[['이름', '팀', 'AVG', 'HR', 'RBI']])
            c2.write("투수 (ERA 순)")
            c2.table(p_df.sort_values("ERA", ascending=True).head(10)[['이름', '팀', 'ERA', 'W', 'K']])

    with tab2:
        st.info("현재 연도의 상위 타자들을 이미지로 만듭니다.")
        if st.button("이미지 생성"):
            # 이미지 생성 로직
            img = Image.new('RGB', (600, 800), color=(15, 30, 60))
            draw = ImageDraw.Draw(img)
            draw.text((220, 50), f"{selected_year} TOP 5", fill=(255, 215, 0))
            
            y = 150
            for i, row in t_df.sort_values("AVG", ascending=False).head(5).iterrows():
                draw.text((100, y), f"{row['이름']} ({row['팀']}) - {row['AVG']}", fill=(255, 255, 255))
                y += 60
            
            st.image(img)
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.download_button("이미지 저장", buf.getvalue(), f"rank_{selected_year}.png")
