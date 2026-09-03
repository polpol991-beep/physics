import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="물리 학습 시스템", page_icon="🏫")

# 1. 구글 시트 연결 (DB 역할)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os
current_folder = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(current_folder, "credentials.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(creds)

# 🌟 여기에 만든 구글 시트 파일 이름을 정확히 적으세요!
spreadsheet = client.open("2026 물리학") 
user_sheet = spreadsheet.worksheet("회원정보") # 회원정보 탭 연결

st.title("👨‍🎓 물리 학습 시스템")

# 세션 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 로그인 성공 화면
if st.session_state.logged_in:
    st.success(f"환영합니다! **{st.session_state.student_id} {st.session_state.student_name}** 학생")
    st.info("👈 왼쪽 사이드바 메뉴에서 **'1_힘과_운동'**을 클릭해 학습과 평가를 시작하세요.")
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.clear()
        st.rerun()

# 로그인 / 회원가입 화면
else:
    tab_login, tab_signup = st.tabs(["로그인", "회원가입"])
    
    # [로그인 탭]
    with tab_login:
        st.subheader("로그인")
        login_id = st.text_input("학번", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", key="login_pw")
        
        if st.button("로그인"):
            users = user_sheet.get_all_records() # 시트의 모든 정보 가져오기
            # 학번과 비밀번호가 일치하는 줄(데이터) 찾기
            valid_user = next((u for u in users if str(u['학번']) == login_id and str(u['비밀번호']) == login_pw), None)
            
            if valid_user:
                st.session_state.logged_in = True
                st.session_state.student_id = str(valid_user['학번'])
                st.session_state.student_name = valid_user['이름']
                st.rerun()
            else:
                st.error("학번이나 비밀번호가 일치하지 않습니다.")
                
    # [회원가입 탭]
    with tab_signup:
        st.subheader("처음이라면 회원가입을 해주세요")
        new_id = st.text_input("학번 (예: 10101)")
        new_name = st.text_input("이름")
        new_pw = st.text_input("비밀번호 (기억하기 쉬운 것으로!)", type="password")
        
        if st.button("가입하기"):
            if new_id and new_name and new_pw:
                user_sheet.append_row([new_id, new_name, new_pw]) # 구글 시트에 한 줄 추가!
                st.success("✅ 가입이 완료되었습니다! 옆의 '로그인' 탭에서 로그인해 주세요.")
            else:
                st.warning("⚠️ 학번, 이름, 비밀번호를 모두 입력해 주세요.")
