from __future__ import annotations

import random
import tkinter as tk
from tkinter import font, ttk

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False
        self.score = 0
        self.total = 0
        
        # 💡 [신규] 오답을 저장할 리스트 초기화
        self.incorrect_words: list[dict[str, str]] = []

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("450x320")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

        ttk.Label(root, text="영단어").pack(pady=(16, 4))
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)
        
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        
        ttk.Button(buttons, text="다음", command=self.next_word).pack(side=tk.LEFT, padx=6)
        
        # 💡 [신규] 오답노트 보기 버튼 추가
        self.review_button = ttk.Button(buttons, text="오답노트", command=self.show_review_note)
        self.review_button.pack(side=tk.LEFT, padx=6)

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=8)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def next_word(self) -> None:
        self.current = draw_word(self.words, self.rng)
        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.checked = False
        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return
            
        self.checked = True
        self.total += 1
        user_input = self.answer_entry.get()
        
        if check_answer(self.current, user_input):
            self.score += 1
            self.feedback_var.set("정답입니다!")
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
            
            # 💡 [신규] 틀린 단어와 사용자가 입력한 오답을 기록
            self.incorrect_words.append({
                "term": self.current.term,
                "meaning": self.current.meaning,
                "user_input": user_input if user_input.strip() else "(입력 없음)"
            })
            
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])

    # 💡 [신규] 오답 노트를 새 창으로 보여주는 함수 구현
    def show_review_note(self) -> None:
        review_window = tk.Toplevel()
        review_window.title("📝 오답 노트")
        review_window.geometry("400x300")

        txt_area = tk.Text(review_window, wrap=tk.WORD, font=("NanumGothic", 11))
        txt_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        if not self.incorrect_words:
            txt_area.insert(tk.END, "\n🎉 틀린 단어가 없습니다! 완벽해요!")
            txt_area.config(state=tk.DISABLED)
            return

        txt_area.insert(tk.END, f"❌ 총 {len(self.incorrect_words)}개의 오답이 있습니다.\n\n")
        for idx, item in enumerate(self.incorrect_words, 1):
            line = f"[{idx}] 단어: {item['term']}\n"
            line += f"    - 내가 쓴 답: {item['user_input']}\n"
            line += f"    - 올바른 정답: {item['meaning']}\n"
            line += "-" * 40 + "\n"
            txt_area.insert(tk.END, line)
            
        txt_area.config(state=tk.DISABLED)