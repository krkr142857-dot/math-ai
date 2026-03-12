import streamlit as st
import google.generativeai as genai
import time
import json
import re

# 1. 페이지 설정 및 사용자 제공 CSS 테마 완벽 이식
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# CSS: 제공하신 HTML의 스타일(폰트, 색상, 레이아웃)을 1:1로 매칭
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&family=Noto+Serif+KR:wght@400;600&family=Caveat:wght@700&display=swap');
    
    :root {
      --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb;
      --text: #111827; --accent: #4f46e5; --red: #dc2626; --green: #16a34a;
      --shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .stApp { background: var(--bg); font-family: 'Noto Sans KR', sans-serif; }
    
    /* 헤더 스타일 */
    .header { background: #fff; border-bottom: 1px solid var(--border); padding: 10px 24px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }

    /* 빨간펜 O/X 스탬프 (Caveat 폰트) */
    .ox-stamp {
        position: absolute; top: 10px; left: 15px;
        font-family: 'Caveat', cursive; font-size: 80px; font-weight: 700;
        line-height: 1; pointer-events: none; z-index: 99; color: #e11d48; opacity: 0.7;
    }

    /* 문제 카드 (Center Panel) */
    .prob-card {
        background: var(--card-bg); border: 1.5px solid var(--border);
        border-radius: 14px; padding: 25px; position: relative;
        box-shadow: var(--shadow); margin-bottom: 20px;
        font-family: 'Noto Serif KR', serif; line-height: 2.1; color: var(--text);
    }
    
    /* 우측 패널 하단 고정 키패드 느낌 */
    .fixed-keypad {
        background: #ffffff; border-top: 2px solid var(--accent);
        padding: 15px; border-radius: 12px 12px 0 0;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
    }

    /* 사이드바 글자 지워짐 방지 */
    .stSelectbox, .stSlider { margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. AI 모델 연결 및 보안
def get_ai_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = next((m for m in model_list if "gemini-1.5-flash" in m), model_list[0])
        return genai.GenerativeModel(target)
    except: return None

# 3. 데이터 및 세션 상태
if 'problems' not in st.session_state: st.session_state.problems = []
if 'user_ans' not in st.session_state: st.session_state.user_ans = {}
if 'results' not in st.session_state: st.session_state.results = {}
if 'cur_idx' not in st.session_state: st.session_state.cur_idx = 0

# 2022 개정 교육과정 데이터베이스
curriculum = {
    "중학교 1학년": ["소수와 합성수", "정수와 유리수", "문자와 식", "좌표평면과 그래프"],
    "중학교 2학년": ["유리수와 순환소수", "식의 계산", "부등식", "연립방정식", "함수"],
    "중학교 3학년": ["제곱근과 실수", "다항식의 곱셈과 인수분해", "이차방정식", "이차함수"],
    "고등학교 1학년(공통수학)": ["다항식", "방정식과 부등식", "경우의 수", "행렬", "집합과 명제"],
    "고등학교 2/3학년(선택)": ["대수", "미적분I", "확률과 통계", "기하", "미적분II"]
}

# 4. 상단 헤더
st.markdown("""
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; background:#4f46e5; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">∑</div>
            <div>
                <div style="font-weight:800; font-size:15px; color:#111827;">수학 문제 생성기</div>
                <div style="font-size:10.5px; color:#9ca3af;">2022 개정 교육과정 · 수학교육과 캡스톤디자인</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. [1분할: 왼쪽 사이드바]
with st.sidebar:
    st.markdown("### ⚙ 문제 설정")
    sel_grade = st.selectbox("학년", list(curriculum.keys()))
    sel_unit = st.selectbox("단원", curriculum[sel_grade])
    
    diff_labels = ["7~9등급(기초)", "4~6등급(기본)", "2~3등급(표준)", "1등급(고난도)"]
    sel_diff = st.select_slider("목표 등급", options=diff_labels)
    
    sel_type = st.radio("유형", ["객관식", "단답형", "서술형"])
    sel_count = st.number_input("문항 수", 1, 5, 3)

    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        model = get_ai_model()
        if model:
            with st.spinner('문제를 설계 중입니다...'):
                prompt = f"""
                수학교사로서 {sel_grade} {sel_unit} 단원의 문제를 {sel_diff} 수준으로 {sel_type} {sel_count}개를 출제해.
                수식은 LaTeX($)를 사용하고, 역슬래시는 반드시 두 번(\\\\) 써서 JSON 파싱 오류를 막아. 
                결과는 반드시 아래 JSON 형식으로만 답변해:
                {{
                    "probs": [
                        {{
                            "q": "문제 내용 (수식은 $기호 사용)",
                            "choices": ["객관식일 때만 5개, 아니면 빈 리스트"],
                            "hints": ["1단계", "2단계", "3단계"],
                            "concepts": "핵심 공식 및 개념",
                            "solution": "상세 풀이",
                            "answer": "정답"
                        }}
                    ]
                }}
                """
                try:
                    res = model.generate_content(prompt).text
                    data = json.loads(re.search(r'\{.*\}', res, re.DOTALL).group())
                    st.session_state.problems = data['probs']
                    st.session_state.user_ans = {}
                    st.session_state.results = {}
                    st.session_state.cur_idx = 0
                except: st.error("출제 중 오류가 발생했습니다. 다시 시도해주세요.")

# 6. 메인 콘텐츠 (2분할: 센터, 3분할: 우측)
if st.session_state.problems:
    col_center, col_right = st.columns([1.5, 1])

    # --- [2분할: 센터 패널] ---
    with col_center:
        for i, prob in enumerate(st.session_state.problems):
            # 문제 카드 시작
            st.markdown(f'<div class="prob-card">', unsafe_allow_html=True)
            
            # O/X 스탬프 (제시하신 X자 포함)
            res = st.session_state.results.get(i)
            if res == "correct": st.markdown('<div class="ox-stamp">○</div>', unsafe_allow_html=True)
            elif res == "wrong": st.markdown('<div class="ox-stamp">✕</div>', unsafe_allow_html=True)
            
            st.markdown(f"<small style='color:#4f46e5; font-weight:700;'>문제 {i+1}</small>", unsafe_allow_html=True)
            st.write(prob['q'])
            
            # 입력 영역
            if sel_type == "객관식":
                st.session_state.user_ans[i] = st.radio(f"보기 ({i+1})", prob['choices'], key=f"radio_{i}", index=None)
            elif sel_type == "단답형":
                st.session_state.user_ans[i] = st.text_input(f"답안 입력 ({i+1})", key=f"input_{i}")
            else:
                st.session_state.user_ans[i] = st.text_area(f"풀이과정 및 정답 입력 ({i+1})", key=f"input_{i}", height=150)
            
            # 버튼 영역
            b1, b2 = st.columns(2)
            if b1.button(f"✅ 채점하기", key=f"btn_{i}"):
                if sel_type == "서술형":
                    model = get_ai_model()
                    feedback = model.generate_content(f"문제: {prob['q']}\n정답: {prob['answer']}\n학생답: {st.session_state.user_ans[i]}\n채점해줘. '정답' 혹은 '오답'으로 시작.").text
                    st.session_state.results[i] = "correct" if "정답" in feedback[:10] else "wrong"
                else:
                    st.session_state.results[i] = "correct" if str(st.session_state.user_ans[i]) == str(prob['answer']) else "wrong"
                st.session_state.cur_idx = i # 현재 보고 있는 문제 업데이트
                st.rerun()

            if b2.button(f"↺ 다시 풀기", key=f"retry_{i}"):
                st.session_state.user_ans[i] = ""
                st.session_state.results[i] = None
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- [3분할: 우측 패널] ---
    with col_right:
        # 상단: 힌트, 개념, 풀이 (스크롤 가능)
        p = st.session_state.problems[st.session_state.cur_idx]
        st.markdown(f"### 💡 문제 {st.session_state.cur_idx+1} 학습 가이드")
        
        with st.container():
            st.markdown("##### 힌트 (단계별)")
            for j, hint in enumerate(p['hints']):
                with st.expander(f"힌트 {j+1}"):
                    st.write(hint)
            
            st.markdown("---")
            st.markdown("##### 📚 핵심 개념 및 공식")
            st.success(p['concepts'])
            
            st.markdown("---")
            if st.button("🔓 정답 및 상세 풀이 공개"):
                st.markdown(f"**정답:** {p['answer']}")
                st.markdown(f"**상세 풀이:**\n{p['solution']}")
        
        st.write("") # 간격
        
        # 하단: 공학용 수식 입력기 (고정 배치 느낌)
        st.markdown('<div class="fixed-keypad">', unsafe_allow_html=True)
        st.markdown("<small style='color:#4f46e5; font-weight:700;'>🎹 수식 입력기</small>", unsafe_allow_html=True)
        
        k_cols = st.columns(4)
        syms = {
            "√": "\\sqrt{ }", "frac": "\\frac{ }{ }", "xⁿ": "^n", "π": "\\pi",
            "sin": "\\sin", "cos": "\\cos", "tan": "\\tan", "θ": "\\theta",
            "lim": "\\lim", "∑": "\\sum", "∫": "\\int", "°": "^{\\circ}"
        }
        
        for idx, (lab, val) in enumerate(syms.items()):
            if k_cols[idx % 4].button(lab, key=f"key_{lab}"):
                st.info(f"복사해서 사용: `{val}`")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 빈 화면 (제공하신 HTML의 Empty State)
    st.markdown("""
        <div style="text-align:center; padding-top:100px; color:#9ca3af;">
            <div style="font-size:40px;">📝</div>
            <div style="font-size:13.5px;">왼쪽에서 설정을 선택하고<br>문제 생성하기를 누르세요</div>
        </div>
        """, unsafe_allow_html=True)
