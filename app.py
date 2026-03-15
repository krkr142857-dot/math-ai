import streamlit as st
import random

# 페이지 기본 설정
st.set_page_config(page_title="고등학교 수학 문제 생성기", layout="wide")

# 캡스톤디자인 수학교육과 문제 은행 데이터 (예시 데이터 일부 포함, 필요시 확장)
BANK = {
    "고1": {
        "다항식": {
            2: [
                {
                    "type": ["객관식", "단답형", "서술형"],
                    "q": "$(x+3)(x-5)$를 전개하면?",
                    "choices": ["$x^2-2x-15$", "$x^2+2x-15$", "$x^2-2x+15$", "$x^2-8x-15$", "$x^2+8x+15$"],
                    "ans": "$x^2-2x-15$",
                    "sol": "$(x+a)(x+b)=x^2+(a+b)x+ab$에 $a=3,b=-5$ 대입\\n$\\Rightarrow x^2-2x-15$",
                    "hints": ["$(x+a)(x+b)$ 공식 이용", "$a+b=-2$, $ab=-15$"]
                },
                {
                    "type": ["객관식", "단답형", "서술형"],
                    "q": "$(2x+1)(3x-2)$를 전개하면?",
                    "choices": ["$6x^2-x-2$", "$6x^2+x-2$", "$6x^2-x+2$", "$5x^2-x-2$", "$6x^2+x+2$"],
                    "ans": "$6x^2-x-2$",
                    "sol": "분배법칙 전개: $6x^2-4x+3x-2=6x^2-x-2$",
                    "hints": ["분배법칙으로 각 항을 전개", "$-4x+3x=-x$", "상수항은 $-2$"]
                }
            ],
            3: [
                {
                    "type": ["객관식", "단답형", "서술형"],
                    "q": "$(x+y)^3$을 전개하면?",
                    "choices": ["$x^3+3x^2y+3xy^2+y^3$", "$x^3+y^3$", "$x^3-3x^2y+3xy^2-y^3$", "$x^3+2x^2y+2xy^2+y^3$", "$x^3+3xy+y^3$"],
                    "ans": "$x^3+3x^2y+3xy^2+y^3$",
                    "sol": "$(a+b)^3=a^3+3a^2b+3ab^2+b^3$에 대입",
                    "hints": ["세제곱 전개 공식 이용", "계수는 1, 3, 3, 1"]
                }
            ]
        }
    },
    "고2": {
        "지수와 로그": {
            1: [
                {
                    "type": ["객관식", "단답형", "서술형"],
                    "q": "$2^3 \\times 2^4$의 값은?",
                    "choices": ["$128$", "$2^{12}$", "$64$", "$2^{-1}$", "$12$"],
                    "ans": "$128$",
                    "sol": "$2^3 \\times 2^4 = 2^{3+4} = 2^7 = 128$",
                    "hints": ["지수법칙: $a^m \\times a^n = a^{m+n}$", "$3+4=7$"]
                }
            ]
        }
    }
}

# 학년별 단원 매핑
GRADE_UNITS = {
    "고1": ["다항식", "방정식과 부등식", "인수분해", "나머지 정리"],
    "고2": ["지수와 로그", "삼각함수", "수열", "함수의 극한과 미분", "적분"],
    "고3": ["수열의 극한", "미분법", "확률과 통계"]
}

# 세션 상태 초기화 (문제 생성 후 화면 유지를 위함)
if "generated_problems" not in st.session_state:
    st.session_state.generated_problems = []

def generate_problems(grade, sub, lv, q_type, count):
    pool = []
    if grade in BANK and sub in BANK[grade] and lv in BANK[grade][sub]:
        pool = [p for p in BANK[grade][sub][lv] if q_type in p["type"]]
    
    if not pool:
        return []
    
    # 요청한 수만큼 랜덤 추출 (중복 허용)
    selected = random.choices(pool, k=count)
    
    formatted_problems = []
    for p in selected:
        prob_data = p.copy()
        if q_type == "객관식" and "choices" in p:
            choices = p["choices"].copy()
            random.shuffle(choices)
            prob_data["shuffled_choices"] = choices
        formatted_problems.append(prob_data)
        
    return formatted_problems

# 헤더 영역
st.title("고등학교 수학 문제 생성기")
st.caption("2022 개정 교육과정 · 수학교육과 캡스톤디자인")
st.divider()

# 사이드바 영역 (문제 설정)
with st.sidebar:
    st.subheader("⚙ 문제 설정")
    
    selected_grade = st.radio("학년", ["고1", "고2", "고3"], horizontal=True)
    selected_sub = st.selectbox("단원", GRADE_UNITS[selected_grade])
    selected_lv = st.slider("난이도", min_value=1, max_value=5, value=2)
    selected_type = st.radio("문제 유형", ["객관식", "단답형", "서술형"], horizontal=True)
    selected_count = st.number_input("문항 수", min_value=1, max_value=5, value=3)
    
    if st.button("✦ 문제 생성하기", type="primary", use_container_width=True):
        st.session_state.generated_problems = generate_problems(
            selected_grade, selected_sub, selected_lv, selected_type, selected_count
        )

# 메인 패널 영역 (문제 출력)
if not st.session_state.generated_problems:
    st.info("왼쪽 사이드바에서 설정을 선택하고 '문제 생성하기' 버튼을 누르십시오.")
else:
    st.success(f"{selected_grade} · {selected_sub} · Lv.{selected_lv} · {len(st.session_state.generated_problems)}문제 생성 완료")
    
    for i, prob in enumerate(st.session_state.generated_problems):
        with st.container(border=True):
            st.markdown(f"**문제 {i+1}**")
            st.markdown(prob["q"])
            
            # 객관식 선지 렌더링
            if selected_type == "객관식" and "shuffled_choices" in prob:
                options = prob["shuffled_choices"]
                user_ans = st.radio(f"문제 {i+1} 답안 선택", options, key=f"radio_{i}", index=None, label_visibility="collapsed")
            
            # 단답형/서술형 입력 창 렌더링
            elif selected_type == "단답형":
                user_ans = st.text_input(f"문제 {i+1} 정답 입력", key=f"text_{i}", placeholder="정답을 입력하십시오")
            else:
                user_ans = st.text_area(f"문제 {i+1} 풀이 입력", key=f"area_{i}", placeholder="풀이 과정을 서술하십시오")
            
            # 힌트 및 정답 확인 패널
            with st.expander("💡 힌트 및 정답 보기"):
                st.markdown("**힌트**")
                for hint in prob.get("hints", []):
                    st.markdown(f"- {hint}")
                st.divider()
                st.markdown(f"**정답:** {prob['ans']}")
                st.markdown(f"**풀이:**\\n{prob.get('sol', '')}")
