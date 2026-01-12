# 간호사 AI 상담사 앱

의사의 진료 내용을 환자와 보호자가 이해하기 쉽게 설명해주는 AI 간호사 챗봇입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

### 로컬 환경

1. `.env` 파일 생성:
   - `.env.example` 파일을 참고하여 `.env` 파일을 생성하세요.
   - 또는 다음 명령어로 생성:
   ```bash
   echo OPENAI_API_KEY=your-api-key-here > .env
   ```

2. Streamlit 앱 실행:
```bash
streamlit run nurseapp.py
```

### Colab 환경

1. Colab의 userdata에 `OPENAI_API_KEY` 저장
2. 노트북에서 실행:
```python
!streamlit run nurseapp.py --server.port=8501 --server.address=0.0.0.0
```

## 보안 주의사항

- ⚠️ `.env` 파일은 절대 Git에 커밋하지 마세요!
- `.gitignore`에 `.env`가 포함되어 있습니다.
- API 키를 공유하거나 공개 저장소에 업로드하지 마세요.

## 파일 구조

```
.
├── nurseapp.py          # 메인 앱 파일
├── .env                 # API 키 (로컬에서만 사용, Git에 포함 안됨)
├── .env.example         # .env 파일 템플릿
├── .gitignore           # Git 제외 파일 목록
├── requirements.txt     # 필요한 패키지 목록
└── nurse.png            # 간호사 이미지
```
