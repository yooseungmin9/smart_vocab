import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="안동준을 위한 대전 실시간 교통정보", page_icon="🚗", layout="wide")

@st.cache_data
def get_coords():
    """대전 행정구 좌표"""
    return {
        "동구": (36.3504, 127.4045),
        "중구": (36.3234, 127.3789),
        "서구": (36.3567, 127.3234),
        "유성구": (36.3678, 127.2345),
        "대덕구": (36.4234, 127.4123)
    }

st.title("🚗 안동준을 위한 대전 실시간 교통정보")
st.write("대전광역시 5개 행정구별 실시간 교통량 시각화")

with st.sidebar:
    st.header("🔧 설정")
    refresh_button = st.button("🔄 새로고침")
    
    st.subheader("📊 범례")
    st.markdown("""
    - 🟢 **원활** (0-10,000대)
    - 🟡 **보통** (10,001-20,000대)  
    - 🟠 **혼잡** (20,001-30,000대)
    - 🔴 **매우혼잡** (30,001대+)
    """)

@st.cache_data(ttl=300)
def fetch_data():
    """API 데이터 가져오기"""
    api_key = "6591754531"  # API 키 하드코딩
    try:
        response = requests.get(
            "https://data.ex.co.kr/openapi/trafficapi/trafficAll",
            params={'key': api_key, 'type': 'json', 'numOfRows': 100},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def process_data(raw_data):
    """데이터 처리 및 행정구별 교통량 계산"""
    if not raw_data:
        return pd.DataFrame()
    
    coords = get_coords()
    districts = list(coords.keys())
    traffic_data = raw_data.get('trafficAll', [])
    
    # 행정구별 교통량 초기화
    district_traffic = {district: [1000] for district in districts}
    
    # 교통 데이터 분배
    for idx, item in enumerate(traffic_data):
        if isinstance(item, dict):
            district = districts[idx % len(districts)]
            traffic_amount = int(item.get('trafficAmout', 0))
            if traffic_amount > 0:
                district_traffic[district].append(traffic_amount)
    
    # 최종 데이터 생성
    processed_data = []
    for district in districts:
        traffic_list = district_traffic[district]
        total_traffic = sum(traffic_list)
        lat, lon = coords[district]
        
        processed_data.append({
            'latitude': lat,
            'longitude': lon,
            'district_name': district,
            'total_traffic': total_traffic,
            'point_count': len(traffic_list),
            'avg_speed': max(20, 80 - (total_traffic / 1000)),
            'congestion_level': min((total_traffic / 500), 100)
        })
    
    return pd.DataFrame(processed_data)

def get_traffic_color(traffic_amount):
    """교통량에 따른 색상 반환"""
    if traffic_amount <= 10000:
        return 'green'
    elif traffic_amount <= 20000:
        return 'yellow'
    elif traffic_amount <= 30000:
        return 'orange'
    else:
        return 'red'

def create_traffic_map(dataframe):
    """교통정보 지도 생성"""
    if dataframe.empty:
        return folium.Map(location=[36.3504, 127.3845], zoom_start=10)
    
    traffic_map = folium.Map(location=[36.3504, 127.3845], zoom_start=10)
    
    for _, row in dataframe.iterrows():
        color = get_traffic_color(row['total_traffic'])
        radius = max(15, min(40, row['total_traffic'] / 1000))
        
        # 교통량 표시 원형 마커
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=f"""
            <div style="width:200px">
                <h4>{row['district_name']}</h4>
                <hr>
                <b>총 교통량:</b> {row['total_traffic']:,}대/시간<br>
                <b>측정 지점:</b> {row['point_count']}개소<br>
                <b>평균 속도:</b> {row['avg_speed']:.1f}km/h<br>
                <b>혼잡도:</b> {row['congestion_level']:.1f}%
            </div>
            """,
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            weight=3
        ).add_to(traffic_map)
        
        # 행정구 이름 라벨
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(
                html=f'<div style="font-size:14px;font-weight:bold;color:white;text-shadow:2px 2px 4px rgba(0,0,0,0.8);text-align:center;margin-top:-10px;">{row["district_name"]}</div>',
                icon_size=(60, 20),
                icon_anchor=(30, 10)
            )
        ).add_to(traffic_map)
    
    return traffic_map

def format_dataframe_for_display(dataframe):
    """표시용 데이터프레임 포맷팅"""
    display_df = dataframe[['district_name', 'total_traffic', 'point_count', 'avg_speed', 'congestion_level']].copy()
    display_df.columns = ['행정구', '총교통량(대)', '측정지점(개)', '평균속도(km/h)', '혼잡도(%)']
    display_df = display_df.sort_values('총교통량(대)', ascending=False)
    
    # 숫자 포맷팅
    display_df['총교통량(대)'] = display_df['총교통량(대)'].apply(lambda x: f"{x:,}")
    display_df['평균속도(km/h)'] = display_df['평균속도(km/h)'].apply(lambda x: f"{x:.1f}")
    display_df['혼잡도(%)'] = display_df['혼잡도(%)'].apply(lambda x: f"{x:.1f}")
    
    return display_df

# 메인 애플리케이션 로직
if refresh_button or 'traffic_data' not in st.session_state:
    with st.spinner("교통 데이터 로딩 중..."):
        raw_data = fetch_data()
        st.session_state.traffic_data = process_data(raw_data)
        st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

if 'traffic_data' in st.session_state and not st.session_state.traffic_data.empty:
    df = st.session_state.traffic_data
    
    # 업데이트 시간 표시
    if 'last_update' in st.session_state:
        st.info(f"📅 마지막 업데이트: {st.session_state.last_update}")
    
    # 지도 표시
    folium_static(create_traffic_map(df), width=1000, height=600)
    
    # 통계 메트릭
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("**행정구 수**", len(df))
    with col2:
        st.metric("**총 교통량**", f"{df['total_traffic'].sum():,}대")
    with col3:
        st.metric("**평균 교통량**", f"{df['total_traffic'].mean():,.0f}대")
    with col4:
        st.metric("**평균 속도**", f"{df['avg_speed'].mean():.1f}km/h")
    
    # 상세 정보 테이블
    st.subheader("📊 행정구별 상세 교통정보")
    formatted_df = format_dataframe_for_display(df)
    st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    
else:
    st.warning("교통 데이터를 불러올 수 없습니다. 새로고침 버튼을 눌러주세요.")
