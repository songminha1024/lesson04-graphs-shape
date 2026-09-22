import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================
# 기본 설정
# ==================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("KOBIS 영화 데이터를 이용해 영화의 분포와 변수 사이의 관계를 살펴봅니다.")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# ==================================
# 데이터 불러오기
# ==================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름 정리
    df.columns = df.columns.str.strip()

    # 개봉일
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str),
            format="%Y%m%d",
            errors="coerce"
        )

    # 장르가 여러 개라면 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = (
            df["genre"]
            .fillna("미상")
            .astype(str)
            .str.split("|")
            .str[0]
            .str.strip()
        )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 영화명이 없는 행 제거
    df = df.dropna(subset=["movieNm"])

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# ==================================
# 그래프 1. 장르별 영화 수
# ==================================
st.divider()
st.header("그래프 1. 영화는 어떤 장르가 가장 많은가?")

genre_count = (
    df["genre"]
    .fillna("미상")
    .value_counts()
    .reset_index()
)

genre_count.columns = ["genre", "count"]

fig1 = px.pie(
    genre_count,
    names="genre",
    values="count",
    hole=0.45,
    title="영화 장르별 개수",
)

fig1.update_traces(
    textposition="inside",
    textinfo="label+percent"
)

st.plotly_chart(fig1, use_container_width=True)


# ==================================
# 그래프 2. 장르별 총 관객
# ==================================
st.divider()
st.header("그래프 2. 어떤 장르의 영화가 가장 많은 관객을 모았는가?")

genre_audience = (
    df.dropna(subset=["genre", "total_audi"])
    .groupby("genre", as_index=False)["total_audi"]
    .sum()
    .sort_values("total_audi", ascending=False)
)

fig2 = px.treemap(
    genre_audience,
    path=["genre"],
    values="total_audi",
    title="장르별 총 관객 수"
)

st.plotly_chart(fig2, use_container_width=True)


# ==================================
# 그래프 3. 총 관객 수 분포
# ==================================
st.divider()
st.header("그래프 3. 영화의 총 관객 수는 어떻게 분포하는가?")

hist_df = df.dropna(subset=["total_audi"]).copy()
hist_df = hist_df[hist_df["total_audi"] >= 0]

if not hist_df.empty:
    fig3 = px.histogram(
        hist_df,
        x="total_audi",
        nbins=20,
        title="영화별 총 관객 수 분포",
        labels={
            "total_audi": "총 관객 수(명)",
            "count": "영화 수"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 가장 많은 영화가 포함된 구간
    bins = pd.cut(
        hist_df["total_audi"],
        bins=20,
        include_lowest=True
    )

    bin_counts = bins.value_counts().sort_index()

    if not bin_counts.empty:
        most_common_bin = bin_counts.idxmax()

        st.caption(
            f"가장 많은 영화가 포함된 관객 수 구간: "
            f"{most_common_bin}"
        )

    # 총 관객 수가 가장 많은 영화
    max_movie = hist_df.loc[
        hist_df["total_audi"].idxmax()
    ]

    st.caption(
        f"총 관객 수가 가장 많은 영화: "
        f"{max_movie['movieNm']} "
        f"({max_movie['total_audi']:,.0f}명)"
    )


# ==================================
# 그래프 4. 개봉 스크린 수와 총 관객 수
# ==================================
st.divider()
st.header("그래프 4. 개봉 스크린 수가 많을수록 총 관객 수도 많은가?")

graph4_df = df.dropna(
    subset=["first_scrn", "total_audi", "movieNm", "genre"]
).copy()

graph4_df = graph4_df[
    (graph4_df["first_scrn"] >= 0) &
    (graph4_df["total_audi"] >= 0)
]

if not graph4_df.empty:
    fig4 = px.scatter(
        graph4_df,
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
            "first_scrn": "개봉 스크린 수",
            "total_audi": "총 관객 수(명)",
            "genre": "장르"
        },
        title="개봉 스크린 수와 총 관객 수의 관계"
    )

    st.plotly_chart(fig4, use_container_width=True)


# ==================================
# 그래프 5. 장르별 총 관객 수 분포
# ==================================
st.divider()
st.header("그래프 5. 장르에 따라 총 관객 수의 분포가 다른가?")

box_df = df.dropna(
    subset=["genre", "total_audi", "movieNm"]
).copy()

# 영화가 10편 이상인 장르만 사용
valid_genres = (
    box_df["genre"]
    .value_counts()
)

valid_genres = valid_genres[
    valid_genres >= 10
].index

box_df = box_df[
    box_df["genre"].isin(valid_genres)
]

if not box_df.empty:
    fig5 = px.box(
        box_df,
        x="genre",
        y="total_audi",
        points="outliers",
        hover_name="movieNm",
        labels={
            "genre": "장르",
            "total_audi": "총 관객 수(명)"
        },
        title="장르별 총 관객 수 분포"
    )

    st.plotly_chart(fig5, use_container_width=True)


# ==================================
# 그래프 6. 개봉 스크린 수·총 관객·첫 주 관객
# ==================================
st.divider()
st.header("그래프 6. 개봉 규모와 흥행 결과는 어떤 관계가 있는가?")

graph6_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "first_week_audi",
        "movieNm",
        "genre"
    ]
).copy()

graph6_df = graph6_df[
    (graph6_df["first_scrn"] >= 0) &
    (graph6_df["total_audi"] >= 0) &
    (graph6_df["first_week_audi"] >= 0)
]

if not graph6_df.empty:
    fig6 = px.scatter(
        graph6_df,
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
        labels={
            "first_scrn": "개봉 스크린 수",
            "total_audi": "총 관객 수(명)",
            "first_week_audi": "첫 주 관객 수",
            "genre": "장르"
        },
        title="개봉 규모와 흥행 결과의 관계"
    )

    fig6.update_traces(
        marker=dict(
            opacity=0.7
        )
    )

    st.plotly_chart(fig6, use_container_width=True)


# ==================================
# 그래프 7. 국가 → 장르별 영화 분포
# ==================================
st.divider()
st.header("그래프 7. 국가와 장르에 따라 영화 분포는 어떻게 다른가?")

sunburst_df = df.dropna(
    subset=["nation", "genre"]
).copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미상")
    .astype(str)
)

sunburst_df["genre"] = (
    sunburst_df["genre"]
    .fillna("미상")
    .astype(str)
)

sunburst_count = (
    sunburst_df
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="count")
)

if not sunburst_count.empty:
    fig7 = px.sunburst(
        sunburst_count,
        path=["nation", "genre"],
        values="count",
        title="국가 → 장르별 영화 수"
    )

    st.plotly_chart(fig7, use_container_width=True)


# ==================================
# 그래프 8. 첫 주 관객 수와 10위권 체류 기간
# ==================================
st.divider()
st.header(
    "그래프 8. 첫 주 관객 수가 많았던 영화는 10위권에도 오래 머무르는가?"
)

graph8_df = df.dropna(
    subset=["days_in_top10", "total_audi", "movieNm"]
).copy()

graph8_df = graph8_df[
    (graph8_df["days_in_top10"] >= 0) &
    (graph8_df["total_audi"] >= 0)
]

if not graph8_df.empty:
    fig8 = px.scatter(
        graph8_df,
        x="days_in_top10",
        y="total_audi",
        hover_name="movieNm",
        hover_data={
            "days_in_top10": ":,.0f",
            "total_audi": ":,.0f"
        },
        labels={
            "days_in_top10": "10위권에 머문 날수(일)",
            "total_audi": "총 관객 수(명)"
        },
        title="첫 주 관객 수가 많았던 영화는 10위권에도 오래 머무르는가?"
    )

    fig8.update_traces(
        marker=dict(
            size=10,
            opacity=0.75
        )
    )

    fig8.update_layout(
        xaxis_title="10위권에 머문 날수(일)",
        yaxis_title="총 관객 수(명)",
        hovermode="closest"
    )

    st.plotly_chart(fig8, use_container_width=True)

    st.caption(
        "각 점은 영화 한 편을 나타냅니다. "
        "점에 마우스를 올리면 영화명, 10위권 체류 일수, 총 관객 수를 확인할 수 있습니다."
    )

else:
    st.warning("산점도를 그릴 데이터가 없습니다.")


# ==================================
# 그래프 8 해석
# ==================================
st.markdown("**이 그래프로 알 수 있는 것**")

st.write(
    "영화가 박스오피스 10위권에 머문 날수와 총 관객 수의 관계를 "
    "살펴볼 수 있다. 이를 통해 10위권 체류 기간이 긴 영화에서 "
    "총 관객 수도 높게 나타나는 경향이 있는지 확인할 수 있다. "
    "단, 두 변수의 관계만으로 인과관계를 단정할 수는 없다."
)
