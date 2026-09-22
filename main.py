
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("영화의 장르, 흥행 성적, 개봉 특성 사이의 분포와 관계를 살펴봅니다.")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/"
    "modudata/main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.str.strip()

    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str).str.strip(),
        format="%Y%m%d",
        errors="coerce"
    )

    df["genre"] = (
        df["genre"].fillna("미분류").astype(str)
        .str.split("|").str[0].str.strip()
        .replace("", "미분류")
    )

    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["movieNm"]).copy()

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


st.info(
    f"총 {len(df):,}편의 영화 데이터 | "
    f"장르 종류: {df['genre'].nunique()}개"
)


# 그래프 1. 장르별 영화 편수
st.divider()
st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    df.groupby("genre")
    .size()
    .reset_index(name="영화 편수")
    .sort_values("영화 편수", ascending=False)
)

fig1 = px.pie(
    genre_counts,
    names="genre",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수 분포"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(legend_title="장르")

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "영화 장르별 편수와 비율을 비교하여 해당 기간에 "
    "박스오피스 10위권에 진입한 영화의 장르별 분포를 파악할 수 있다."
)


# 그래프 2. 장르별 영화 총 관객 트리맵
st.divider()
st.header("그래프 2. 장르별 영화 총 관객 트리맵")

treemap_df = df.dropna(subset=["total_audi"]).copy()
treemap_df = treemap_df[treemap_df["total_audi"] >= 0]

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객 분포"
)

fig2.update_traces(
    hovertemplate=(
        "영화명: %{label}<br>"
        "총 관객: %{value:,.0f}명<extra></extra>"
    )
)

fig2.update_layout(margin=dict(t=50, l=10, r=10, b=10))

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "장르별 영화의 총 관객 규모를 면적에 따라 비교하여 "
    "관객 수에서 큰 비중을 차지하는 영화와 장르별 흥행 분포를 파악할 수 있다."
)


# 그래프 3. 총 관객 수 히스토그램
st.divider()
st.header("그래프 3. 영화별 총 관객 수 분포")

hist_df = df.dropna(subset=["total_audi"]).copy()
hist_df = hist_df[hist_df["total_audi"] >= 0]

if not hist_df.empty:
    fig3 = px.histogram(
        hist_df,
        x="total_audi",
        nbins=20,
        title="영화별 총 관객 수 히스토그램",
        labels={"total_audi": "총 관객 수(명)", "count": "영화 편수"},
        hover_data={"movieNm": True, "total_audi": ":,.0f"}
    )

    fig3.update_layout(
        xaxis_title="총 관객 수(명)",
        yaxis_title="영화 편수",
        bargap=0.08
    )

    fig3.update_traces(
        hovertemplate=(
            "총 관객 수 구간: %{x}<br>"
            "영화 편수: %{y}편<extra></extra>"
        )
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 영화가 가장 많이 몰린 구간 계산
    bin_counts, bin_edges = pd.cut(
        hist_df["total_audi"],
        bins=20,
        include_lowest=True,
        retbins=True
    ).value_counts().sort_index(), None

    most_common_bin = bin_counts.idxmax()
    most_common_count = bin_counts.max()

    # 총 관객 수가 가장 많은 영화
    top_movie = hist_df.loc[hist_df["total_audi"].idxmax()]

    st.markdown("**히스토그램 분석 결과**")

    st.write(
        f"• 영화가 가장 많이 분포한 구간은 "
        f"**{most_common_bin.left:,.0f}명 ~ "
        f"{most_common_bin.right:,.0f}명**이며, "
        f"이 구간에 {most_common_count}편의 영화가 포함되어 있다."
    )

    st.write(
        f"• 총 관객 수가 가장 많은 영화는 "
        f"**{top_movie['movieNm']}**이며, "
        f"총 관객 수는 **{top_movie['total_audi']:,.0f}명**이다."
    )

else:
    st.warning("총 관객 수 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "히스토그램을 통해 영화별 총 관객 수가 어느 구간에 집중되어 있는지 "
    "확인하고, 영화들의 흥행 규모 분포와 최다 관객 영화를 파악할 수 있다."
)


# 그래프 4. 추후 추가 예정
st.divider()
st.header("그래프 4. 추후 추가 예정")
st.info("다음 그래프를 이 영역에 추가할 수 있습니다.")
