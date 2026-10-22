import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# 앱 제목 설정
st.title("🚇 부산 지하철 역별 이용객 수 지도 분석")
st.write("CSV 파일을 업로드하여 호선별 필터링, 색상 지정, 상위 역 정보를 확인해보세요.")

# ① CSV 파일 업로드
uploaded_file = st.file_uploader("busan_subway.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 업로드된 CSV 파일 읽기
    df = pd.read_csv(uploaded_file)

    # 업로드한 전체 데이터 표로 보여주기
    st.subheader("📊 전체 지하철 데이터 확인")
    st.dataframe(df)

    # [추가] 이용객 상위 5개 역 표 표시
    st.subheader("🏆 이용객 수 상위 5개 역")
    top5_df = df.nlargest(5, '이용객수')[['호선', '역명', '이용객수']]
    st.dataframe(top5_df)

    st.subheader("🗺️ 역별 이용객 수 지도")

    # [추가] 호선 필터 (multiselect)
    available_lines = df['호선'].unique()
    selected_lines = st.multiselect(
        "표시할 호선을 선택하세요",
        options=available_lines,
        default=available_lines  # 기본적으로 모든 호선 선택
    )

    # 선택된 호선만 데이터 필터링
    filtered_df = df[df['호선'].isin(selected_lines)]

    # 부산 중심 좌표(서면역 근처)로 기본 지도 생성
    m = folium.Map(location=[35.1578, 129.0594], zoom_start=11)

    # [추가] 호선별 색상 지정 딕셔너리 (1호선: 주황, 2호선: 초록, 3호선: 갈색, 4호선: 파랑)
    color_dict = {
        '1호선': 'orange',
        '2호선': 'green',
        '3호선': 'brown',
        '4호선': 'blue'
    }

    # ② 필터링된 데이터의 각 행을 순회하며 지도에 CircleMarker 추가
    for index, row in filtered_df.iterrows():
        # 원의 면적이 이용객수에 비례하도록 반지름(radius)을 제곱근(sqrt)으로 설정
        radius_val = np.sqrt(row['이용객수']) * 0.1

        # 호선별 색상 가져오기 (딕셔너리에 없으면 기본값 gray)
        line_color = color_dict.get(row['호선'], 'gray')

        # 지도에 원형 마커 표시
        folium.CircleMarker(
            location=[row['위도'], row['경도']],  # 위도, 경도 좌표
            radius=radius_val,  # 반지름 크기
            color=line_color,  # 테두리 색상 (호선별)
            fill=True,  # 채우기 여부
            fill_color=line_color,  # 채우기 색상 (호선별)
            fill_opacity=0.6,  # 투명도 (0~1)
            tooltip=f"[{row['호선']}] {row['역명']}",  # ③ 마우스 올렸을 때: 호선 및 역명 표시
            popup=f"{row['호선']} {row['역명']}: {row['이용객수']:,}명"  # ③ 클릭했을 때: 이용객 수 표시
        ).add_to(m)

    # Streamlit 화면에 folium 지도 출력
    st_folium(m, width=700, height=500)

else:
    st.info("💡 분석을 시작하려면 `busan_subway.csv` 파일을 먼저 업로드해주세요.")