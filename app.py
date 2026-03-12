import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="AI 수학 인터랙티브 플랫폼", layout="wide")

st.markdown("""
    <style>
    .correct-circle { color: #2ecc71; font-size: 100px; position: absolute; top: 0px; left: 50%; transform: translateX(-50%); opacity: 0.7; font-weight: bold; z-index: 10; }
    .wrong-slash { color: #e74c3c; font-size: 120px; position: absolute; top: -10px; left: 50%; transform: translateX(-50%); opacity: 0.7; font-weight: bold; z-index: 10; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .math-keypad button { background-color: #f1f3f5 !important; }
    .concept-area { background-color: #fff9db; padding: 15px; border-radius: 10px; border-left: 5px solid #fab005; }
    </style>
    """, unsafe_allow_html=True)

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

# 데이터 설정
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년": ["다항식", "방정식과 부등식", "경우의 수", "행렬"],
    "고등학교 2/3학년": ["대수", "미적분I", "확률과 통계", "기하"]
}

# --- [1분할: 사이드바] ---
with st.sidebar:
    st.title("🎓 스마트 출제 설정")
    sel_grade = st.selectbox("학년", list(curriculum.keys()))
    sel_unit = st.selectbox("단원", curriculum[sel_grade])
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(심화)", "1등급(고난도)"]
    sel_diff = st.select_slider("목표 등급", options=diff_labels)
    sel_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    
    if st.button("✨ 새 문제 생성", type="primary"):
        with st.spinner('AI가 단원 성취기준을 분석하여 출제 중...'):
            try:
                # [수정] 사용 가능한 모델 중 'gemini'가 포함된 모델을 자동으로 찾습니다.
                model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                # flash 1.5 -> flash -> pro 순서로 찾기
                target_model = next((m for m in model_list if "gemini-1.5-flash" in m), 
                               next((m for m in model_list if "flash" in m), 
                               model_list[0] if model_list else ""))
                
                if not target_model: raise Exception("사용 가능한 Gemini 모델이 없습니다.")
                
                model = genai.GenerativeModel(target_model)
                prompt = f"""
                수학교사로서 2022 개정 교육과정 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준에 맞춰 {sel_type}으로 출제해.
                수식은 LaTeX($)를 사용해. 반드시 아래 JSON 형식으로만 답변해.
                {{
                    "problem": "문제 내용",
                    "options": ["객관식일 때만 5개 항목, 아니면 빈 리스트"],
                    "hint1": "1단계 힌트", "hint2": "2단계 힌트", "hint3": "3단계 힌트",
                    "concepts": "핵심 공식/개념", "solution": "상세 풀이", "answer": "최종 정답"
                }}
                """
                response = model.generate_content(prompt)
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    st.session_state.problem_data = json.loads(json_match.group())
                    st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""
                else: st.error("AI 응답 형식 오류. 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"❌ 출제 오류: {e}")

# --- 메인 화면 레이아웃 (2분할/3분할) ---
if st.session_state.problem_data:
    p = st.session_state.problem_data
    col2, col3 = st.columns([1.6, 1])

    with col2: # [2분할: 문제 및 입력]
        st.subheader("📝 문제")
        # 채점 이펙트
        if st.session_state.grade_status == "correct": st.markdown('<div class="correct-circle">○</div>', unsafe_allow_html=True)
        elif st.session_status == "wrong": st.markdown('<div class="wrong-slash">／</div>', unsafe_allow_html=True)
        
        st.write(p['problem'])
        st.write("---")

        if sel_type == "객관식":
            st.session_state.user_answer = st.radio("정답 선택", p['options'], index=None if st.session_state.user_answer == "" else p['options'].index(st.session_state.user_answer))
        else:
            st.write("🎹 수학 기호 도우미")
            m_cols = st.columns(6)
            symbols = {"√": "\\sqrt{ }", "x²": "^2", "÷": "/", "π": "\\pi", "sin": "\\sin", "cos": "\\cos"}
            for i, (lab, sym) in enumerate(symbols.items()):
                if m_cols[i].button(lab): st.session_state.user_answer += sym
            st.session_state.user_answer = st.text_area("답변 입력", value=st.session_state.user_answer)

        c1, c2 = st.columns(2)
        if c1.button("✅ 제출 및 채점"):
            if sel_type == "객관식":
                st.session_state.grade_status = "correct" if st.session_state.user_answer == p['answer'] else "wrong"
            else:
                with st.spinner('AI 채점 중...'):
                    judge_model = genai.GenerativeModel(target_model)
                    res = judge_model.generate_content(f"문제: {p['problem']}\n정답: {p['answer']}\n학생답: {st.session_state.user_answer}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                    st.session_state.grade_status = "correct" if "정답" in res[:10] else "wrong"
                    st.session_state.ai_feedback = res

        if c2.button("🔄 다시 풀기"):
            st.session_state.user_answer = ""; st.session_state.grade_status = None; st.session_state.ai_feedback = ""; st.rerun()
        
        if st.session_state.ai_feedback: st.info(f"💡 채점 피드백: {st.session_state.ai_feedback}")

    with col3: # [3분할: 가이드]
        st.subheader("💡 학습 가이드")
        with st.expander("1단계 힌트"): st.write(p['hint1'])
        with st.expander("2단계 힌트"): st.write(p['hint2'])
        with st.expander("3단계 힌트"): st.write(p['hint3'])
        
        st.write("---")
        st.markdown("### 📚 핵심 개념")
        st.markdown(f'<div class="concept-area">{p["concepts"]}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🔓 정답/풀이 공개"):
            st.write(f"**정답:** {p['answer']}"); st.write(f"**풀이:** {p['solution']}")
else:
    st.info("👈 왼쪽에서 설정을 완료하고 [새 문제 생성]을 눌러주세요.")
