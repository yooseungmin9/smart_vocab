import streamlit as st
from word_list import word_list
from class_main import Smart_Vocab
import base64
from PIL import Image
import os
import io

if "trainer" not in st.session_state:
    st.session_state.trainer = Smart_Vocab(word_list)
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


def get_base64_image(image_path, width=60):
    """PNG/JPG 이미지를 리사이징하고 base64로 인코딩"""
    image = Image.open(image_path)
    height = int(width * image.height / image.width)
    resized = image.resize((width, height), resample=Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    resized.save(buffer, format='PNG', optimize=True, quality=95)

    return base64.b64encode(buffer.getvalue()).decode()


def get_base64_svg(svg_path):
    """SVG 파일을 base64로 인코딩"""
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        return base64.b64encode(svg_content.encode('utf-8')).decode()
    except FileNotFoundError:
        return None


def logo_with_title(image_path, title="오늘도 보카", width=80):
    """이미지 확장자를 자동 감지하여 로고와 제목을 표시"""
    if not os.path.exists(image_path):
        st.title(title)
        return

    # 파일 확장자 확인
    file_ext = os.path.splitext(image_path)[1].lower()

    try:
        if file_ext == '.svg':
            # SVG 파일 처리
            svg_base64 = get_base64_svg(image_path)
            if svg_base64:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <img src="data:image/svg+xml;base64,{svg_base64}" 
                         width="{width}" 
                         style="margin-right: 15px; border-radius: 8px;">
                    <h1 style="margin: 0; color: #262730;">{title}</h1>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.title(title)
        else:
            # PNG/JPG 파일 처리
            image_base64 = get_base64_image(image_path, width)
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{image_base64}" 
                     style="margin-right: 15px; border-radius: 8px;">
                <h1 style="margin: 0; color: #262730;">{title}</h1>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"이미지 로딩 오류: {e}")
        st.title(title)

logo_with_title("logo.svg", "오늘도 보카", width=60) # PNG 파일
st.write("Update: 2025.08.19")

MAX_ATTEMPTS = 3

def get_available_words():
    return [
        word for word in word_list
        if st.session_state.word_correct_count.get(word['word'], 0) < MAX_ATTEMPTS
    ]

if st.button("새 단어 / 다음 단어"):
    available_words = get_available_words()
    if available_words:
        st.session_state.trainer = Smart_Vocab(available_words)
        st.session_state.trainer.start_learn()
        st.session_state.current_word = st.session_state.trainer.next_word()
        st.session_state.choices = st.session_state.trainer.present_question(st.session_state.current_word)
        st.session_state.answered = False
    else:
        st.warning("모든 단어를 3번씩 맞췄습니다 🎉")

if st.session_state.current_word:
    word_text = st.session_state.current_word['word']
    correct_count = st.session_state.word_correct_count.get(word_text, 0)
    st.subheader(f"Q: {word_text}")
    st.caption(f"이 단어 정답 횟수: {correct_count}/{MAX_ATTEMPTS}")
    if 'accent' in st.session_state.current_word:
        st.caption(f"🔊 발음: {st.session_state.current_word['accent']}")
    choice = st.radio("뜻을 고르세요.", st.session_state.choices, index=None, key=f"answer_{correct_count}_{word_text}")

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

total_words = len(word_list)
completed_count = len(st.session_state.completed_words)
available_count = len(get_available_words())
st.info(f"진행 상황: {completed_count}/{total_words} 단어 완료")

if st.button("학습 종료하기"):
    st.write("한번 더 누르면 학습을 종료합니다.")
    st.write("다시 시작하려면 [새단어]를 누르세요.")
    st.session_state.trainer = Smart_Vocab(word_list)
    st.session_state.trainer.start_learn()
    st.session_state.current_word = None
    st.session_state.choices = None
    st.session_state.answered = True
    st.session_state.word_correct_count = {}
    st.session_state.completed_words = set()

if available_count == 0:
    st.balloons()
    if st.button("🔄 처음부터 다시 시작"):
        st.session_state.trainer = Smart_Vocab(word_list)
        st.session_state.trainer.start_learn()
        st.session_state.current_word = None
        st.session_state.choices = None
        st.session_state.answered = True
        st.session_state.word_correct_count = {}
        st.session_state.completed_words = set()
        st.rerun()