import random
import json

class VocabularyTrainer:
    def __init__(self, word_list):
        self.word_list = word_list
        self.current_word = None
        self.is_answered = False
        self.score = 0
        self.total_questions = 0

    def start_learning(self):
        print("=== 영어 단어 학습을 시작합니다! ===")
        return True

    def next_word(self):
        """랜덤으로 다음 단어 선택"""
        self.current_word = random.choice(self.word_list)
        self.is_answered = False
        return self.current_word

    def present_question(self, word_data):
        """단어와 4지선다 출제"""
        print(f"\n단어: **{word_data['word']}**")
        choices = word_data["meanings"].copy()
        random.shuffle(choices)  # 선택지 순서 섞기
        
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        return choices

    def check_answer(self, user_choice, choices):
        """정답 확인 및 피드백"""
        self.total_questions += 1
        
        if choices[user_choice - 1] == self.current_word["meanings"][0]:
            print(f"✅ 정답! '{self.current_word['word']}'의 뜻은 '{self.current_word['meanings']}'입니다.")
            self.score += 1
            self.is_answered = True
            return True
        else:
            print("❌ 틀렸습니다. 다시 시도하세요!")
            return False
