
# ----------------------------------
# 그래프 7. 제작 국가 → 장르 선버스트
# ----------------------------------
st.divider()
st.header("그래프 7. 제작 국가별 장르 분포")

sunburst_df = df.dropna(
    subset=["nation", "genre", "movieNm"]
).copy()

# 국가 및 장르 데이터 정리
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

# 국가-장르별 영화 편수 계산
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
        title="제작 국가별 장르 구성",
        labels={
            "nation": "제작 국가",
            "genre": "장르",
            "영화 편수": "영화 편수"
        }
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
        "영역의 크기는 영화 편수에 비례하며, "
        "국가 영역을 클릭하면 해당 국가의 장르 구성을 확대해 볼 수 있습니다."
    )

else:
    st.warning("선버스트 그래프를 그릴 데이터가 없습니다.")

st.markdown("**이 그래프로 알 수 있는 것**")
st.write(
    "제작 국가별 영화 편수와 각 국가에 포함된 장르의 구성을 "
    "한눈에 비교하여, 국가별 장르 분포의 차이를 파악할 수 있다."
)
