
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


# ==================================
# 데이터 불러오기 및 전처리
# ==================================
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


# ==================================
# 그래프 1. 장르별 영화 편수
# ==================================
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
    "장르별 영화 편수와 비율을 비교하여 "
    "박스오피스 10위권에 진입한 영화의 장르별 분포를 파악할 수 있다."
)


# ==================================
# 그래프 2. 장르별 총 관객 트리맵
# ==================================
st.divider()
st.header("그래프 2. 장르별 영화 총 관객 트리맵")

treemap_df = df.dropna(subset=["total_audi"]).copy()
treemap_df = treemap_df[treemap_df["total_audi"] >= 0]

if not treemap_df.empty:
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

    fig2.update_layout(
        margin=dict(t=50, l=10, r=10, b=10)
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("트리맵을 그릴 총 관객 수 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "장르별 영화의 총 관객 규모를 면적으로 비교하여 "
    "영화와 장르별 흥행 분포를 파악할 수 있다."
)


# ==================================
# 그래프 3. 총 관객 수 히스토그램
# ==================================
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
        labels={
            "total_audi": "총 관객 수(명)",
            "count": "영화 편수"
        }
    )

    fig3.update_layout(
        xaxis_title="총 관객 수(명)",
        yaxis_title="영화 편수",
        bargap=0.08
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 영화가 가장 많이 분포한 구간 계산
    bins = pd.cut(
        hist_df["total_audi"],
        bins=20,
        include_lowest=True
    )

    bin_counts = bins.value_counts().sort_index()
    most_common_bin = bin_counts.idxmax()
    most_common_count = bin_counts.max()

    # 총 관객 수가 가장 많은 영화
    top_movie = hist_df.loc[hist_df["total_audi"].idxmax()]

    st.markdown("### 📊 히스토그램 분석 결과")

    st.write(
        f"영화가 가장 많이 분포한 구간은 "
        f"**{most_common_bin.left:,.0f}명 ~ "
        f"{most_common_bin.right:,.0f}명**이며, "
        f"이 구간에 **{most_common_count}편**의 영화가 포함되어 있다."
    )

    st.write(
        f"총 관객 수가 가장 많은 영화는 "
        f"**{top_movie['movieNm']}**이며, "
        f"총 관객 수는 **{top_movie['total_audi']:,.0f}명**이다."
    )
else:
    st.warning("총 관객 수 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "영화별 총 관객 수가 집중된 구간과 최다 관객 영화를 파악할 수 있다."
)


# ==================================
# 그래프 4. 스크린 수와 총 관객 산점도
# ==================================
st.divider()
st.header("그래프 4. 개봉일 스크린 수와 총 관객의 관계")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi", "movieNm", "genre"]
).copy()

scatter_df = scatter_df[
    (scatter_df["first_scrn"] >= 0) &
    (scatter_df["total_audi"] >= 0)
]

if not scatter_df.empty:
    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "genre": True
        },
        labels={
            "first_scrn": "개봉일 스크린 수(개)",
            "total_audi": "총 관객 수(명)",
            "genre": "장르"
        },
        title="개봉일 스크린 수와 총 관객 수의 관계"
    )

    fig4.update_traces(
        marker=dict(size=10, opacity=0.75)
    )

    fig4.update_layout(
        legend_title="장르",
        hovermode="closest"
    )

    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("산점도를 그릴 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "개봉일 스크린 수와 총 관객 수의 관계를 살펴보고 "
    "장르별 흥행 양상을 비교할 수 있다. "
    "단, 상관관계만으로 인과관계를 단정할 수는 없다."
)


# ==================================
# 그래프 5. 장르별 총 관객 수 박스플롯
# ==================================
st.divider()
st.header("그래프 5. 장르별 총 관객 수 박스플롯")

box_df = df.dropna(
    subset=["genre", "total_audi", "movieNm"]
).copy()

box_df = box_df[box_df["total_audi"] >= 0]

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = box_df["genre"].value_counts()

selected_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_df = box_df[
    box_df["genre"].isin(selected_genres)
].copy()

if not box_df.empty:
    fig5 = px.box(
        box_df,
        x="genre",
        y="total_audi",
        color="genre",
        points="outliers",
        hover_name="movieNm",
        hover_data={
            "genre": True,
            "total_audi": ":,.0f"
        },
        labels={
            "genre": "장르",
            "total_audi": "총 관객 수(명)"
        },
        title="영화가 10편 이상인 장르의 총 관객 수 분포"
    )

    fig5.update_layout(
        showlegend=False,
        xaxis_title="장르",
        yaxis_title="총 관객 수(명)"
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.caption(
        "상자 밖의 이상치 점에 마우스를 올리면 "
        "영화명과 총 관객 수를 확인할 수 있습니다."
    )
else:
    st.warning("조건에 맞는 장르의 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "영화가 10편 이상인 장르만 비교하여 장르별 총 관객 수의 "
    "중앙값과 분포 범위를 파악할 수 있다."
)


# ==================================
# 그래프 6. 첫 주 관객 수 버블 그래프
# ==================================
st.divider()
st.header("그래프 6. 첫 주 관객 수를 반영한 버블 그래프")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "genre"
    ]
).copy()

bubble_df = bubble_df[
    (bubble_df["first_scrn"] >= 0) &
    (bubble_df["total_audi"] >= 0) &
    (bubble_df["first_week_audi"] >= 0)
]

if not bubble_df.empty:
    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "first_week_audi": ":,.0f",
            "genre": True
        },
        size_max=55,
        labels={
            "first_scrn": "개봉일 스크린 수(개)",
            "total_audi": "총 관객 수(명)",
            "first_week_audi": "첫 주 관객 수(명)",
            "genre": "장르"
        },
        title="개봉일 스크린 수 · 총 관객 수 · 첫 주 관객 수"
    )

    fig6.update_traces(
        marker=dict(opacity=0.65, line=dict(width=0.5))
    )

    fig6.update_layout(
        xaxis_title="개봉일 스크린 수(개)",
        yaxis_title="총 관객 수(명)",
        legend_title="장르",
        hovermode="closest"
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.caption(
        "버블이 클수록 첫 주 관객 수가 많습니다. "
        "점에 마우스를 올리면 영화명과 주요 수치를 확인할 수 있습니다."
    )
else:
    st.warning("버블 그래프를 그릴 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "개봉일 스크린 수와 총 관객 수에 첫 주 관객 수를 추가해 "
    "개봉 초기 관객 동원 규모와 전체 흥행 성적을 함께 비교할 수 있다."
)


# ==================================
# 그래프 7. 제작 국가 → 장르 선버스트
# ==================================
st.divider()
st.header("그래프 7. 제작 국가별 장르 분포")

sunburst_df = df.dropna(
    subset=["nation", "genre", "movieNm"]
).copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .astype(str)
    .str.strip()
    .replace("", "미분류")
)

sunburst_df["genre"] = (
    sunburst_df["genre"]
    .astype(str)
    .str.strip()
    .replace("", "미분류")
)

# 국가-장르별 영화 편수 집계
sunburst_counts = (
    sunburst_df
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)

if not sunburst_counts.empty:
    fig7 = px.sunburst(
        sunburst_counts,
        path=["nation", "genre"],
        values="영화 편수",
        title="제작 국가별 장르 구성"
    )

    fig7.update_traces(
        hovertemplate=(
            "항목: %{label}<br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        ),
        insidetextorientation="radial"
    )

    fig7.update_layout(
        margin=dict(t=50, l=10, r=10, b=10)
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.caption(
        "바깥쪽은 제작 국가, 안쪽은 장르를 나타냅니다. "
        "영역의 크기는 영화 편수에 비례합니다. "
        "국가 영역을 클릭하면 해당 국가의 장르 구성을 확대해 볼 수 있습니다."
    )
else:
    st.warning("선버스트 그래프를 그릴 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "제작 국가별 영화 편수와 각 국가에 포함된 장르 구성을 비교하여 "
    "국가별 장르 분포의 차이를 파악할 수 있다."
)
