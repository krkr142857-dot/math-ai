import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

# 2. API 보안 연결
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ API 키 연결 실패: {e}")
    st.stop()

# 3. 세션 상태 관리
if 'problem_data' not in st.session_state: st.session_state.problem_data = None
if 'user_answer' not in st.session_state: st.session_state.user_answer = ""
if 'grade_status' not in st.session_state: st.session_state.grade_status = None
if 'ai_feedback' not in st.session_state: st.session_state.ai_feedback = ""

# 학년 및 단원 데이터
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년": ["대수", "미적분I", "확률과 통계", "기하"]
}

# --- [1분할: 사이드바] ---
with st.sidebar:
    st.title("🎓 설정 및 출제")
    sel_grade = st.selectbox("학년 선택", list(curriculum.keys()))
    sel_unit = st.selectbox("단원 선택", curriculum[sel_grade])
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(심화)", "1등급(고난도)"]
    sel_diff = st.select_slider("목표 등급 선택", options=diff_labels)
    sel_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    
    if st.button("✨ 새 문제 생성", type="primary"):
        with st.spinner('AI가 문제를 설계 중입니다...'):
            try:
                # 사용 가능한 모델 자동 탐색
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_model = next((m for m in available_models if "gemini-1.5-flash" in m), "models/gemini-1.5-flash")
                
                model = genai.GenerativeModel(target_model)
                
                prompt = f"""
                수학교사로서 2022 개정 교육과정 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준에 맞춰 {sel_type}으로 출제해.
                수식은 LaTeX($)를 사용해.
                반드시 아래의 JSON 형식으로만 응답해. 다른 설명은 하지마.
                {{
                    "problem": "문제 내용",
                    "options": ["객관식일 때만 5개 항목, 아니면 빈 리스트"],
                    "hint1": "힌트1", "hint2": "힌트2", "hint3": "힌트3",
                    "concepts": "핵심 개념",
                    "solution": "풀이", "answer": "정답"
                }}
                """
                response = model.generate_content(prompt)
                
                # [강화된 JSON 추출 로직] AI가 앞뒤에 헛소리를 붙여도 JSON만 뽑아냅니다.
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    st.session_state.problem_data = json.loads(json_match.group())
                    st.session_state.user_answer = ""
                    st.session_state.grade_status = None
                    st.session_state.ai_feedback = ""
                else:
                    st.error("AI가 형식을 지키지 않았습니다. 다시 시도해주세요.")
                    st.write("AI 답변 내용:", response.text) # 디버깅용
            except Exception as e:
                st.error(f"❌ 오류 발생 원인: {e}") # 정확한 에러 메시지 표시

# --- [이후 메인 화면 코드는 이전과 동일하게 유지] ---
# (지면 관계상 생략하지만, 실제 app.py에는 이전 코드를 그대로 붙여넣으시면 됩니다)
