import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정 및 사용자 제공 CSS 테마 적용
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# CSS: 보내주신 HTML의 모든 스타일(색상, 폰트, 그림자) 반영
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&family=Noto+Serif+KR:wght@400;600&family=Caveat:wght@700&display=swap');
    
    :root {
      --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb;
      --text: #111827; --accent: #4f46e5; --red: #e11d48; --green: #16a34a;
    }
    
    .stApp { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; }

    /* 헤더 스타일 */
    .custom-header {
        background: #fff; border-bottom: 1px solid var(--border);
        padding: 10px 24px; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 20px;
    }

    /* 빨간펜 O/X 스탬프 (Caveat 폰트 적용) */
    .ox-stamp {
        position: absolute; top: 12px; left: 14px;
        font-family: 'Caveat', cursive; font-size: 60px; font-weight: 700;
        line-height: 1; pointer-events: none; z-index: 100;
    }
    .stamp-o { color: #e11d48; opacity: 0.7; }
    .stamp-x { color: #e11d48; opacity: 0.7; }

    /* 문제 카드 스타일 (센터 패널) */
    .prob-card {
        background: var(--card-bg); border: 1.5px solid var(--border);
        border-radius: 14px; padding: 22px; position: relative;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 15px;
        font-family: 'Noto Serif KR', serif; line-height: 2.1;
    }
    
    /* 우측 패널 힌트/해설 박스 */
    .info-box {
        background: #f8fafc; border: 1px solid var(--border);
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }

    /* 수식 키패드 (고정형 스타일) */
    .keypad-container {
        background: #ffffff; border: 2px solid var(--accent);
        border-radius: 12px; padding: 12px; margin-top: 20px;
        box-shadow: 0 -4px 10px rgba(79,70,229,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 모델 설정
def load_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(target)
    except: return None

# 3. 데이터 및 세션 상태 관리
if 'problems' not in st.session_state: st.session_state.problems = []
if 'selected_idx' not in st.session_state: st.session_state.selected_idx = 0
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'grade_results' not in st.session_state: st.session_state.grade_results = {}

curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# 4. 상단 헤더 (HTML 구조 유지)
st.markdown("""
    <div class="custom-header">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; background:#4f46e5; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">∑</div>
            <div>
                <div style="font-weight:800; font-size:15px; color:#111827;">수학 문제 생성기</div>
                <div style="font-size:10.5px; color:#9ca3af;">2022 개정 교육과정 · 수학교육과 캡스톤디자인</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. [1분할: 사이드바 설정]
with st.sidebar:
    st.markdown("### ⚙ 문제 설정")
    sel_grade = st.selectbox("학년 선택", list(curriculum.keys()))
    sel_unit = st.selectbox("단원 선택", curriculum[sel_grade])
    
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(표준)", "1등급(심화)"]
    sel_diff = st.select_slider("난이도", options=diff_labels)
    
    sel_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"])
    sel_count = st.number_input("문항 수", 1, 5, 1)

    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        model = load_model()
        if model:
            with st.spinner('문제를 생성 중입니다...'):
                prompt = f"""
                수학교사로서 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준으로 {sel_type} {sel_count}개를 출제해.
                모든 수식은 반드시 LaTeX($)로 감싸고 역슬래시는 두 번(\\\\) 써서 JSON 오류를 방지해. 
                $ 기호와 내용 사이에 공백을 두지 마. (예: $x^2$)
                형식:
                {{
                    "problems": [
                        {{
                            "q": "문제 내용",
                            "choices": ["객관식일 때만 5개, 아니면 빈 리스트"],
                            "hints": ["1단계", "2단계", "3단계"],
                            "concepts": "핵심 개념 및 공식",
                            "solution": "상세 풀이",
                            "answer": "정답"
                        }}
                    ]
                }}
                답변은 JSON만 출력해.
                """
                try:
                    res = model.generate_content(prompt).text
                    match = re.search(r'\{.*\}', res, re.DOTALL)
                    data = json.loads(match.group())
                    st.session_state.problems = data['problems']
                    st.session_state.user_answers = {}
                    st.session_state.grade_results = {}
                    st.session_state.selected_idx = 0
                except: st.error("출제 실패. 다시 시도해 주세요.")

# 6. 메인 워크스페이스 (2분할: 센터, 3분할: 우측)
if st.session_state.problems:
    col_center, col_right = st.columns([1.6, 1])

    # --- [2분할: 센터 패널] ---
    with col_center:
        for idx, prob in enumerate(st.session_state.problems):
            # 문제 카드 시작
            st.markdown(f'<div class="prob-card" id="prob-{idx}">', unsafe_allow_html=True)
            
            # 빨간펜 O/X 스탬프
            res = st.session_state.grade_results.get(idx)
            if res == "correct": st.markdown('<div class="ox-stamp stamp-o">○</div>', unsafe_allow_html=True)
            elif res == "wrong": st.markdown('<div class="ox-stamp stamp-x">✕</div>', unsafe_allow_html=True)
            
            st.markdown(f"<small style='color:#4f46e5; font-weight:700;'>문제 {idx+1}</small>", unsafe_allow_html=True)
            st.write(prob['q'])
            
            # 입력 영역
            if sel_type == "객관식":
                ans = st.radio(f"정답 선택 ({idx+1})", prob['choices'], key=f"ans_{idx}", index=None)
                st.session_state.user_answers[idx] = ans
            elif sel_type == "단답형":
                ans = st.text_input(f"답안 입력 ({idx+1})", key=f"ans_{idx}")
                st.session_state.user_answers[idx] = ans
            else:
                ans = st.text_area(f"풀이 및 답안 입력 ({idx+1})", key=f"ans_{idx}", height=150)
                st.session_state.user_answers[idx] = ans
            
            # 채점 및 다시풀기 버튼
            b1, b2 = st.columns(2)
            if b1.button(f"✅ 채점하기 ({idx+1})", key=f"grade_btn_{idx}"):
                if sel_type == "서술형":
                    model = load_model()
                    feedback = model.generate_content(f"문제: {prob['q']}\n정답: {prob['answer']}\n학생답: {ans}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                    st.session_state.grade_results[idx] = "correct" if "정답" in feedback[:10] else "wrong"
                else:
                    st.session_state.grade_results[idx] = "correct" if ans == prob['answer'] else "wrong"
                st.rerun()

            if b2.button(f"↺ 다시 풀기 ({idx+1})", key=f"retry_{idx}"):
                st.session_state.grade_results[idx] = None
                st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)

    # --- [3분할: 우측 패널] ---
    with col_right:
        st.markdown("### 💡 학습 가이드")
        
        # 선택된 문제의 상세 정보 표시 (가장 최근에 건드린 문제 기준)
        cur_idx = st.session_state.selected_idx
        p = st.session_state.problems[cur_idx]
        
        with st.container():
            # 힌트 3단계
            for i, h in enumerate(p['hints']):
                with st.expander(f"힌트 {i+1}"):
                    st.write(h)
            
            st.markdown("---")
            # 핵심 개념
            st.markdown("##### 📚 핵심 개념 및 공식")
            st.success(p['concepts'])
            
            st.markdown("---")
            # 정답 및 풀이 (스크롤 가능)
            if st.button("🔓 정답 및 풀이 확인"):
                st.markdown(f"**정답:** {p['answer']}")
                st.write(p['solution'])
        
        # [고정형 수식 키패드 - 한글 수식 편집기 스타일]
        st.markdown('<div class="keypad-container">', unsafe_allow_html=True)
        st.markdown("<small style='color:#4f46e5; font-weight:700;'>🎹 수식 입력기</small>", unsafe_allow_html=True)
        
        k_col1, k_col2, k_col3, k_col4 = st.columns(4)
        syms = {
            "√": "\\sqrt{ }", "frac": "\\frac{ }{ }", "xⁿ": "^n", "π": "\\pi",
            "sin": "\\sin ", "cos": "\\cos ", "tan": "\\tan ", "θ": "\\theta",
            "lim": "\\lim_{x \\to \\infty}", "∑": "\\sum_{k=1}^{n}", "∫": "\\int ", "°": "^{\\circ}"
        }
        
        # 각 버튼 클릭 시 안내 메시지 (스트림릿은 텍스트 영역에 직접 주입이 어려우므로 문구 제공)
        for i, (lab, val) in enumerate(syms.items()):
            cols = [k_col1, k_col2, k_col3, k_col4]
            if cols[i%4].button(lab, key=f"key_{lab}"):
                st.code(val)
                st.caption("위 코드를 복사해서 입력창에 붙여넣으세요.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 초기 빈 화면 (보내주신 HTML의 Empty State 반영)
    st.markdown("""
        <div style="text-align:center; padding-top:100px; color:#9ca3af;">
            <div style="font-size:40px;">📝</div>
            <div style="font-size:13.5px;">왼쪽에서 설정을 선택하고<br>문제 생성하기를 누르세요</div>
        </div>
        """, unsafe_allow_html=True)
