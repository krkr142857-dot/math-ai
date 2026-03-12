import streamlit as st
import google.generativeai as genai
import json
import re

# 1. 페이지 설정 (화면 전체 사용)
st.set_page_config(page_title="수학 문제 생성기", layout="wide")

# 2. AI 모델 연결 함수
def get_gemini_response(grade, unit, diff, q_type, count):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"].strip().replace('"', '').replace("'", "")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        수학교사로서 {grade} {unit} 단원의 문제를 {diff} 수준으로 {q_type} {count}개를 출제해.
        수식은 반드시 LaTeX($)로 감싸고 역슬래시는 반드시 두 번(\\\\) 써서 JSON 오류를 방지해. 
        반드시 아래의 구조를 가진 JSON 데이터만 응답해. 다른 설명은 절대 하지마.
        {{
            "problems": [
                {{
                    "q": "문제 내용 (라텍스 포함)",
                    "choices": ["객관식일 때만 5개, 아니면 빈 리스트"],
                    "correct_idx": 0,
                    "answer": "정답 표시용 라텍스",
                    "short_answer": "채점용 정답 텍스트",
                    "solution": "상세 풀이",
                    "hints": ["힌트1", "힌트2", "힌트3"],
                    "terms": "핵심 용어",
                    "standard": "교육과정 성취기준"
                }}
            ]
        }}
        """
        response = model.generate_content(prompt)
        # JSON 부분만 추출
        json_data = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        return json.loads(json_data)
    except:
        return None

# 3. 사이드바 설정 (디자인과 기능 일치)
with st.sidebar:
    st.markdown("### ⚙️ 문제 설정")
    grade = st.selectbox("학년", ["중학교 1학년", "중학교 2학년", "중학교 3학년", "고등학교 1학년", "고등학교 2/3학년"])
    unit = st.text_input("단원명", "다항식의 연산")
    diff = st.select_slider("난이도", options=["7~9등급", "4~6등급", "2~3등급", "1등급"])
    q_type = st.radio("유형", ["객관식", "단답형", "서술형"])
    count = st.number_input("문항 수", 1, 5, 3)
    
    generate_clicked = st.button("✦ 문제 생성하기", type="primary", use_container_width=True)

# 4. 문제 생성 로직
if generate_clicked:
    with st.spinner('AI가 문제를 설계 중입니다...'):
        result = get_gemini_response(grade, unit, diff, q_type, count)
        if result:
            st.session_state.bank_data = result['problems']
            st.session_state.current_info = f"{grade} · {unit} · {diff}"
        else:
            st.error("출제 오류가 발생했습니다. 다시 시도해주세요.")

# 5. HTML/CSS/JS 템플릿 (제공해주신 코드 100% 반영)
if 'bank_data' in st.session_state:
    # 파이썬 데이터를 자바스크립트 변수로 변환
    json_bank = json.dumps(st.session_state.bank_data, ensure_ascii=False)
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&family=Noto+Serif+KR&family=Caveat:wght@700&display=swap" rel="stylesheet"/>
    <style>
    /* 제공하신 CSS 스타일 그대로 복사 */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ --bg: #f5f6fa; --sidebar-bg: #ffffff; --card-bg: #ffffff; --border: #e5e7eb; --text: #111827; --accent: #4f46e5; --red: #dc2626; --green: #16a34a; }}
    body {{ background: var(--bg); font-family: 'Noto Sans KR', sans-serif; color: var(--text); height: 100vh; overflow: hidden; display: flex; flex-direction: column; }}
    .workspace {{ flex: 1; display: flex; overflow: hidden; }}
    .center-panel {{ flex: 1; overflow-y: auto; padding: 20px 16px; display: flex; flex-direction: column; gap: 14px; }}
    .right-panel {{ width: 370px; background: var(--sidebar-bg); border-left: 1px solid var(--border); overflow-y: auto; padding: 20px 18px; display: flex; flex-direction: column; gap: 14px; }}
    .prob-card {{ background: var(--card-bg); border: 1.5px solid var(--border); border-radius: 14px; padding: 22px; cursor: pointer; position: relative; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .prob-card.selected {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(79,70,229,0.08); }}
    .ox-stamp {{ position: absolute; top: 12px; left: 14px; font-family: 'Caveat', cursive; font-size: 48px; font-weight: 700; opacity: 0; transition: opacity .25s; pointer-events: none; }}
    .ox-stamp.show-o {{ color: #e11d48; opacity: 1; }}
    .ox-stamp.show-x {{ color: #e11d48; opacity: 1; }}
    .card-q {{ font-family: 'Noto Serif KR', serif; font-size: 16px; line-height: 2.1; }}
    .choice-opt {{ padding: 10px 14px; border-radius: 9px; cursor: pointer; border: 1.5px solid #f0f1f5; background: var(--bg); margin-top: 7px; }}
    .choice-opt.picked {{ border-color: var(--accent); background: #ede9fe; }}
    .choice-opt.revealed-correct {{ border-color: var(--green) !important; background: #f0fdf4 !important; }}
    .choice-opt.revealed-wrong {{ border-color: var(--red) !important; background: #fef2f2 !important; }}
    .hint-body, .ans-box, .sol-box {{ display: none; padding: 10px; border-radius: 7px; margin-top: 5px; font-size: 13px; }}
    .hint-body.open, .ans-box.open, .sol-box.open {{ display: block; }}
    .ans-box {{ background: #f0fdf4; color: var(--green); }}
    .sol-box {{ background: #fffbeb; color: #78350f; white-space: pre-wrap; }}
    
    /* 하단 고정 키패드 스타일 */
    .math-keypad {{ position: sticky; bottom: 0; background: white; border-top: 2px solid var(--accent); padding: 10px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; z-index: 100; }}
    .key-btn {{ padding: 8px; font-size: 12px; border: 1px solid var(--border); border-radius: 5px; cursor: pointer; background: #f8fafc; }}
    </style>
    </head>
    <body>
    <div class="workspace">
        <div class="center-panel" id="centerPanel"></div>
        <div class="right-panel">
            <div id="rightPanelContents">
                <div style="text-align:center; color:#9ca3af; padding-top:50px;">문제를 클릭하면<br>해설이 나옵니다</div>
            </div>
            <div class="math-keypad">
                <button class="key-btn" onclick="copyToClipboard('\\\\sqrt{{}}')">√</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\frac{{}}{{}}')">분수</button>
                <button class="key-btn" onclick="copyToClipboard('^n')">제곱</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\sin')">sin</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\lim_{{x \\\\to \\\\infty}}')">lim</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\sum')">∑</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\int')">∫</button>
                <button class="key-btn" onclick="copyToClipboard('\\\\theta')">θ</button>
            </div>
        </div>
    </div>

    <script>
    const BANK = {json_bank};
    let selectedIdx = -1;
    const states = BANK.map(() => ({{ picked: -1, submitted: false }}));

    function renderProblems() {{
        const container = document.getElementById('centerPanel');
        container.innerHTML = BANK.map((p, i) => `
            <div class="prob-card" id="card-${{i}}" onclick="selectCard(${{i}})">
                <div class="ox-stamp" id="stamp-${{i}}"></div>
                <div style="font-size:11px; color:var(--accent); font-weight:700; margin-bottom:8px;">문제 ${{i+1}}</div>
                <div class="card-q">${{p.q}}</div>
                ${{ p.choices.length > 0 ? 
                    `<div class="choices-list">${{p.choices.map((c, ci) => `
                        <div class="choice-opt" id="opt-${{i}}-${{ci}}" onclick="pick(${{i}}, ${{ci}})">
                            <span style="font-weight:700; margin-right:10px;">${{ci+1}}</span>${{c}}
                        </div>`).join('')}}</div>` : 
                    `<input type="text" id="input-${{i}}" style="width:100%; padding:10px; margin-top:10px; border:1px solid #ddd; border-radius:8px;">`
                }}
                <button onclick="submit(${{i}})" style="margin-top:15px; width:100%; padding:10px; background:var(--accent); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:700;">채점하기</button>
            </div>
        `).join('');
        renderMathInElement(container, {{ delimiters: [{{left: "$", right: "$", display: false}}] }});
    }}

    window.selectCard = function(idx) {{
        selectedIdx = idx;
        document.querySelectorAll('.prob-card').forEach((c, i) => c.classList.toggle('selected', i === idx));
        const p = BANK[idx];
        document.getElementById('rightPanelContents').innerHTML = `
            <div style="font-size:10px; color:var(--accent); font-weight:700; letter-spacing:1px;">💡 해설 가이드</div>
            <div style="margin-top:15px;">
                <div style="font-size:12px; color:var(--text-sub); margin-bottom:5px;">힌트</div>
                <div class="hint-body open">${{p.hints[0]}}</div>
            </div>
            <div style="margin-top:15px;">
                <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:8px; background:#f0fdf4; border:1px solid #86efac; color:#16a34a; border-radius:8px; cursor:pointer;">정답 확인</button>
                <div class="ans-box">정답: ${{p.answer}}</div>
            </div>
            <div style="margin-top:10px;">
                <button onclick="this.nextElementSibling.classList.toggle('open')" style="width:100%; padding:8px; background:#fffbeb; border:1px solid #fcd34d; color:#d97706; border-radius:8px; cursor:pointer;">풀이 보기</button>
                <div class="sol-box">${{p.solution}}</div>
            </div>
        `;
        renderMathInElement(document.getElementById('rightPanelContents'), {{ delimiters: [{{left: "$", right: "$", display: false}}] }});
    }}

    window.pick = function(pi, ci) {{
        if (states[pi].submitted) return;
        states[pi].picked = ci;
        document.querySelectorAll(`#card-${{pi}} .choice-opt`).forEach((o, i) => o.classList.toggle('picked', i === ci));
    }}

    window.submit = function(idx) {{
        const p = BANK[idx];
        const stamp = document.getElementById(`stamp-${{idx}}`);
        let correct = false;
        if (p.choices.length > 0) {{
            correct = (states[idx].picked === p.correct_idx);
            document.querySelectorAll(`#card-${{idx}} .choice-opt`).forEach((o, i) => {{
                if (i === p.correct_idx) o.classList.add('revealed-correct');
                else if (i === states[idx].picked) o.classList.add('revealed-wrong');
            }});
        } else {{
            const val = document.getElementById(`input-${{idx}}`).value.replace(/\s/g,'');
            correct = (val === p.short_answer.replace(/\s/g,''));
        }}
        stamp.textContent = correct ? '○' : '✕';
        stamp.className = correct ? 'ox-stamp show-o' : 'ox-stamp show-x';
        states[idx].submitted = true;
    }}

    window.copyToClipboard = function(text) {{
        alert('복사되었습니다: ' + text + '\\n답안 입력창에 붙여넣으세요.');
    }}

    renderProblems();
    </script>
    </body>
    </html>
    """
    st.components.v1.html(html_code, height=800, scrolling=True)
else:
    st.markdown(f"""
        <div style="text-align:center; padding-top:150px; color:#9ca3af; font-family:'Noto Sans KR';">
            <h1 style="font-size:50px;">∑</h1>
            <p>왼쪽 사이드바에서 조건을 설정하고<br><b>[문제 생성하기]</b>를 누르면 AI가 문제를 출제합니다.</p>
        </div>
    """, unsafe_allow_html=True)
