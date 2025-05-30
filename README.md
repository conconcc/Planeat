# 🪐 Planeat - AI 영수증 기반 맞춤형 식단 분석 서비스

![Planeat Logo](https://img.shields.io/badge/Planeat-AI%20Diet%20Coach-FF8C42?style=for-the-badge&logo=nutrition&logoColor=white)

## 📋 프로젝트 소개

**Planeat**은 영수증 사진만으로 AI가 개인 맞춤형 식단을 분석하고 건강한 라이프스타일을 제안하는 스마트 헬스케어 서비스입니다.

바쁜 현대인들이 쉽게 자신의 식습관을 점검하고 개선할 수 있도록, 복잡한 영양 계산 없이도 전문적인 건강 조언을 받을 수 있습니다.

### 🎯 핵심 기능

- 📸 **영수증 OCR 분석**: Google Cloud Vision API로 영수증 텍스트 자동 인식
- 🤖 **AI 맞춤 분석**: Gemini AI가 개인 정보 기반 식단 평가 및 조언 제공
- 📊 **영양소 점수화**: 단백질, 탄수화물, 지방, 비타민 등 4개 영역별 점수 제공
- 🍽️ **개인화 식단 제안**: 성별, 체중, 건강 목표에 따른 맞춤형 식단 추천
- 💊 **영양제 추천**: 부족한 영양소 기반 영양제 및 식품 추천
- 🎨 **직관적 UI/UX**: Streamlit 기반 반응형 웹 인터페이스

## 🛠️ 기술 스택

### **Frontend**
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### **Backend & AI**
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini%20AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)

### **APIs & Services**
- **Google Cloud Vision API**: 영수증 텍스트 추출 (OCR)
- **Google Gemini API**: AI 기반 식단 분석 및 추천
- **Google AI Studio**: AI 모델 프롬프트 설계 및 테스트

## 📸 서비스 미리보기

### 메인 화면
- 🪐 커스텀 SVG 로고와 그라데이션 디자인
- 직관적인 4단계 사용자 정보 입력 폼

### 분석 결과 화면
- 📊 4개 영역별 영양소 점수 (100점 만점)
- 🍽️ 아침/점심/저녁 맞춤형 식단 제안
- 💪 개인 건강 목표 기반 개선 포인트 제시
- 🚀 추가 구매 추천 식재료 및 영양제 정보

## 🚀 시작하기

### 필수 조건

```bash
Python 3.8+
Streamlit
Google Cloud Vision API 계정
Google Gemini API 키
```

### 설치 및 실행

1. **레포지토리 클론**
```bash
git clone https://github.com/your-username/planeat.git
cd planeat
```

2. **의존성 설치**
```bash
pip install streamlit google-cloud-vision google-generativeai
```

3. **API 키 설정**
`.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
GOOGLE_CLOUD_VISION_API_KEY_JSON = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "your-private-key",
  "client_email": "your-client-email",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
'''
```

4. **애플리케이션 실행**
```bash
streamlit run app.py
```

## 💡 사용 방법

### 1단계: 기본 정보 입력
- 성별, 신장(cm), 체중(kg) 입력
- 건강 목표 선택 (다이어트/근육증가/건강유지/체중증가)

### 2단계: 영수증 업로드
- JPG, PNG 형식의 영수증 이미지 업로드
- AI가 자동으로 텍스트 인식 및 식재료 추출

### 3단계: AI 분석 실행
- "🔍 식단 분석 시작" 버튼 클릭
- 약 10-15초 후 상세 분석 결과 확인

### 4단계: 결과 확인 및 활용
- 4개 섹션별 상세 분석 결과 확인
- 개선점 및 추천사항 적용

## 🏗️ 프로젝트 구조

```
planeat/
├── app.py                 # 메인 Streamlit 애플리케이션
├── .streamlit/
│   └── secrets.toml       # API 키 설정 파일
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 문서
```

## 🎨 주요 기능 상세

### OCR 텍스트 추출
```python
def extract_text_from_image(image_bytes):
    """Google Cloud Vision API를 사용한 영수증 텍스트 추출"""
    image = vision.Image(content=image_bytes)
    response = vision_client.text_detection(image=image)
    return response.text_annotations[0].description
```

### AI 프롬프트 엔지니어링
- 구조화된 4단계 분석 프롬프트 설계
- 개인 맞춤형 변수 (성별, 체중, 목표) 반영
- 100점 만점 점수 시스템으로 직관적 피드백

### 반응형 UI 컴포넌트
- CSS 그라데이션 및 호버 효과
- 모바일 친화적 반응형 레이아웃
- 색상별 구분된 분석 섹션

## 👥 팀 구성
| 역할 | 이름 | GitHub | 담당 업무 |
|------|------|--------|-----------|
| 🎨 **Design & Backend Lead** | 정해찬 | [@gocks77777](https://github.com/gocks77777) | 페이지 디자인, 로고 제작, 이미지 및 데이터 입출력 기능 구현, 프롬프트 엔지니어링 |
| 🔧 **Frontend & AI Lead** | 이승준 | [@conconcc](https://github.com/conconcc) | 프론트엔드 구현, 이미지 인식 및 추출 기능 구현, 프롬프트 엔지니어링, API 연동, 배포 관리 |

## 🚀 배포 및 운영

- **플랫폼**: Streamlit Cloud
- **도메인**: https://planeat-vsdh5tre5diksg39je685i.streamlit.app/
- **모니터링**: Streamlit 내장 분석 도구

## 🔮 향후 개발 계획

### Phase 2: 고도화 기능
- [ ] 📅 주간/월간 식습관 트래킹 기능
- [ ] 🍎 음식 사진 직접 분석 기능
- [ ] 👥 가족/친구와 식단 공유 기능
- [ ] 📊 개인 건강 데이터 시각화 대시보드

### Phase 3: 모바일 확장
- [ ] 📱 모바일 앱 개발 (React Native)
- [ ] 🔔 식사 시간 알림 기능
- [ ] 🏪 근처 건강식품점 추천

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 문제 해결

### 자주 발생하는 오류

**Q: "Vision API 클라이언트가 초기화되지 않았습니다" 오류**
```bash
A: secrets.toml 파일의 GOOGLE_CLOUD_VISION_API_KEY_JSON 설정을 확인하세요.
```

**Q: "Gemini API 인증 오류" 발생 시**
```bash
A: GEMINI_API_KEY가 올바르게 설정되었는지 확인하세요.
```

**Q: 영수증 텍스트가 인식되지 않을 때**
```bash
A: 명확하고 선명한 영수증 이미지를 사용해주세요. (권장: 600x800px 이상)
```

## 📞 연락처

**프로젝트 문의**: 
- 정해찬: gocks77777@github.com
- 이승준: conconcc@github.com

**프로젝트 링크**: [https://github.com/your-username/planeat](https://github.com/your-username/planeat)

---

⭐ **Planeat으로 더 건강한 식습관을 만들어보세요!** ⭐
