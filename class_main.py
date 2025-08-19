import random
import json
from jpn_word_list import word_list

class Smart_Vocab:
    def __init__(self, word_list):
        self.word_list = word_list
        self.current_word = None
        self.is_answered = False
        self.score = 0
        self.total_questions = 0
        self.current_index = 0 
        self.total_words = len(word_list)
    
    def start_learn(self):
        print("일본어 단어 학습시작")
        return True
    
    def next_word(self):
        self.current_word = random.choice(self.word_list)
        self.is_answered = False
        return self.current_word
    
    def present_question(self, word_list):
        print(f"\n단어 {word_list['word']}")
        choices = word_list["meanings"].copy()
        random.shuffle(choices)

        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        return choices
    
    def check_answer(self, user_choice, choices):
        self.total_words = len(self.word_list)

        if choices[user_choice - 1] == self.current_word["meanings"][0]: # 정답 확인
            print(f"정답입니다. '{self.current_word['word']}'의 뜻은 '{self.current_word['correct_meaning']}'입니다.")
            self.score += 1
            self.is_answered = True
            return True
        else:
            print("틀렸습니다.")
            return False