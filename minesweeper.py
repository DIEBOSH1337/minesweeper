import tkinter as tk
from tkinter import messagebox
import random
import time


class Game:
    def __init__(self):
        self.rows = 9
        self.cols = 9
        self.mines_count = 10
        
        self.root = tk.Tk()
        self.root.title("Сапёр")
        self.root.resizable(False, False)
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=5, pady=5)
        
        # Верхняя панель
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.timer_label = tk.Label(self.top_frame, text="0", font=('Arial', 16, 'bold'))
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        self.mine_counter_label = tk.Label(self.top_frame, text=f" {self.mines_count}", font=('Arial', 16, 'bold'))
        self.mine_counter_label.pack(side=tk.RIGHT, padx=10)
        
        # Игровые переменные
        self.mines = None
        self.numbers = None
        self.revealed = None
        self.flags = None
        self.flags_count = 0
        self.game_active = True
        self.start_time = 0
        self.time_elapsed = 0
        self.last_click_row = -1
        self.last_click_col = -1
        
        self.buttons = []
        
        self.create_board()
        self.place_mines()
        self.calculate_numbers()
        
        self.root.mainloop()
    
    def create_board(self):
        self.buttons = []
        for i in range(self.rows):
            row_buttons = []
            for j in range(self.cols):
                btn = tk.Button(
                    self.frame,
                    width=2,
                    height=1,
                    font=('Arial', 12, 'bold'),
                    relief=tk.RAISED
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind('<Button-1>', lambda e, r=i, c=j: self.left_click(r, c))
                btn.bind('<Button-3>', lambda e, r=i, c=j: self.right_click(r, c))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags = [[False for _ in range(self.cols)] for _ in range(self.rows)]
    
    def place_mines(self):
        self.mines = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        mines_placed = 0
        
        while mines_placed < self.mines_count:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if not self.mines[row][col]:
                self.mines[row][col] = True
                mines_placed += 1
    
    def calculate_numbers(self):
        self.numbers = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                if self.mines[i][j]:
                    self.numbers[i][j] = -1
                    continue
                
                count = 0
                
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.rows and 0 <= nj < self.cols and self.mines[ni][nj]:
                            count += 1
                
                self.numbers[i][j] = count
    
    def left_click(self, row, col):
        if not self.game_active:
            return
        if self.revealed[row][col] or self.flags[row][col]:
            return
        
        self.last_click_row = row
        self.last_click_col = col
        
        if self.start_time == 0:
            self.start_timer()
        
        if self.mines[row][col]:
            self.game_over(won=False)
        else:
            self.reveal_cell(row, col)
            self.check_win()
    
    def right_click(self, row, col):
        if not self.game_active:
            return
        if self.revealed[row][col]:
            return
        
        self.toggle_flag(row, col)
    
    def reveal_cell(self, row, col):
        if self.revealed[row][col] or self.flags[row][col]:
            return
        
        self.revealed[row][col] = True
        self.buttons[row][col].config(
            text=str(self.numbers[row][col]) if self.numbers[row][col] > 0 else '',
            state=tk.DISABLED,
            relief=tk.SUNKEN,
            bg='light gray'
        )
        
        if self.numbers[row][col] == 0:
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = row + di, col + dj
                    if 0 <= ni < self.rows and 0 <= nj < self.cols and not self.revealed[ni][nj]:
                        self.reveal_cell(ni, nj)
    
    def toggle_flag(self, row, col):
        if self.revealed[row][col]:
            return
        
        if not self.flags[row][col] and self.flags_count < self.mines_count:
            self.flags[row][col] = True
            self.buttons[row][col].config(text='🚩', fg='red')
            self.flags_count += 1
        
        elif self.flags[row][col]:
            self.flags[row][col] = False
            self.buttons[row][col].config(text='', fg='black')
            self.flags_count -= 1
        
        self.update_mine_counter()
    
    def update_mine_counter(self):
        remaining = self.mines_count - self.flags_count
        self.mine_counter_label.config(text=f" {remaining}")
    
    def start_timer(self):
        self.start_time = time.time()
        self.update_timer()
    
    def update_timer(self):
        if not self.game_active:
            return
        
        self.time_elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"{self.time_elapsed}")
        self.timer_label.after(1000, self.update_timer)
    
    def check_win(self):
        safe_cells_count = self.rows * self.cols - self.mines_count
        revealed_safe = sum(row.count(True) for row in self.revealed) - self.mines_count
        
        if revealed_safe == safe_cells_count:
            self.game_active = False
            self.game_over(won=True)
            return True
        return False
    
    def game_over(self, won):
        self.game_active = False
        if won:
            messagebox.showinfo("Победа!", f"Вы выиграли! Время: {self.time_elapsed} сек.")
        else:
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.mines[i][j]:
                        self.buttons[i][j].config(text='💣', bg='red' if (i, j) == (self.last_click_row, self.last_click_col) else 'orange')
            messagebox.showinfo("Поражение", "Вы наступили на мину!")


if __name__ == "__main__":
    Game()
