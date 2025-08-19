import streamlit as st
from eng_word_list import eng_word_list
from jpn_word_list import jpn_word_list
from class_main import Smart_vocab
st.markdown("""
<style>
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        text-align: center;
    }
    .stButton > button {
        margin: 0 auto;
        display: block;
    }
    .stRadio > div {
        text-align: left;
        margin: 0 auto;
        display: inline-block;
    }
    .stSelectbox > div {
        margin: 0 auto;
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)
language_dict = {
    '영어': eng_word_list,
    '일본어': jpn_word_list,
}
# 세션 상태 초기화
if "selected_language" not in st.session_state:
    st.session_state.selected_language = '영어'
if "trainer" not in st.session_state:
    st.session_state.trainer = Smart_vocab(language_dict[st.session_state.selected_language])
    st.session_state.trainer.start_learn()
if "current_word" not in st.session_state:
    st.session_state.current_word = None
if "choices" not in st.session_state:
    st.session_state.choices = None
if "answered" not in st.session_state:
    st.session_state.answered = True
if "word_correct_count" not in st.session_state:
    st.session_state.word_correct_count = {}
if "completed_words" not in st.session_state:
    st.session_state.completed_words = set()
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>📚오늘도 보카 Oneldo Vocab</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>오늘의 날짜 : 2025년 08월 19일</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.sidebar.header("🌍언어 선택")
default_language = '영어'
selected_language = st.sidebar.selectbox(
    "언어를 선택하세요:",
    options=list(language_dict.keys()),
    index=list(language_dict.keys()).index(default_language)
)
# 언어가 변경되었을 때 세션 상태 리셋
if selected_language != st.session_state.selected_language:
    st.session_state.selected_language = selected_language
    st.session_state.trainer = Smart_vocab(language_dict[selected_language])
    st.session_state.trainer.start_learn()
    st.session_state.current_word = None
    st.session_state.choices = None
    st.session_state.answered = True
    st.session_state.word_correct_count = {}
    st.session_state.completed_words = set()
# 현재 선택된 언어 정보 표시
st.sidebar.info(f"📍 현재 선택: **{selected_language}**")
# 현재 선택된 언어의 단어 리스트 가져오기
current_word_list = language_dict[st.session_state.selected_language]
MAX_ATTEMPTS = 3
def get_available_words():
    return [
        word for word in current_word_list
        if st.session_state.word_correct_count.get(word['word'], 0) < MAX_ATTEMPTS
    ]
def get_next_word():
    available_words = get_available_words()
    if available_words:
        st.session_state.trainer = Smart_vocab(available_words)
        st.session_state.trainer.start_learn()
        st.session_state.current_word = st.session_state.trainer.next_word()
        st.session_state.choices = st.session_state.trainer.present_question(st.session_state.current_word)
        st.session_state.answered = False
    else:
        st.warning("모든 단어를 3번씩 맞췄습니다 🎉")
if st.button("오늘도 학습"):
    get_next_word()
if st.session_state.current_word:
    word_text = st.session_state.current_word['word']
    correct_count = st.session_state.word_correct_count.get(word_text, 0)
    st.subheader(f"Q: {word_text}")
    if 'accent' in st.session_state.current_word:
        st.caption(f"🔊 발음: {st.session_state.current_word['accent']}")
    st.caption(f"이 단어 정답 횟수: {correct_count}/{MAX_ATTEMPTS}")
    choice = st.radio("뜻을 고르세요.", st.session_state.choices, index=None, key=f"answer_{correct_count}_{word_text}")
    if st.session_state.current_word:
        if st.button("다음 단어"):
            if st.session_state.answered:
                get_next_word()
            else:
                st.warning("현재 문제를 먼저 풀어주세요")
    if not st.session_state.answered and choice is not None:
        selected_index = st.session_state.choices.index(choice) + 1
        correct = st.session_state.trainer.check_answer(selected_index, st.session_state.choices)
        if correct:
            st.session_state.answered = True
            st.success("정답 🎉")
            st.info(f"'{word_text}'의 뜻은 '{st.session_state.current_word['correct_meaning']}'입니다.")
            st.session_state.word_correct_count[word_text] = correct_count + 1
            if word_text not in st.session_state.completed_words:
                st.session_state.completed_words.add(word_text)
        else:
            st.error("틀렸습니다. 다시 선택하세요.")
total_words = len(current_word_list)
completed_count = len(st.session_state.completed_words)
available_count = len(get_available_words())
st.info(f"진행 상황: {completed_count}/{total_words} 단어 완료")
if st.button("학습 종료하기"):
    st.write("한번 더 누르면 학습을 종료합니다.")
    st.session_state.trainer = Smart_vocab(current_word_list)
    st.session_state.trainer.start_learn()
    st.session_state.current_word = None
    st.session_state.choices = None
    st.session_state.answered = True
    st.session_state.word_correct_count = {}
    st.session_state.completed_words = set()
if available_count == 0:
    st.balloons()
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.trainer = Smart_vocab(current_word_list)
        st.session_state.trainer.start_learn()
        st.session_state.current_word = None
        st.session_state.choices = None
        st.session_state.answered = True
        st.session_state.word_correct_count = {}
        st.session_state.completed_words = set()
        st.rerun()