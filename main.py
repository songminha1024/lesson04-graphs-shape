
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 페이지 설정
# ==========================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "영화의 장르, 흥행 성적, 개봉 특성 사이의 "
    "분포와 관계를 살펴봅니다."
)


# ==========================================
# 데이터 불러오기 및 전처리
# ==========================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/"
    "modudata/main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

    # 개봉일을 실제 날짜 자료형으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str).str.strip(),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르가 여러 개라면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "미분류")
    )

    # 숫자 열 변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# ==========================================
# 데이터 요약
# ==========================================
st.info(
    f"총 {len(df):,}편의 영화 데이터 | "
    f"장르 종류: {df['genre'].nunique()}개"
)


# ==========================================
# 그래프 1. 장르별 영화 편수
# ==========================================
st.divider()
st.header("그래프 1. 장르별 영화 편수")

st.markdown(
    "영화의 첫 번째 장르를 기준으로 장르별 영화 편수와 "
    "전체에서 차지하는 비율을 확인합니다."
)

# 장르별 영화 편수 계산
genre_counts = (
    df.groupby("genre")
    .size()
    .reset_index(name="영화 편수")
    .sort_values("영화 편수", ascending=False)
)

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names="genre",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수 분포",
    custom_data=["영화 편수"]
)

# 마우스 오버 시 편수와 비율 표시
fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    legend_title="장르",
    uniformtext_minsize=10,
    uniformtext_mode="hide"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "영화 장르별 편수와 비율을 비교하여 "
    "해당 기간에 박스오피스 10위권에 진입한 영화의 "
    "장르별 분포를 파악할 수 있다."
)


# ==========================================
# 그래프 2. 추가 예정
# ==========================================
st.divider()
st.header("그래프 2. 추가 예정")
st.caption("영화 데이터의 분포와 관계를 분석하는 그래프를 추가할 공간입니다.")


# ==========================================
# 그래프 3. 추가 예정
# ==========================================
st.divider()
st.header("그래프 3. 추가 예정")
st.caption("새로운 분석 그래프를 추가할 공간입니다.")
