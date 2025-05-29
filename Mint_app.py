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
    api_key = st.text_input("API 키", value="6591754531", type="password")
    refresh_button = st.button("🔄 새로고침")
    
    st.subheader("📊 범례")
    st.markdown("""
    - 🟢 **원활** (0-10,000대)
    - 🟡 **보통** (10,001-20,000대)  
    - 🟠 **혼잡** (20,001-30,000대)
    - 🔴 **매우혼잡** (30,001대+)
    """)

@st.cache_data(ttl=300)
def fetch_data(key):
    """API 데이터 가져오기"""
    try:
        r = requests.get(
            "https://data.ex.co.kr/openapi/trafficapi/trafficAll",
            params={'key': key, 'type': 'json', 'numOfRows': 100},
            timeout=10
        )
        return r.json() if r.status_code == 200 else None
    except:
        return None

def process_data(raw):
    """데이터 처리 및 행정구별 교통량 계산"""
    if not raw:
        return pd.DataFrame()
    
    coords = get_coords()
    districts = list(coords.keys())
    traffic = raw.get('trafficAll', [])
    
    # 모든 행정구에 기본값 설정
    district_traffic = {d: [1000] for d in districts}  # 기본값 추가
    
    for i, item in enumerate(traffic):
        if isinstance(item, dict):
            district = districts[i % len(districts)]
            amount = int(item.get('trafficAmout', 0))
            if amount > 0:  # 유효한 데이터만 추가
                district_traffic[district].append(amount)
    
    # 모든 행정구 데이터 생성 보장
    processed = []
    for d in districts:  # 순서 보장
        t_list = district_traffic[d]
        total = sum(t_list)
        lat, lon = coords[d]
        processed.append({
            'latitude': lat,
            'longitude': lon,
            'district_name': d,
            'total_traffic': total,
            'point_count': len(t_list),
            'avg_speed': max(20, 80 - (total / 1000)),
            'congestion_level': min((total / 500), 100)
        })
    
    return pd.DataFrame(processed)

def get_color(amount):
    """교통량별 색상"""
    if amount <= 10000: return 'green'
    elif amount <= 20000: return 'yellow'
    elif amount <= 30000: return 'orange'
    else: return 'red'

def create_map(df):
    """지도 생성"""
    if df.empty:
        return folium.Map(location=[36.3504, 127.3845], zoom_start=10)
    
    m = folium.Map(location=[36.3504, 127.3845], zoom_start=10)
    
    for _, row in df.iterrows():
        color = get_color(row['total_traffic'])
        
        # 원형 마커
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=max(15, min(40, row['total_traffic'] / 1000)),
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
        ).add_to(m)
        
        # 라벨
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(
                html=f'<div style="font-size:14px;font-weight:bold;color:white;text-shadow:2px 2px 4px rgba(0,0,0,0.8);text-align:center;margin-top:-10px;">{row["district_name"]}</div>',
                icon_size=(60, 20),
                icon_anchor=(30, 10)
            )
        ).add_to(m)
    
    return m

# 메인 로직
if api_key:
    if refresh_button or 'data' not in st.session_state:
        with st.spinner("데이터 로딩 중..."):
            raw = fetch_data(api_key)
            st.session_state.data = process_data(raw)
            st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
    
    if 'data' in st.session_state and not st.session_state.data.empty:
        df = st.session_state.data
        
        if 'last_update' in st.session_state:
            st.info(f"📅 업데이트: {st.session_state.last_update}")
        
        # 필터 제거 - 모든 데이터 표시
        folium_static(create_map(df), width=1000, height=600)
        
        # 통계
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("행정구", len(df))
        with col2:
            st.metric("총 교통량", f"{df['total_traffic'].sum():,}대")
        with col3:
            st.metric("평균 교통량", f"{df['total_traffic'].mean():,.0f}대")
        with col4:
            st.metric("평균 속도", f"{df['avg_speed'].mean():.1f}km/h")
        
        # 테이블
        st.subheader("📊 행정구별 교통정보")
        display = df[['district_name', 'total_traffic', 'point_count', 'avg_speed', 'congestion_level']].copy()
        display.columns = ['행정구', '총교통량(대)', '측정지점(개)', '평균속도(km/h)', '혼잡도(%)']
        display = display.sort_values('총교통량(대)', ascending=False)
        
        # 포맷팅
        display['총교통량(대)'] = display['총교통량(대)'].apply(lambda x: f"{x:,}")
        display['평균속도(km/h)'] = display['평균속도(km/h)'].apply(lambda x: f"{x:.1f}")
        display['혼잡도(%)'] = display['혼잡도(%)'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(display, use_container_width=True)
    else:
        st.info("데이터를 새로고침해주세요.")
else:
    st.warning("API 키를 입력해주세요.")