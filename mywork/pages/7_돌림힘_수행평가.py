import streamlit as st
import streamlit.components.v1 as components
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import random  # 🌟 랜덤 출제를 위해 추가

st.set_page_config(page_title="수행평가: 돌림힘과 평형", page_icon="⚖️", layout="wide")

# =====================================================================
# 🚨 로그인 수문장
# =====================================================================
if not st.session_state.get('logged_in', False):
    st.error("⚠️ 로그인이 필요한 페이지입니다.")
    st.info("👈 왼쪽 사이드바에서 메인 페이지로 이동하여 먼저 로그인해 주세요!")
    st.stop()

# =====================================================================
# 🛠️ 구글 시트 연동 세팅
# =====================================================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if "google_creds" in st.secrets:
    creds_dict = json.loads(st.secrets["google_creds"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    current_folder = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_folder) 
    key_path = os.path.join(parent_folder, "credentials.json")
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)

client = gspread.authorize(creds)
spreadsheet = client.open("2026 물리학")
result_sheet = spreadsheet.worksheet("돌림힘 수행평가") 
user_sheet = spreadsheet.worksheet("회원정보") 

s_id = str(st.session_state.student_id)
s_name = st.session_state.student_name
st.success(f"현재 로그인된 학생: **{s_id} {s_name}**")

# =====================================================================
# 🌟 [신규] 학생마다 다른 A, B, C 질량을 생성하는 로직
# =====================================================================
random.seed(s_id + "_eval") # 학번을 시드로 사용하여 항상 같은 랜덤값 보장
# 10kg 추와 1~5m 갈고리 범위 내에서 정수로 완벽히 측정 가능한 질량만 뽑았습니다!
eval_mass_a = random.choice([2, 4, 6, 8])
eval_mass_b = random.choice([15, 20, 25])
eval_mass_c = random.choice([30, 40, 50])
random.seed() # 다음 작업을 위해 초기화

# =====================================================================
# 🌟 가상 실험실 HTML 코드 (질량을 자유자재로 바꾸는 함수형으로 진화!)
# =====================================================================
def get_sim_html(mass_a, mass_b, mass_c):
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
            .instructions {{ background: #fff3cd; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; max-width: 600px; color: #555; text-align: center; line-height: 1.5; font-size: 14px; }}
            #lab-container {{ width: 100%; max-width: 800px; height: 350px; background: white; border-radius: 12px; position: relative; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            #fulcrum {{ width: 0; height: 0; border-left: 30px solid transparent; border-right: 30px solid transparent; border-bottom: 60px solid #7f8c8d; position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%); z-index: 2; }}
            #beam-wrapper {{ position: absolute; bottom: 110px; left: 50%; width: 90%; height: 20px; transform: translateX(-50%); }}
            #beam {{ width: 100%; height: 100%; background: #e67e22; border-radius: 10px; position: relative; transform-origin: center center; transition: transform 1s ease-in-out; box-shadow: 0 4px 6px rgba(0,0,0,0.2); z-index: 3; }}
            .hook {{ width: 40px; height: 20px; position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; }}
            .hook::after {{ content: ''; width: 4px; height: 25px; background: #333; position: absolute; top: 15px; z-index: -1; }}
            .hook-label {{ position: absolute; top: -25px; font-size: 14px; font-weight: bold; color: #333; }}
            .controls {{ display: flex; gap: 15px; margin-bottom: 20px; }}
            button {{ padding: 12px 25px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; color: white; box-shadow: 0 3px 6px rgba(0,0,0,0.15); transition: background 0.2s; }}
            #btn-test {{ background: #3498db; }} #btn-reset {{ background: #e74c3c; }}
            #inventory {{ display: flex; gap: 15px; padding: 20px; background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 800px; justify-content: center; min-height: 80px; box-sizing: border-box; }}
            .weight {{ width: 50px; height: 50px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; cursor: grab; position: absolute; z-index: 10; touch-action: none; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; font-size: 14px; transition: transform 1s ease-in-out; }}
            .weight:active {{ cursor: grabbing; transform: scale(1.1); transition: none; }}
            #w-std {{ background: #2ecc71; }} #w-a {{ background: #9b59b6; }} #w-b {{ background: #f1c40f; color: #333; }} #w-c {{ background: #34495e; }}
            .inv-slot {{ width: 50px; height: 50px; border: 2px dashed #ccc; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="instructions">
            <strong>[실험 방법]</strong> 하단의 기준 추(10kg)와 미지 시료를 수평대 위 갈고리에 드래그하세요.<br>
            <strong>'시도하기'</strong>를 눌러 수평이 되는지 확인하고, A, B, C의 질량을 구하세요!
        </div>
        <div class="controls"><button id="btn-test">▶ 시도하기</button><button id="btn-reset">↺ 수평 맞추기</button></div>
        <div id="lab-container">
            <div id="beam-wrapper"><div id="beam"></div></div><div id="fulcrum"></div>
        </div>
        <div id="inventory">
            <div class="inv-slot" id="slot-std"></div><div class="inv-slot" id="slot-a"></div><div class="inv-slot" id="slot-b"></div><div class="inv-slot" id="slot-c"></div>
        </div>
        
        <!-- 🌟 파이썬에서 지정한 질량이 HTML로 쏙 들어갑니다! -->
        <div class="weight" id="w-std" data-mass="10">기준<br>10kg</div>
        <div class="weight" id="w-a" data-mass="{mass_a}">시료 A</div>
        <div class="weight" id="w-b" data-mass="{mass_b}">시료 B</div>
        <div class="weight" id="w-c" data-mass="{mass_c}">시료 C</div>

        <script>
            const beam = document.getElementById('beam');
            const hooks = []; const positions = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]; let isTesting = false;
            positions.forEach(pos => {{
                const hook = document.createElement('div'); hook.className = 'hook'; hook.style.left = `calc(50% + ${{pos * 9}}%)`; hook.dataset.pos = pos;
                const label = document.createElement('div'); label.className = 'hook-label'; label.innerText = Math.abs(pos) + 'm';
                hook.appendChild(label); beam.appendChild(hook); hooks.push({{ el: hook, pos: pos, currentWeight: null }});
            }});
            let draggedWeight = null; let startX, startY, initialLeft, initialTop;
            const weights = document.querySelectorAll('.weight');
            const slots = {{ 'w-std': document.getElementById('slot-std'), 'w-a': document.getElementById('slot-a'), 'w-b': document.getElementById('slot-b'), 'w-c': document.getElementById('slot-c') }};
            function resetWeightPosition(w) {{ document.body.appendChild(w); const rect = slots[w.id].getBoundingClientRect(); w.style.left = (rect.left + window.scrollX) + 'px'; w.style.top = (rect.top + window.scrollY) + 'px'; w.style.transform = 'none'; w.dataset.hookPos = ""; }}
            window.addEventListener('load', () => {{ weights.forEach(w => resetWeightPosition(w)); }});
            window.addEventListener('resize', () => {{ weights.forEach(w => {{ if(!w.dataset.hookPos) resetWeightPosition(w); }}); }});
            weights.forEach(w => {{
                w.addEventListener('pointerdown', (e) => {{
                    if (isTesting) {{ beam.style.transform = 'rotate(0deg)'; hooks.forEach(h => {{ if (h.currentWeight) h.currentWeight.style.transform = 'translateX(-50%) rotate(0deg)'; }}); isTesting = false; }}
                    const rect = w.getBoundingClientRect(); document.body.appendChild(w); w.style.left = (rect.left + window.scrollX) + 'px'; w.style.top = (rect.top + window.scrollY) + 'px'; w.style.transform = 'none'; 
                    draggedWeight = w; startX = e.clientX; startY = e.clientY; initialLeft = parseFloat(w.style.left || 0); initialTop = parseFloat(w.style.top || 0); w.style.zIndex = 100;
                    hooks.forEach(h => {{ if(h.currentWeight === w) h.currentWeight = null; }}); w.dataset.hookPos = ""; document.body.style.userSelect = 'none';
                }});
            }});
            document.addEventListener('pointermove', (e) => {{ if (!draggedWeight) return; const dx = e.clientX - startX; const dy = e.clientY - startY; draggedWeight.style.left = initialLeft + dx + 'px'; draggedWeight.style.top = initialTop + dy + 'px'; }});
            document.addEventListener('pointerup', (e) => {{
                if (!draggedWeight) return; document.body.style.userSelect = ''; let snapped = false;
                const weightRect = draggedWeight.getBoundingClientRect(); const wCenter = weightRect.left + weightRect.width / 2; const wTop = weightRect.top; 
                hooks.forEach(h => {{
                    const hookRect = h.el.getBoundingClientRect(); const hCenter = hookRect.left + hookRect.width / 2; const hBottom = hookRect.bottom;
                    if (Math.abs(wCenter - hCenter) < 40 && Math.abs(wTop - hBottom) < 60) {{
                        if (h.currentWeight == null) {{ h.el.appendChild(draggedWeight); draggedWeight.style.left = '50%'; draggedWeight.style.top = '35px'; draggedWeight.style.transform = 'translateX(-50%) rotate(0deg)'; h.currentWeight = draggedWeight; draggedWeight.dataset.hookPos = h.pos; snapped = true; }}
                    }}
                }});
                if (!snapped) resetWeightPosition(draggedWeight); draggedWeight.style.zIndex = 10; draggedWeight = null;
            }});
            document.getElementById('btn-test').addEventListener('click', () => {{
                isTesting = true; let leftTorque = 0, rightTorque = 0;
                hooks.forEach(h => {{ if (h.currentWeight) {{ const mass = parseFloat(h.currentWeight.dataset.mass); if (h.pos < 0) leftTorque += mass * Math.abs(h.pos); else rightTorque += mass * h.pos; }} }});
                let angle = 0; if (leftTorque > rightTorque) angle = -15; else if (rightTorque > leftTorque) angle = 15; 
                beam.style.transform = `rotate(${{angle}}deg)`;
                hooks.forEach(h => {{ if (h.currentWeight) {{ h.currentWeight.style.transform = `translateX(-50%) rotate(${{-angle}}deg)`; }} }});
            }});
            document.getElementById('btn-reset').addEventListener('click', () => {{
                beam.style.transform = 'rotate(0deg)'; isTesting = false;
                hooks.forEach(h => {{ if (h.currentWeight) h.currentWeight.style.transform = `translateX(-50%) rotate(0deg)`; h.currentWeight = null; }});
                weights.forEach(w => resetWeightPosition(w));
            }});
        </script>
    </body>
    </html>
    """

@st.cache_data(ttl=10)
def check_exam_open(_sheet):
    try:
        val = _sheet.acell('E1').value
        return str(val).strip() if val else "0"
    except Exception:
        return "0"
exam_open_flag = check_exam_open(user_sheet)

# =====================================================================
# 🚨 진짜 감점을 먹이는 보이지 않는 버튼 로직
# =====================================================================
st.markdown('<div style="opacity: 0; height: 0px; overflow: hidden;">', unsafe_allow_html=True)
if st.button("HiddenPenalty", key="hidden_penalty"):
    if st.session_state.get('eval_started', False) and st.session_state.get('eval_status') == "진행중":
        st.session_state.eval_penalty += 10
        try:
            result_sheet.update_cell(st.session_state.eval_row_index, 4, st.session_state.eval_penalty)
        except: pass
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)


tab_practice, tab_eval = st.tabs(["🛠️ 수행연습", "🔥 수행평가 실시"])

# ---------------------------------------------------------
# [탭 1] 수행연습 화면 (고정된 질량으로 연습)
# ---------------------------------------------------------
with tab_practice:
    if st.session_state.get('eval_started', False):
        st.error("🚨 [경고] 현재 수행평가가 진행 중입니다!")
        st.warning("부정행위 방지를 위해 평가 중에는 연습 화면을 열 수 없습니다.")
    else:
        st.header("🛠️ 미지 시료 질량 찾기 연습")
        st.info("💡 실전에서는 A, B, C의 질량이 변합니다! 어떻게 평형을 맞추는지 미리 감을 익혀보세요.")
        # 연습용 고정 질량 (A=5, B=15, C=20)
        components.html(get_sim_html(5, 15, 20), height=650, scrolling=False)

# ---------------------------------------------------------
# [탭 2] 수행평가 실시 화면 (학생별 랜덤 질량 부여!)
# ---------------------------------------------------------
with tab_eval:
    st.header("🔥 돌림힘 수행평가 실시")
    
    if exam_open_flag != '1':
        st.error("🔒 **현재 수행평가가 비활성화되어 있습니다.**")
        st.info("선생님께서 구글 시트의 [회원정보] 탭 **E1 셀**에 숫자 **1**을 입력하셔야 평가가 시작됩니다.")
    else:
        if 'eval_db_checked' not in st.session_state:
            st.session_state.eval_db_checked = True
            st.session_state.eval_status = None
            st.session_state.eval_row_index = None
            st.session_state.eval_penalty = 0
            st.session_state.eval_started = False
            st.session_state.eval_results = None
            
            all_rows = result_sheet.get_all_values()
            for i, row in enumerate(all_rows):
                if len(row) > 0 and row[0] == s_id:
                    st.session_state.eval_row_index = i + 1 
                    st.session_state.eval_status = row[2] 
                    st.session_state.eval_penalty = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                    
                    if st.session_state.eval_status == "진행중":
                        st.session_state.eval_penalty += 10
                        result_sheet.update_cell(st.session_state.eval_row_index, 4, st.session_state.eval_penalty) 
                        st.session_state.eval_started = True
                        st.toast("🚨 비정상적인 이탈/새로고침이 감지되어 10점 감점되었습니다!")
                    elif st.session_state.eval_status == "완료":
                        st.session_state.eval_started = True
                        st.session_state.eval_results = {
                            "base_score": int(row[5]),
                            "final_score": int(row[6])
                        }
                    break

        is_completed = (st.session_state.eval_status == "완료")
        start_eval = st.toggle("✍️ 수행평가 응시 시작 (주의: 켜진 상태로 화면을 이탈하거나 끄면 10점 감점)", 
                               value=st.session_state.eval_started, 
                               disabled=is_completed)
            
        if start_eval and not st.session_state.eval_started:
            st.session_state.eval_started = True
            if st.session_state.eval_status is None:
                st.session_state.eval_status = "진행중"
                try:
                    result_sheet.append_row([s_id, s_name, "진행중", 0, "", "", ""])
                    st.session_state.eval_row_index = len(result_sheet.get_all_values())
                except: pass
            st.rerun() 

        elif not start_eval and st.session_state.eval_started:
            st.session_state.eval_started = False
            if st.session_state.eval_status == "진행중":
                st.session_state.eval_penalty += 10
                try:
                    result_sheet.update_cell(st.session_state.eval_row_index, 4, st.session_state.eval_penalty)
                except: pass
                st.error("🚨 [경고] 시험 스위치를 임의로 껐습니다. 10점이 감점되었습니다! 다시 켜서 이어서 푸세요.")
            st.rerun()

        if st.session_state.eval_started and st.session_state.eval_status == "진행중":
            st.warning("🚨 [주의] 평가가 진행 중입니다. 다른 탭으로 이동하거나 화면을 끄면 감점 처리됩니다.")
            
            # 자바스크립트가 화면 이탈 감지 시, 위에 숨겨둔 파이썬 감점 버튼을 클릭!
            components.html(
                """
                <script>
                document.addEventListener("visibilitychange", function() {
                    if (document.hidden) { 
                        try {
                            window.parent.alert("🚨 [경고] 화면 이탈이 감지되었습니다! (10점 감점)");
                            var btns = window.parent.document.querySelectorAll("button");
                            for (var i = 0; i < btns.length; i++) {
                                if (btns[i].innerText.includes("HiddenPenalty")) {
                                    btns[i].click();
                                    break;
                                }
                            }
                        } catch(e) { console.log(e); }
                    }
                });
                </script>
                """, height=0
            )
            
            # 🌟 [수정 완료] 실전용 학생별 시뮬레이션 표시!
            components.html(get_sim_html(eval_mass_a, eval_mass_b, eval_mass_c), height=650, scrolling=False)
            
            with st.form("eval_form"):
                st.subheader("📝 수행평가 답안지 (총 100점)")
                
                # 시뮬레이션 결과 입력란 (각 10점)
                st.markdown("---")
                st.markdown("### [Part 1] 가상 실험 결과")
                # 🖼️ 나중에 그림 추가: st.image("img/sim_q.png", use_container_width=True)
                mass_A = st.number_input("**[10점]** 미지 시료 **A**의 질량은 몇 kg 입니까?", step=1, value=None)
                mass_B = st.number_input("**[10점]** 미지 시료 **B**의 질량은 몇 kg 입니까?", step=1, value=None)
                mass_C = st.number_input("**[10점]** 미지 시료 **C**의 질량은 몇 kg 입니까?", step=1, value=None)

                # 기존 퀴즈 (배점 조정)
                st.markdown("---")
                st.markdown("### [Part 2] 돌림힘과 평형 이론")
                
                st.markdown("**문제 1. [객관식] (10점)** 자동차 바퀴의 꽉 조여진 볼트를 스패너로 풀려고 합니다. 볼트(회전축)로부터 가까운 A 지점과 먼 B 지점 중, 더 적은 힘으로 볼트를 풀 수 있는 곳은 어디이며 그 이유는 무엇입니까?")
                st.image("img/q1_spanner.png", use_container_width=True)
                a1 = st.radio("1번 답 선택", ["A 지점 (회전축에 가까울수록 돌림힘이 커지므로)", "B 지점 (회전축에서 멀수록 작은 힘으로도 큰 돌림힘을 낼 수 있으므로)", "두 지점 모두 필요한 힘은 같다."], index=None, key="a1")
                
                st.markdown("**문제 2. [단답식] (10점)** 무게를 무시할 수 있는 시소의 받침점으로부터 왼쪽으로 2 m 떨어진 곳에 질량이 10 kg인 물체가 놓여 있습니다. 이 시소가 수평을 유지하기 위해 오른쪽으로 5 m 떨어진 곳에 놓아야 할 물체 X의 질량은 몇 kg입니까?")
                st.image("img/q2_seesaw.png", use_container_width=True)
                a2 = st.number_input("2번 답 입력 (숫자만)", step=1, value=None, key="a2")
                
                st.markdown("**문제 3. [단답식] (10점)** 길이가 4 m이고 질량이 2 kg인 균일한 막대가 있습니다. 막대의 왼쪽 끝에서 1 m 떨어진 지점에 받침대를 놓았습니다. 이 막대가 수평을 이루도록 하려면 막대의 왼쪽 끝부분에 몇 kg의 추를 매달아야 합니까?")
                st.image("img/q3_stick.png", use_container_width=True)
                a3 = st.number_input("3번 답 입력 (숫자만)", step=1, value=None, key="a3")
                
                st.markdown("**문제 4. [객관식] (10점)** 두 개의 기둥 A(왼쪽)와 B(오른쪽)가 떠받치고 있는 수평 다리 위를 무거운 트럭이 지나가고 있습니다. 트럭이 기둥 B에 더 가깝게 위치해 있을 때, 다리를 떠받치는 힘(수직항력)의 크기에 대한 설명으로 옳은 것은?")
                st.image("img/q4_bridge.png", use_container_width=True)
                a4 = st.radio("4번 답 선택", ["기둥 A가 받는 힘이 더 크다.", "기둥 B가 받는 힘이 더 크다.", "기둥 A와 B가 받는 힘은 같다."], index=None, key="a4")
                
                st.markdown("**문제 5. [객관식] (15점)** 아반떼와 같이 차체가 낮고 바닥 면적이 넓은 승용차와, 짐을 높게 쌓아 올려 차체가 높은 화물차가 동일한 각도의 굽은 경사로를 달리고 있습니다. 두 차량 중 더 안정적인 차량과 그 이유로 올바른 것은?")
                st.image("img/q5_car.png", use_container_width=True)
                a5 = st.radio("5번 답 선택", ["승용차 (무게중심이 낮고 지지면이 넓어 안정성이 높다.)", "화물차 (질량이 더 커서 관성에 의해 안정성이 높다.)", "두 차량의 안정성은 동일하다."], index=None, key="a5")
                
                st.markdown("**문제 6. [단답식 - 심화] (15점)** 건물 옥상 밖으로 2 m가 튀어나오도록 널빤지를 놓았습니다. 널빤지 전체의 길이는 6 m이고, 질량은 10 kg으로 균일합니다. 질량이 5 kg인 고양이가 옥상에서 출발하여 밖으로 튀어나온 널빤지 위를 조심스럽게 걸어갑니다. 널빤지가 뒤집어지기 직전까지 고양이는 옥상 모서리(받침점)로부터 최대 몇 m까지 걸어갈 수 있습니까?")
                st.image("img/q6_cat.png", use_container_width=True)
                a6 = st.number_input("6번 답 입력 (숫자만)", step=1, value=None, key="a6")
                
                st.markdown("---")
                submitted = st.form_submit_button("최종 답안 제출하기")
                
                if submitted:
                    if None in [mass_A, mass_B, mass_C, a1, a2, a3, a4, a5, a6]:
                        st.error("⚠️ 풀지 않은 문제가 있습니다. 모든 칸을 채워주세요!")
                    else:
                        base_score = 0
                        correct_count = 0
                        
                        # 🌟 학생마다 다르게 출제된 A, B, C 정답과 비교하여 채점합니다!
                        if mass_A == eval_mass_a: base_score += 10; correct_count += 1
                        if mass_B == eval_mass_b: base_score += 10; correct_count += 1
                        if mass_C == eval_mass_c: base_score += 10; correct_count += 1
                        
                        # Part 2 채점
                        if a1 == "B 지점 (회전축에서 멀수록 작은 힘으로도 큰 돌림힘을 낼 수 있으므로)": base_score += 10; correct_count += 1
                        if a2 == 4: base_score += 10; correct_count += 1
                        if a3 == 2: base_score += 10; correct_count += 1
                        if a4 == "기둥 B가 받는 힘이 더 크다.": base_score += 10; correct_count += 1
                        if a5 == "승용차 (무게중심이 낮고 지지면이 넓어 안정성이 높다.)": base_score += 15; correct_count += 1
                        if a6 == 2: base_score += 15; correct_count += 1
                        
                        final_score = base_score - st.session_state.eval_penalty
                        
                        try:
                            result_sheet.update_cell(st.session_state.eval_row_index, 3, "완료")
                            result_sheet.update_cell(st.session_state.eval_row_index, 4, st.session_state.eval_penalty)
                            result_sheet.update_cell(st.session_state.eval_row_index, 5, correct_count)
                            result_sheet.update_cell(st.session_state.eval_row_index, 6, base_score)
                            result_sheet.update_cell(st.session_state.eval_row_index, 7, final_score)
                            
                            st.session_state.eval_status = "완료"
                            st.session_state.eval_results = {"base_score": base_score, "final_score": final_score}
                            st.rerun()
                        except Exception as e:
                            st.error(f"구글 시트 저장 실패! 오류: {e}")

        if st.session_state.eval_status == "완료" and st.session_state.eval_results is not None:
            base_score = st.session_state.eval_results["base_score"]
            final_score = st.session_state.eval_results["final_score"]
            
            st.divider()
            st.subheader("📊 수행평가 채점 결과")
            st.write(f"* 취득 점수: **{base_score}점** (100점 만점)")
            if st.session_state.eval_penalty > 0:
                st.write(f"* 이탈/새로고침 감점: **-{st.session_state.eval_penalty}점**")
            st.write(f"### 최종 점수: {final_score}점")
            st.success("✅ 제출이 완료되었습니다. 수고하셨습니다!")
