from word_list import word_list
from class_main import Smart_Vocab

def main():
    trainer = Smart_Vocab(word_list)
    trainer.start_learn()
    
    while True:
        # 1. 학습 시작
        start = input("\n학습을 시작: Enter (종료: Q)")
        if start.lower() == 'Q':
            break
            
        # 2. 단어 출제
        word = trainer.next_word()
        choices = trainer.present_question(word)
        
        # 3. 정답 입력 및 확인 (틀릴 때까지 반복)
        while not trainer.is_answered:
            try:
                answer = int(input("뜻을 고르세요 (1-4): "))
                if 1 <= answer <= 4:
                    correct = trainer.check_answer(answer, choices)
                    if correct:
                        print(f"현재 점수: {trainer.score}/{trainer.total_words}")
                        break  # 다음 문제로
                else:
                    print("틀렸습니다. 다시 선택하세요.")
            except ValueError:
                print("숫자를 입력하세요.")

if __name__ == "__main__":
    main()