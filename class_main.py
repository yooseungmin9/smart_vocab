import random
import json
from word_list import word_list

class Smart_Vocab:
    def __init__(self, word_list):
        self.word_list = word_list # 단어장
        self.current_word = None # 현재 단어
        self.is_answered = False # 사용자 답변 여부
        self.score = 0 # 점수
        self.total_questions = 0 # 총 문제 수
    
    def start_learn(self):
        print("영어 단어 학습을 시작합니다!")
        return True # 학습 시작
    
    def next_word(self):
        self.current_word = random.choice(self.word_list) # 랜덤 단어 선택
        self.is_answered = False # 답변 초기화
        return self.current_word # 단어 정보 반환
    
    def present_question(self, word_list): # 단어와 선택지 제공
        print(f"\n단어 {word_list['word']}") # 단어 출력
        choices = word_list["meanings"].copy() # 의미 복사
        random.shuffle(choices) # 선택지 섞기

        for i, choice in enumerate(choices, 1): # 선택지 출력
            print(f"{i}. {choice}")
        
        return choices # 선택지 반환
    
    def check_answer(self, user_choice, choices): # 정답 확인
        self.total_questions += 1

        if choices[user_choice - 1] == self.current_word["meanings"][0]: # 정답 확인
            print(f"정답! '{self.current_word['word']}'의 뜻은 '{self.current_word['meanings']}'입니다.")
            self.score += 1 # 점수 증가
            self.is_answered = True # 답변 완료
            return True
        else:
            print("틀렸습니다. 다시 시도하세요!") # 오답 메시지
            return False