import streamlit as st
import os
import json
from google.cloud import vision
from google.oauth2 import service_account
import google.generativeai as genai
import re
import base64
from io import BytesIO

# Planeat 로고 SVG (배포 환경에서도 사용 가능)
PLANEAT_LOGO_SVG = """
<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 원 -->
  <circle cx="25" cy="25" r="24" fill="#FF8C42" stroke="#E67E22" stroke-width="1"/>
  
  <!-- 행성 고리 -->
  <ellipse cx="25" cy="25" rx="18" ry="6" fill="none" stroke="white" stroke-width="2" opacity="0.8"/>
  
  <!-- 행성 본체 -->
  <circle cx="25" cy="25" r="12" fill="#FFB366"/>
  
  <!-- 크레이터/점들 -->
  <circle cx="22" cy="22" r="1.5" fill="#E67E22" opacity="0.6"/>
  <circle cx="28" cy="20" r="1" fill="#E67E22" opacity="0.6"/>
  <circle cx="24" cy="28" r="1.2" fill="#E67E22" opacity="0.6"/>
  <circle cx="30" cy="26" r="0.8" fill="#E67E22" opacity="0.6"/>
  <circle cx="20" cy="28" r="0.9" fill="#E67E22" opacity="0.6"/>
  
  <!-- 포크 -->
  <g transform="translate(35, 15) rotate(25)">
    <rect x="0" y="0" width="1.5" height="12" fill="white" rx="0.7"/>
    <rect x="-1" y="0" width="1" height="4" fill="white" rx="0.5"/>
    <rect x="2.5" y="0" width="1" height="4" fill="white" rx="0.5"/>
    <rect x="-2" y="0" width="0.8" height="3" fill="white" rx="0.4"/>
    <rect x="3.7" y="0" width="0.8" height="3" fill="white" rx="0.4"/>
  </g>
</svg>
"""

# 페이지 기본 설정
st.set_page_config(
    page_title="Planeat - 영수증으로 식단 짜기",
    page_icon="🪐",
    layout="wide"
)

def get_logo_html():
    """로고 HTML을 반환하는 함수"""
    return f'<div style="margin-right: 1rem; display: inline-block;">{PLANEAT_LOGO_SVG}</div>'

# 페이지 스타일 설정
st.markdown("""
<style>
    /* 헤더 스타일링 */
    .main-header {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        background: linear-gradient(45deg, #FF8C42, #E67E22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* 설명 텍스트 스타일링 - 더 잘 보이는 색상으로 변경 */
    .description {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        color: #2C3E50;  /* 어두운 네이비 색상으로 변경 */
        font-weight: 500;  /* 폰트 굵기 추가 */
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);  /* 텍스트 그림자로 가독성 향상 */
        background-color: rgba(255, 255, 255, 0.9);  /* 반투명 흰색 배경 추가 */
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF8C42;  /* 왼쪽 테두리 추가 */
    }

    /* 섹션 제목 스타일링 */
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
    }

    /* 섹션별 색상 스타일 */
    .section-color-1 { 
        color: #FF6B6B; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-2 { 
        color: #4ECDC4; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-3 { 
        color: #45B7D1; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-4 { 
        color: #96CEB4; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }

    /* 영수증 이미지 컨테이너 스타일링 */
    .receipt-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .receipt-image {
        max-width: 400px;
        max-height: 600px;
        width: auto;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 2px solid #e0e0e0;
    }

    /* 버튼 스타일링 - 눌러지기 전 상태 (활성화) */
    .stButton > button {
        background: linear-gradient(45deg, #FF8C42, #E67E22) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(255, 140, 66, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #E67E22, #D35400) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 140, 66, 0.6) !important;
    }

    /* 버튼 비활성화 상태 (눌러진 후) */
    .stButton > button:disabled {
        background: linear-gradient(45deg, #BDC3C7, #95A5A6) !important;
        color: #7F8C8D !important;
        box-shadow: none !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }

    .stButton > button:disabled:hover {
        transform: none !important;
        box-shadow: none !important;
    }

</style>
""", unsafe_allow_html=True)

# 로고와 타이틀을 포함한 헤더
st.markdown(f"""
<div class="main-header">
    {get_logo_html()}
    <h1>Planeat</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="description">
🪐 AI가 당신의 영수증을 분석하여 맞춤형 식단을 제안해드립니다.<br>
구매하신 식재료를 활용한 건강한 식단 구성과 영양 조언을 받아보세요!
</div>

""", unsafe_allow_html=True)

# Gemini API 인증 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Gemini API 인증 오류: {e}")

# Google Cloud Vision API 서비스 계정 키 로드
vision_client = None
try:
    service_account_info = json.loads(st.secrets["GOOGLE_CLOUD_VISION_API_KEY_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
except KeyError:
    st.info("Google Cloud Vision API 서비스 계정 키가 secrets.toml에 'GOOGLE_CLOUD_VISION_API_KEY_JSON'으로 설정되어 있지 않습니다.")
except json.JSONDecodeError:
    st.error("secrets.toml에 있는 Google Cloud Vision API 키가 올바른 JSON 형식이 아닙니다. JSON 형식을 확인해주세요.")
except Exception as e:
    st.error(f"Google Cloud Vision API 클라이언트 초기화 중 오류가 발생했습니다: {e}")

def extract_text_from_image(image_bytes):
    """영수증 이미지에서 텍스트를 추출하는 함수"""
    if not vision_client:
        st.error("Vision API 클라이언트가 초기화되지 않았습니다. API 키 설정을 확인해주세요.")
        return None
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)
        if response.error.message:
            raise Exception(response.error.message)
        
        texts = response.text_annotations
        if texts:
            return texts[0].description  # 전체 텍스트
        return ""
    except Exception as e:
        st.error(f"이미지 텍스트 추출 중 오류가 발생했습니다: {e}")
        return None

def generate_meal_plan_prompt(gender, height, weight, goal, receipt_text):
    """식단 계획을 위한 프롬프트 생성 함수"""
    prompt = f"""
사용자 정보:
- 성별: {gender}
- 신장: {height}cm
- 체중: {weight}kg
- 건강 목표: {goal}

영수증 내용:
{receipt_text}

다음 형식으로 분석해주세요. 각 섹션의 제목은 그대로 유지하고, 내용은 Markdown 형식으로 작성해주세요:

[1. 영수증 식재료 요약]
### 오늘 구매한 식재료 목록:
- (식재료 1) 
- (식재료 2) 
- (식재료 3) 

### 🛒 오늘의 구매 점수 : XX/100

### 단백질 점수: 🥩 XX/100
- 구매한 식재료 중 단백질이 풍부한 재료: (재료명)

### 탄수화물 점수: 🍚 XX/100
- 구매한 식재료 중 탄수화물이 풍부한 재료: (재료명)

### 지방 점수: 🥑 XX/100
- 구매한 식재료 중 건강한 지방이 풍부한 재료: (재료명)

### 비타민/무기질 점수: 🥬 XX/100
- 구매한 식재료 중 비타민과 무기질이 풍부한 재료: (재료명)

[2. 맞춤형 식단 제안 🍽️]
### 아침:
- (메뉴 1) ,(메뉴 2) 

### 점심:
- (메뉴 1) ,(메뉴 2) 

### 저녁:
- (메뉴 1) ,(메뉴 2) 

[3. 영양소 분석 및 개선 포인트 💪]
### ⭕ 현재 식단의 강점:
- (강점 1) 
- (강점 2) 
- (강점 3) 

### ❌ 부족한 영양소:
- (부족 영양소 1) 
- (부족 영양소 2) 
- (부족 영양소 3) 

### 건강 목표 달성을 위한 개선 필요 사항:
- (개선사항 1) 
- (개선사항 2) 
- (개선사항 3) 

[4. 점수 UP! 추가 제안 🚀]
### 다음 장보기 시 구매 추천 식재료:
- (추천 식재료 1) 
- (추천 식재료 2) 
- (추천 식재료 3) 

### 영양제 추천:
- (추천 영양제 1) 
- (추천 영양제 2) 

### 개선 시 예상 추가 점수: +XX점

모든 답변은 간결하고 전문적이지만, 일반인이 이해하기 쉬운 용어로 작성해주세요.
"""
    return prompt

def parse_gemini_response(response):
    """Gemini 응답을 파싱하는 함수"""
    try:
        sections = re.split(r'(\[\d+\.\s.*?\])', response)
        parsed = []
        i = 1
        while i < len(sections):
            if re.match(r'\[\d+\.\s.*?\]', sections[i]):
                title = sections[i]
                content = sections[i+1] if i+1 < len(sections) else ''
                parsed.append((title, content.strip()))
                i += 2
            else:
                i += 1
        return parsed
    except Exception as e:
        st.error(f"응답 파싱 중 오류가 발생했습니다: {e}")
        return None

def ask_gemini(prompt):
    """Gemini API 호출 함수"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text') and response.text:
            return response.text
        else:
            st.warning("Gemini API 응답이 비어있습니다. 다시 시도해 주세요.")
            return None
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")
        return None

# 메인 UI

# 사용자 정보 입력
st.markdown('<h2 class="section-title">1️⃣ 기본 정보 입력</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    gender = st.selectbox("성별", ["남성", "여성"])
with col2:
    height = st.number_input("신장 (cm)", min_value=0.0, step=0.1)
with col3:
    weight = st.number_input("체중 (kg)", min_value=0.0, step=0.1)
with col4:
    goal = st.selectbox("건강 목표", ["다이어트", "근육 증가", "건강 유지", "체중 증가"])

# 영수증 이미지 업로드
st.markdown('<h2 class="section-title">2️⃣ 영수증 이미지 업로드</h2>', unsafe_allow_html=True)
receipt_image = st.file_uploader("영수증 이미지를 업로드해주세요", type=["jpg", "jpeg", "png"])

extracted_text_global = None
analysis_completed = False

if receipt_image is not None:
    # 이미지를 적절한 크기로 표시
    st.markdown('<div class="receipt-container">', unsafe_allow_html=True)
    st.image(receipt_image, caption="📄 업로드된 영수증", use_container_width=False, width=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 이미지에서 텍스트 추출 시도
    receipt_bytes = receipt_image.getvalue()
    extracted_text_global = extract_text_from_image(receipt_bytes)
    
    if not extracted_text_global:
        st.error("영수증 텍스트를 추출할 수 없습니다. 다른 이미지를 시도해보세요.")

# 분석 완료 상태를 session_state로 관리
if 'analysis_completed' not in st.session_state:
    st.session_state.analysis_completed = False

# 버튼 활성화 조건 체크
button_enabled = (extracted_text_global is not None and 
                 extracted_text_global.strip() and 
                 gender and height > 0 and weight > 0 and goal and 
                 not st.session_state.analysis_completed)

# 분석 시작 버튼
if st.button("🔍 식단 분석 시작", disabled=not button_enabled):
    if not (gender and height > 0 and weight > 0 and goal):
        st.warning("모든 기본 정보를 입력해주세요.")
    elif not extracted_text_global.strip():
        st.warning("영수증 텍스트가 인식되지 않았습니다. 유효한 영수증 이미지를 업로드해주세요.")
    else:
        with st.spinner("🪐 AI가 영수증을 분석하고 맞춤형 식단을 생성하고 있습니다..."):
            prompt = generate_meal_plan_prompt(gender, height, weight, goal, extracted_text_global)
            response = ask_gemini(prompt)
            
            if response:
                st.session_state.analysis_completed = True
                st.session_state.analysis_result = response
                st.rerun()

# 분석 결과 표시
if st.session_state.analysis_completed and 'analysis_result' in st.session_state:
    st.markdown('<h2 class="section-title">3️⃣ AI 식단 분석 결과</h2>', unsafe_allow_html=True)
    response = st.session_state.analysis_result
    
    parsed_sections = parse_gemini_response(response)
    if parsed_sections:
        color_map = {
            "[1. 영수증 식재료 요약]": "section-color-1",
            "[2. 맞춤형 식단 제안 🍽️]": "section-color-2",
            "[3. 영양소 분석 및 개선 포인트 💪]": "section-color-3",
            "[4. 점수 UP! 추가 제안 🚀]": "section-color-4",
        }
        
        for title, content in parsed_sections:
            color_class = color_map.get(title, "")
            
            # 섹션 제목 표시
            title_html = f'<div class="{color_class}">{title}</div>'
            st.markdown(title_html, unsafe_allow_html=True)
            
            # expander 내용 표시
            with st.expander("자세히 보기", expanded=True if "영수증 식재료 요약" in title else False):
                st.markdown(content)
                st.markdown("---")
    else:
        st.warning("AI 응답을 파싱하는 데 실패했습니다. 원본 응답을 표시합니다.")
        st.markdown(response)import streamlit as st
import os
import json
from google.cloud import vision
from google.oauth2 import service_account
import google.generativeai as genai
import re
import base64
from io import BytesIO

# Planeat 로고 SVG (배포 환경에서도 사용 가능)
PLANEAT_LOGO_SVG = """
<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
  <!-- 배경 원 -->
  <circle cx="25" cy="25" r="24" fill="#FF8C42" stroke="#E67E22" stroke-width="1"/>
  
  <!-- 행성 고리 -->
  <ellipse cx="25" cy="25" rx="18" ry="6" fill="none" stroke="white" stroke-width="2" opacity="0.8"/>
  
  <!-- 행성 본체 -->
  <circle cx="25" cy="25" r="12" fill="#FFB366"/>
  
  <!-- 크레이터/점들 -->
  <circle cx="22" cy="22" r="1.5" fill="#E67E22" opacity="0.6"/>
  <circle cx="28" cy="20" r="1" fill="#E67E22" opacity="0.6"/>
  <circle cx="24" cy="28" r="1.2" fill="#E67E22" opacity="0.6"/>
  <circle cx="30" cy="26" r="0.8" fill="#E67E22" opacity="0.6"/>
  <circle cx="20" cy="28" r="0.9" fill="#E67E22" opacity="0.6"/>
  
  <!-- 포크 -->
  <g transform="translate(35, 15) rotate(25)">
    <rect x="0" y="0" width="1.5" height="12" fill="white" rx="0.7"/>
    <rect x="-1" y="0" width="1" height="4" fill="white" rx="0.5"/>
    <rect x="2.5" y="0" width="1" height="4" fill="white" rx="0.5"/>
    <rect x="-2" y="0" width="0.8" height="3" fill="white" rx="0.4"/>
    <rect x="3.7" y="0" width="0.8" height="3" fill="white" rx="0.4"/>
  </g>
</svg>
"""

# 페이지 기본 설정
st.set_page_config(
    page_title="Planeat - 영수증으로 식단 짜기",
    page_icon="🪐",
    layout="wide"
)

def get_logo_html():
    """로고 HTML을 반환하는 함수"""
    return f'<div style="margin-right: 1rem; display: inline-block;">{PLANEAT_LOGO_SVG}</div>'

# 페이지 스타일 설정
st.markdown("""
<style>
    /* 헤더 스타일링 */
    .main-header {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        background: linear-gradient(45deg, #FF8C42, #E67E22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* 설명 텍스트 스타일링 - 더 잘 보이는 색상으로 변경 */
    .description {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        color: #2C3E50;  /* 어두운 네이비 색상으로 변경 */
        font-weight: 500;  /* 폰트 굵기 추가 */
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);  /* 텍스트 그림자로 가독성 향상 */
        background-color: rgba(255, 255, 255, 0.9);  /* 반투명 흰색 배경 추가 */
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF8C42;  /* 왼쪽 테두리 추가 */
    }

    /* 섹션 제목 스타일링 */
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
    }

    /* 섹션별 색상 스타일 */
    .section-color-1 { 
        color: #FF6B6B; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-2 { 
        color: #4ECDC4; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-3 { 
        color: #45B7D1; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .section-color-4 { 
        color: #96CEB4; 
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0;
    }

    /* 영수증 이미지 컨테이너 스타일링 */
    .receipt-container {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .receipt-image {
        max-width: 400px;
        max-height: 600px;
        width: auto;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 2px solid #e0e0e0;
    }

    /* 버튼 스타일링 - 눌러지기 전 상태 (활성화) */
    .stButton > button {
        background: linear-gradient(45deg, #FF8C42, #E67E22) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(255, 140, 66, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #E67E22, #D35400) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 140, 66, 0.6) !important;
    }

    /* 버튼 비활성화 상태 (눌러진 후) */
    .stButton > button:disabled {
        background: linear-gradient(45deg, #BDC3C7, #95A5A6) !important;
        color: #7F8C8D !important;
        box-shadow: none !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }

    .stButton > button:disabled:hover {
        transform: none !important;
        box-shadow: none !important;
    }

</style>
""", unsafe_allow_html=True)

# 로고와 타이틀을 포함한 헤더
st.markdown(f"""
<div class="main-header">
    {get_logo_html()}
    <h1>Planeat</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="description">
🪐 AI가 당신의 영수증을 분석하여 맞춤형 식단을 제안해드립니다.<br>
구매하신 식재료를 활용한 건강한 식단 구성과 영양 조언을 받아보세요!
</div>

""", unsafe_allow_html=True)

# Gemini API 인증 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Gemini API 인증 오류: {e}")

# Google Cloud Vision API 서비스 계정 키 로드
vision_client = None
try:
    service_account_info = json.loads(st.secrets["GOOGLE_CLOUD_VISION_API_KEY_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
except KeyError:
    st.info("Google Cloud Vision API 서비스 계정 키가 secrets.toml에 'GOOGLE_CLOUD_VISION_API_KEY_JSON'으로 설정되어 있지 않습니다.")
except json.JSONDecodeError:
    st.error("secrets.toml에 있는 Google Cloud Vision API 키가 올바른 JSON 형식이 아닙니다. JSON 형식을 확인해주세요.")
except Exception as e:
    st.error(f"Google Cloud Vision API 클라이언트 초기화 중 오류가 발생했습니다: {e}")

def extract_text_from_image(image_bytes):
    """영수증 이미지에서 텍스트를 추출하는 함수"""
    if not vision_client:
        st.error("Vision API 클라이언트가 초기화되지 않았습니다. API 키 설정을 확인해주세요.")
        return None
    try:
        image = vision.Image(content=image_bytes)
        response = vision_client.text_detection(image=image)
        if response.error.message:
            raise Exception(response.error.message)
        
        texts = response.text_annotations
        if texts:
            return texts[0].description  # 전체 텍스트
        return ""
    except Exception as e:
        st.error(f"이미지 텍스트 추출 중 오류가 발생했습니다: {e}")
        return None

def generate_meal_plan_prompt(gender, height, weight, goal, receipt_text):
    """식단 계획을 위한 프롬프트 생성 함수"""
    prompt = f"""
사용자 정보:
- 성별: {gender}
- 신장: {height}cm
- 체중: {weight}kg
- 건강 목표: {goal}

영수증 내용:
{receipt_text}

다음 형식으로 분석해주세요. 각 섹션의 제목은 그대로 유지하고, 내용은 Markdown 형식으로 작성해주세요:

[1. 영수증 식재료 요약]
### 오늘 구매한 식재료 목록:
- (식재료 1) 
- (식재료 2) 
- (식재료 3) 

### 🛒 오늘의 구매 점수 : XX/100

### 단백질 점수: 🥩 XX/100
- 구매한 식재료 중 단백질이 풍부한 재료: (재료명)

### 탄수화물 점수: 🍚 XX/100
- 구매한 식재료 중 탄수화물이 풍부한 재료: (재료명)

### 지방 점수: 🥑 XX/100
- 구매한 식재료 중 건강한 지방이 풍부한 재료: (재료명)

### 비타민/무기질 점수: 🥬 XX/100
- 구매한 식재료 중 비타민과 무기질이 풍부한 재료: (재료명)

[2. 맞춤형 식단 제안 🍽️]
### 아침:
- (메뉴 1) ,(메뉴 2) 

### 점심:
- (메뉴 1) ,(메뉴 2) 

### 저녁:
- (메뉴 1) ,(메뉴 2) 

[3. 영양소 분석 및 개선 포인트 💪]
### ⭕ 현재 식단의 강점:
- (강점 1) 
- (강점 2) 
- (강점 3) 

### ❌ 부족한 영양소:
- (부족 영양소 1) 
- (부족 영양소 2) 
- (부족 영양소 3) 

### 건강 목표 달성을 위한 개선 필요 사항:
- (개선사항 1) 
- (개선사항 2) 
- (개선사항 3) 

[4. 점수 UP! 추가 제안 🚀]
### 다음 장보기 시 구매 추천 식재료:
- (추천 식재료 1) 
- (추천 식재료 2) 
- (추천 식재료 3) 

### 영양제 추천:
- (추천 영양제 1) 
- (추천 영양제 2) 

### 개선 시 예상 추가 점수: +XX점

모든 답변은 간결하고 전문적이지만, 일반인이 이해하기 쉬운 용어로 작성해주세요.
"""
    return prompt

def parse_gemini_response(response):
    """Gemini 응답을 파싱하는 함수"""
    try:
        sections = re.split(r'(\[\d+\.\s.*?\])', response)
        parsed = []
        i = 1
        while i < len(sections):
            if re.match(r'\[\d+\.\s.*?\]', sections[i]):
                title = sections[i]
                content = sections[i+1] if i+1 < len(sections) else ''
                parsed.append((title, content.strip()))
                i += 2
            else:
                i += 1
        return parsed
    except Exception as e:
        st.error(f"응답 파싱 중 오류가 발생했습니다: {e}")
        return None

def ask_gemini(prompt):
    """Gemini API 호출 함수"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text') and response.text:
            return response.text
        else:
            st.warning("Gemini API 응답이 비어있습니다. 다시 시도해 주세요.")
            return None
    except Exception as e:
        st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")
        return None

# 메인 UI

# 사용자 정보 입력
st.markdown('<h2 class="section-title">1️⃣ 기본 정보 입력</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    gender = st.selectbox("성별", ["남성", "여성"])
with col2:
    height = st.number_input("신장 (cm)", min_value=0.0, step=0.1)
with col3:
    weight = st.number_input("체중 (kg)", min_value=0.0, step=0.1)
with col4:
    goal = st.selectbox("건강 목표", ["다이어트", "근육 증가", "건강 유지", "체중 증가"])

# 영수증 이미지 업로드
st.markdown('<h2 class="section-title">2️⃣ 영수증 이미지 업로드</h2>', unsafe_allow_html=True)
receipt_image = st.file_uploader("영수증 이미지를 업로드해주세요", type=["jpg", "jpeg", "png"])

extracted_text_global = None
analysis_completed = False

if receipt_image is not None:
    # 이미지를 적절한 크기로 표시
    st.markdown('<div class="receipt-container">', unsafe_allow_html=True)
    st.image(receipt_image, caption="📄 업로드된 영수증", use_container_width=False, width=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 이미지에서 텍스트 추출 시도
    receipt_bytes = receipt_image.getvalue()
    extracted_text_global = extract_text_from_image(receipt_bytes)
    
    if not extracted_text_global:
        st.error("영수증 텍스트를 추출할 수 없습니다. 다른 이미지를 시도해보세요.")

# 분석 완료 상태를 session_state로 관리
if 'analysis_completed' not in st.session_state:
    st.session_state.analysis_completed = False

# 버튼 활성화 조건 체크
button_enabled = (extracted_text_global is not None and 
                 extracted_text_global.strip() and 
                 gender and height > 0 and weight > 0 and goal and 
                 not st.session_state.analysis_completed)

# 분석 시작 버튼
if st.button("🔍 식단 분석 시작", disabled=not button_enabled):
    if not (gender and height > 0 and weight > 0 and goal):
        st.warning("모든 기본 정보를 입력해주세요.")
    elif not extracted_text_global.strip():
        st.warning("영수증 텍스트가 인식되지 않았습니다. 유효한 영수증 이미지를 업로드해주세요.")
    else:
        with st.spinner("🪐 AI가 영수증을 분석하고 맞춤형 식단을 생성하고 있습니다..."):
            prompt = generate_meal_plan_prompt(gender, height, weight, goal, extracted_text_global)
            response = ask_gemini(prompt)
            
            if response:
                st.session_state.analysis_completed = True
                st.session_state.analysis_result = response
                st.rerun()

# 분석 결과 표시
if st.session_state.analysis_completed and 'analysis_result' in st.session_state:
    st.markdown('<h2 class="section-title">3️⃣ AI 식단 분석 결과</h2>', unsafe_allow_html=True)
    response = st.session_state.analysis_result
    
    parsed_sections = parse_gemini_response(response)
    if parsed_sections:
        color_map = {
            "[1. 영수증 식재료 요약]": "section-color-1",
            "[2. 맞춤형 식단 제안 🍽️]": "section-color-2",
            "[3. 영양소 분석 및 개선 포인트 💪]": "section-color-3",
            "[4. 점수 UP! 추가 제안 🚀]": "section-color-4",
        }
        
        for title, content in parsed_sections:
            color_class = color_map.get(title, "")
            
            # 섹션 제목 표시
            title_html = f'<div class="{color_class}">{title}</div>'
            st.markdown(title_html, unsafe_allow_html=True)
            
            # expander 내용 표시
            with st.expander("자세히 보기", expanded=True if "영수증 식재료 요약" in title else False):
                st.markdown(content)
                st.markdown("---")
    else:
        st.warning("AI 응답을 파싱하는 데 실패했습니다. 원본 응답을 표시합니다.")
        st.markdown(response)
