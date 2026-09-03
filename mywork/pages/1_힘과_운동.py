import streamlit as st
import streamlit.components.v1 as components
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

st.set_page_config(page_title="1. 힘과 운동", page_icon="🚀", layout="wide")

# =====================================================================
# 🛠️ 구글 시트 연동 세팅
# =====================================================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 👇 현재 방(pages 폴더)에서 한 칸 밖(mywork 폴더)으로 나가서 열쇠와 사진을 찾는 마법의 코드입니다.
current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder) # 상위 폴더로 이동!
key_path = os.path.join(parent_folder, "credentials.json")

creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open("2026 물리학")
result_sheet = spreadsheet.worksheet("1단원_결과") # 👈 '1단원_결과' 탭에 연결

# 학생 정보 가져오기
s_id = str(st.session_state.get('student_id', '00000'))
s_name = st.session_state.get('student_name', '테스트학생')

# =====================================================================
# 🎨 화면 상단 타이틀
# =====================================================================
if 'student_name' in st.session_state and st.session_state.student_name:
    st.success(f"현재 로그인된 학생: **{s_id} {s_name}**")
else:
    st.success("💡 단독 실행 모드 (테스트용)")

# =====================================================================
# 📑 탭(Tabs) 생성
# =====================================================================
tab_learn, tab_quiz = st.tabs(["📚 개념 학습", "📝 형성평가 (퀴즈)"])

# ---------------------------------------------------------
# [탭 1] 개념 학습 화면 (시험 중일 땐 숨김)
# ---------------------------------------------------------
with tab_learn:
    if st.session_state.get('exam_started', False):
        st.error("🚨 [경고] 현재 형성평가가 진행 중입니다!")
        st.warning("부정행위 방지를 위해 시험 중에는 개념 학습을 펼쳐볼 수 없습니다.")
    else:
        st.header("📖 핵심 개념 요약")
        with st.expander("1. 힘의 평형과 돌림힘", expanded=True):
            st.markdown("### 가. 힘의 평형")
            st.markdown("* **알짜힘:** 물체에 작용하는 모든 힘을 합친 것을 의미합니다.")
            # 🌟 [수정 완료] 사진 경로 앞에 parent_folder 연결
            st.image(os.path.join(parent_folder, "img", "image_e81eaa.png"), caption="힘의 평형과 돌림힘의 평형을 모두 만족하는 선반", use_container_width=True)
            st.markdown("* **힘의 평형:** 물체에 작용하는 알짜힘이 0인 상태를 말합니다.")
            
        with st.expander("2. 물체의 운동", expanded=True):
            st.markdown("### 가. 이동 거리와 변위")
            # 🌟 [수정 완료] 사진 경로 앞에 parent_folder 연결
            st.image(os.path.join(parent_folder, "img", "image03.png"), caption="경로에 따른 이동 거리와 변위의 차이", use_container_width=True)
            st.markdown("* **이동 거리:** 물체가 실제로 움직인 총거리입니다.")

        with st.expander("3. 운동량과 충격량"):
            st.markdown("### 가. 운동량과 운동량 보존 법칙")
            # 🌟 [수정 완료] 사진 경로 앞에 parent_folder 연결
            st.image(os.path.join(parent_folder, "img", "image11.png"), caption="두 물체의 충돌 전후", use_container_width=True)
            st.markdown("* **운동량:** 운동하는 물체가 가진 운동하는 정도를 나타내는 물리량입니다.")

# ---------------------------------------------------------
# [탭 2] 형성평가 화면 (🔥 무적의 방어 로직 적용)
# ---------------------------------------------------------
with tab_quiz:
    st.header("✅ 1단원 형성평가")
    
    # 🌟 1. 새로고침 방어: 시트에서 내 기록 찾기
    if 'db_checked' not in st.session_state:
        st.session_state.db_checked = True
        st.session_state.db_status = None
        st.session_state.row_index = None
        st.session_state.cheating_penalty = 0
        st.session_state.exam_started = False
        st.session_state.quiz_results = None
        
        # 구글 시트를 위에서부터 훑어서 내 학번이 있는지 찾습니다.
        all_rows = result_sheet.get_all_values()
        for i, row in enumerate(all_rows):
            if len(row) > 0 and row[0] == s_id:
                st.session_state.row_index = i + 1 # 엑셀은 1번 줄부터 시작하므로 +1
                st.session_state.db_status = row[2] # C열(상태) 확인
                st.session_state.cheating_penalty = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                
                # 🚨 시험 보다가 도망친(새로고침한) 경우!
                if st.session_state.db_status == "진행중":
                    st.session_state.cheating_penalty += 10 # 10점 추가 감점
                    result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty) # 시트에 감점 업데이트
                    st.session_state.exam_started = True
                    st.toast("🚨 비정상적인 새로고침이 감지되어 10점 감점되었습니다!")
                
                # ✅ 이미 퀴즈를 정상 제출한 경우
                elif st.session_state.db_status == "완료":
                    st.session_state.exam_started = True
                    st.session_state.quiz_results = {
                        "correct_count": int(row[4]),
                        "base_score": int(row[5])
                    }
                break

    # 🌟 2. 문제 출제 (동일한 학생은 항상 동일한 문제 고정!)
    if 'quiz_questions' not in st.session_state:
        all_questions = [
            {"level": "중", "q": "길이가 $L$인 질량이 균일한 막대가 줄 A, B에 매달려 정지해 있다. 줄 A는 왼쪽 끝에, 줄 B는 오른쪽 끝에서 $\\frac{1}{3}L$ 떨어진 곳에 있다. A, B가 막대를 당기는 힘의 크기 비 $\\frac{F_A}{F_B}$는?", "img": "img/스크린샷 2026-08-31 154719.png", "options": ["1/3", "1/2", "1", "2", "3"], "answer": "1/2"},
            {"level": "상", "q": "바닥면 한 변의 길이가 10 cm이고 높이가 12 cm인 균일한 직육면체 구조물의 한끝을 민다. 구조물이 넘어지지 않기 위한 $\\tan \\theta$의 최댓값은?", "img": "img/스크린샷 2026-08-31 154725.png", "options": ["1/6", "2/5", "1/2", "2/3", "5/6"], "answer": "5/6"},
            {"level": "하", "q": "직선상에서 운동하는 네 물체 A~D의 속도-시간 그래프에서 A와 C는 기울기가 양수인 직선, B와 D는 기울기가 0인 직선이다 (B의 속도>0, D의 속도=0). 이에 대한 설명으로 옳은 것은?", "img": "img/스크린샷 2026-08-31 154734.png", "options": ["A와 C의 속도는 항상 같다.", "A와 C는 속도가 일정한 운동을 가한다.", "B와 D는 정지해 있다.", "B와 D의 가속도는 0이다.", "3초 동안 변위의 크기는 B가 가장 크다."], "answer": "B와 D의 가속도는 0이다."},
            {"level": "중", "q": "마찰이 없는 수평면에 질량이 각각 $m, 2m, m$인 물체 A, B, C가 있다. 이들에게 각각 $F, F, 3F$의 알짜힘이 작용할 때, 세 물체의 가속도 비 $a_A : a_B : a_C$ 는?", "img": "img/스크린샷 2026-08-31 154745.png", "options": ["1 : 1 : 3", "2 : 1 : 6", "1 : 2 : 3", "2 : 2 : 6", "3 : 1 : 2"], "answer": "2 : 1 : 6"},
            {"level": "상", "q": "속도 $v$로 달리던 자동차가 브레이크를 밟아 정지할 때까지의 이동 거리를 $s$라 하자. 알짜힘이 일정할 때, 속도가 $3v$가 되면 제동거리 $s$는 몇 배가 되는가?", "img": "img/스크린샷 2026-08-31 154803.png", "options": ["3배", "6배", "9배", "12배", "15배"], "answer": "9배"},
            {"level": "중", "q": "물체 A, B를 손바닥으로 받쳐 정지해 있다. A가 B를 누르는 힘 $F_{AB}$, B가 손을 누르는 힘 $F_{B손}$, 손이 B를 떠받치는 힘 $F_{손B}$의 크기를 옳게 비교한 것은?", "img": "img/스크린샷 2026-08-31 154822.png", "options": ["$F_{AB} > F_{B손} > F_{손B}$", "$F_{AB} > F_{B손} = F_{손B}$", "$F_{AB} = F_{B손} < F_{손B}$", "$F_{AB} < F_{B손} < F_{손B}$", "$F_{AB} < F_{B손} = F_{손B}$"], "answer": "$F_{AB} < F_{B손} = F_{손B}$"},
            {"level": "상", "q": "질량 $m$인 선수 A가 $2v$의 속도로 운동하다가, $v$의 속도로 운동하는 질량 $0.8m$인 선수 B를 밀었다. 밀고 난 직후 A의 속도가 $0.5v$가 되었다면, B의 속도는?", "img": "img/스크린샷 2026-08-31 154849.png", "options": ["0", "2/3 v", "23/8 v", "13/4 v", "15/4 v"], "answer": "23/8 v"},
            {"level": "중", "q": "고무줄로 연결된 수레 A(질량 2m)와 B(질량 m)를 잡고 있다가 동시에 놓았다. 두 수레가 충돌하여 한 덩어리가 되었다. 충돌 직전 A의 속도가 0.2 m/s라면 충돌 직후 한 덩어리가 된 A, B의 속도는?", "img": "img/스크린샷 2026-08-31 154831.png", "options": ["0 m/s", "0.05 m/s", "0.07 m/s", "0.12 m/s", "0.15 m/s"], "answer": "0 m/s"},
            {"level": "하", "q": "크기가 같은 두 힘 $F_1, F_2$를 정지해있는 막대의 두 지점에 그림과 같이 작용할 때 옳은 것은? (막대의 알짜힘은 0, 돌림힘은 0이 아님)", "img": "img/스크린샷 2026-08-31 154701.png", "options": ["막대에 작용하는 알짜힘은 0이 아니다.", "막대는 직선 운동을 한다.", "막대는 회전 운동을 한다.", "돌림힘의 평형을 이룬다.", "아무런 운동도 하지 않는다."], "answer": "막대는 회전 운동을 한다."},
            {"level": "하", "q": "직선상에서 운동하는 물체의 속도-시간 그래프에서 0\\~10초 구간은 속도가 증가하고, 10\\~20, $t$\\~30초는 등속, 20\\~$t$, 30\\~40초는 속도가 감소한다. 가속도의 크기가 가장 큰 구간은?", "img": "img/스크린샷 2026-08-31 154751.png", "options": ["0~10초", "10~20초", "20~30초", "30~40초", "모두 같다"], "answer": "30~40초"},
            {"level": "하", "q": "길이가 $3L$인 균일한 막대에 수직 방향으로 여러 힘이 작용할 때 막대가 회전하지 않는 조건은?", "img": None, "options": ["알짜힘만 0이면 된다.", "알짜 돌림힘만 0이면 된다.", "알짜힘과 알짜 돌림힘이 모두 0이어야 한다.", "무게중심에 힘이 작용해야 작용해야 한다.", "힘의 크기가 모두 같아야 한다."], "answer": "알짜힘과 알짜 돌림힘이 모두 0이어야 한다."}
        ]
        
        # 학번을 '시드(Seed)'로 삼아, 도망갔다 와도 항상 똑같은 문제가 나오도록 고정합니다!
        random.seed(s_id)
        
        easy_qs = [q for q in all_questions if q["level"] == "하"]
        med_qs = [q for q in all_questions if q["level"] == "중"]
        hard_qs = [q for q in all_questions if q["level"] == "상"]
        
        selected_qs = random.sample(easy_qs, 2) + random.sample(med_qs, 2) + random.sample(hard_qs, 1)
        random.shuffle(selected_qs)
        
        st.session_state.quiz_questions = selected_qs
        random.seed() # 다음 랜덤 작업을 위해 초기화

    # 🌟 3. 스위치 (이미 완료했으면 비활성화)
    is_completed = (st.session_state.db_status == "완료")
    start_exam = st.toggle("✍️ 형성평가 응시 시작 (주의: 새로고침하거나 끄면 10점 감점)", 
                           value=st.session_state.exam_started, 
                           disabled=is_completed, 
                           key="exam_toggle")
        
    # [스위치를 처음 켠 순간!] -> 구글 시트에 "진행중" 생성
    if start_exam and st.session_state.db_status is None:
        st.session_state.exam_started = True
        st.session_state.db_status = "진행중"
        result_sheet.append_row([s_id, s_name, "진행중", 0, "", "", ""])
        st.session_state.row_index = len(result_sheet.get_all_values())
        st.rerun() # 화면 새로고침해서 스위치 켜진 상태 고정

    # [스위치를 끈 순간!] -> 감점 폭탄
    if not start_exam and st.session_state.exam_started and st.session_state.db_status == "진행중":
        st.session_state.cheating_penalty += 10
        result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty)
        st.session_state.exam_started = False
        st.error("🚨 [경고] 시험 스위치를 임의로 껐습니다. 10점이 감점되었습니다! 퀴즈를 보려면 다시 켜세요.")

    # 🌟 4. 시험 진행 폼
    if st.session_state.exam_started and st.session_state.db_status == "진행중":
        st.warning("🚨 [주의] 평가가 진행 중입니다. 화면을 이탈하면 경고 알림이 발생합니다.")
        
        components.html(
            """
            <script>
            document.addEventListener("visibilitychange", function() {
                if (document.hidden) {
                    window.parent.alert("🚨 [경고] 화면 이탈이 감지되었습니다! 부정행위로 간주될 수 있습니다.");
                }
            });
            </script>
            """,
            height=0
        )
        
        with st.form("quiz_form"):
            st.markdown("---")
            user_answers = []
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"#### 문제 {i+1}.")
                # 🌟 [수정 완료] 퀴즈 이미지 경로에도 parent_folder 연결
                if q.get("img"):
                    img_path = os.path.join(parent_folder, q["img"])
                    st.image(img_path, use_container_width=True)
                st.write(q["q"])
                ans = st.radio("선택해 주세요.", q["options"], key=f"q_{i}", index=None)
                user_answers.append(ans)
            
            st.markdown("---")
            submitted = st.form_submit_button("답안 제출하기")
            
            if submitted:
                if None in user_answers:
                    st.error("⚠️ 풀지 않은 문제가 있습니다. 모든 문제의 답을 선택해 주세요!")
                else:
                    correct_count = 0
                    for i, q in enumerate(st.session_state.quiz_questions):
                        if user_answers[i] == q["answer"]:
                            correct_count += 1
                    
                    base_score = 100 - ((5 - correct_count) * 10)
                    final_score = base_score - st.session_state.cheating_penalty
                    
                    # 🔥 채점 완료 후 구글 시트에 업데이트!
                    try:
                        result_sheet.update_cell(st.session_state.row_index, 3, "완료")
                        result_sheet.update_cell(st.session_state.row_index, 4, st.session_state.cheating_penalty)
                        result_sheet.update_cell(st.session_state.row_index, 5, correct_count)
                        result_sheet.update_cell(st.session_state.row_index, 6, base_score)
                        result_sheet.update_cell(st.session_state.row_index, 7, final_score)
                        
                        st.session_state.db_status = "완료"
                        st.session_state.quiz_results = {"correct_count": correct_count, "base_score": base_score}
                        st.rerun() # 결과 보여주기 위해 새로고침
                    except Exception as e:
                        st.error(f"구글 시트 저장 실패! 오류 내용: {e}")

    # 🌟 5. 완료 후 결과 보여주기
    if st.session_state.db_status == "완료" and st.session_state.quiz_results is not None:
        base_score = st.session_state.quiz_results["base_score"]
        final_score = base_score - st.session_state.cheating_penalty
        
        st.divider()
        st.subheader("📊 채점 결과")
        st.write(f"* 맞힌 문제: **5문제 중 {st.session_state.quiz_results['correct_count']}문제**")
        st.write(f"* 기본 점수: **{base_score}점** (100점 만점 / 틀린 문제당 -10점)")
        if st.session_state.cheating_penalty > 0:
            st.write(f"* 스위치 OFF / 새로고침 감점: **-{st.session_state.cheating_penalty}점**")
        st.write(f"### 최종 점수: {final_score}점")
        
        if final_score == 100:
            st.success("🎉 완벽합니다! 만점입니다!")
        elif final_score >= 80:
            st.info("👍 잘했습니다! 조금만 더 복습해 볼까요?")
        else:
            st.error("💪 개념 학습 탭으로 돌아가서 내용을 다시 한번 꼼꼼히 확인해 보세요!")
