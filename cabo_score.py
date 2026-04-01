import tkinter as tk
from tkinter import messagebox
import json


class CaboScoreTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("卡波(Cabo)计分器")
        self.root.geometry("500x600")

        self.players = []
        self.current_round = 1
        self.scores = []

        self.setup_frame = tk.Frame(root)
        self.setup_frame.pack(pady=20)

        tk.Label(self.setup_frame, text="玩家数量:", font=("Arial", 14)).pack()

        self.player_count_var = tk.IntVar(value=2)
        for i in range(2, 5):
            rb = tk.Radiobutton(
                self.setup_frame,
                text=f"{i}人",
                variable=self.player_count_var,
                value=i,
                font=("Arial", 12),
                command=self.update_player_count,
            )
            rb.pack()

        tk.Label(self.setup_frame, text="输入玩家名称:", font=("Arial", 12)).pack(
            pady=10
        )
        self.name_entries = []
        self.name_frame = tk.Frame(self.setup_frame)
        self.name_frame.pack()
        self.update_player_count()

        tk.Button(
            self.setup_frame,
            text="开始游戏",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            command=self.start_game,
        ).pack(pady=20)

        self.game_frame = None

    def update_player_count(self):
        for widget in self.name_frame.winfo_children():
            widget.destroy()

        self.name_entries = []
        count = self.player_count_var.get()

        for i in range(count):
            tk.Label(self.name_frame, text=f"玩家{i + 1}:", font=("Arial", 10)).grid(
                row=i, column=0, padx=5, pady=2
            )
            entry = tk.Entry(self.name_frame, font=("Arial", 10), width=12)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, f"玩家{i + 1}")
            self.name_entries.append(entry)

    def start_game(self):
        self.players = [entry.get() for entry in self.name_entries]
        if not all(self.players):
            messagebox.showwarning("警告", "请输入所有玩家名称")
            return

        self.scores = [0] * len(self.players)
        self.setup_frame.pack_forget()
        self.create_game_ui()

    def create_game_ui(self):
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(
            self.game_frame,
            text=f"第 {self.current_round} 轮",
            font=("Arial", 18, "bold"),
        ).pack(pady=10)

        self.round_inputs = []
        for i, player in enumerate(self.players):
            player_frame = tk.LabelFrame(
                self.game_frame, text=player, font=("Arial", 12), padx=10, pady=10
            )
            player_frame.pack(fill=tk.X, pady=5)

            tk.Label(player_frame, text="卡牌总和:", font=("Arial", 10)).grid(
                row=0, column=0, sticky=tk.W
            )
            total_entry = tk.Entry(player_frame, font=("Arial", 10), width=8)
            total_entry.grid(row=0, column=1, padx=5)

            cabo_var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                player_frame, text="呼唤CABO", variable=cabo_var, font=("Arial", 10)
            ).grid(row=1, column=0, columnspan=2, sticky=tk.W)

            special_frame = tk.Frame(player_frame)
            special_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)

            shenfeng_var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                special_frame,
                text="神锋特工队(12,12,13,13)",
                variable=shenfeng_var,
                font=("Arial", 9),
            ).pack(side=tk.LEFT)

            self.round_inputs.append(
                {"total": total_entry, "cabo": cabo_var, "shenfeng": shenfeng_var}
            )

        btn_frame = tk.Frame(self.game_frame)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="确定",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.submit_round,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="显示总分",
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            command=self.show_scores,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="新游戏",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            command=self.new_game,
        ).pack(side=tk.LEFT, padx=5)

        self.update_score_display()

    def submit_round(self):
        try:
            totals = []
            has_cabo = False

            for i, inp in enumerate(self.round_inputs):
                total = int(inp["total"].get())
                totals.append(total)
                if inp["cabo"].get():
                    has_cabo = True

            min_total = min(totals)

            for i, inp in enumerate(self.round_inputs):
                total = totals[i]
                is_cabo = inp["cabo"].get()
                is_shenfeng = inp["shenfeng"].get()

                if is_shenfeng:
                    self.scores[i] += 0
                    for j in range(len(self.scores)):
                        if j != i:
                            self.scores[j] += 50
                elif is_cabo:
                    if total == min_total:
                        self.scores[i] += 0
                    else:
                        self.scores[i] += total + 10
                else:
                    self.scores[i] += total

            for i in range(len(self.scores)):
                if self.scores[i] == 100:
                    self.scores[i] = 50

            self.update_score_display()
            self.current_round += 1

            game_over = False
            winner = None
            for i, score in enumerate(self.scores):
                if score > 100:
                    game_over = True
                    min_score = min(
                        [s for s in self.scores if s <= 100], default=min(self.scores)
                    )
                    winners = [j for j, s in enumerate(self.scores) if s == min_score]
                    if len(winners) == 1:
                        winner = self.players[winners[0]]
                    else:
                        winner = "、".join([self.players[j] for j in winners])
                    break

            if game_over:
                result = f"游戏结束!\n\n"
                for i, player in enumerate(self.players):
                    result += f"{player}: {self.scores[i]}分\n"
                result += f"\n获胜者: {winner}"
                messagebox.showinfo("游戏结束", result)
                self.game_frame.pack_forget()
                self.setup_frame.pack()
                self.current_round = 1
            else:
                for inp in self.round_inputs:
                    inp["total"].delete(0, tk.END)
                    inp["cabo"].set(False)
                    inp["shenfeng"].set(False)

                for label in self.game_frame.winfo_children():
                    if isinstance(label, tk.Label) and "第" in label.cget("text"):
                        label.config(text=f"第 {self.current_round} 轮")
                        break

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def update_score_display(self):
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                widget.destroy()

        tk.Label(
            self.game_frame,
            text=f"第 {self.current_round} 轮",
            font=("Arial", 18, "bold"),
        ).pack(pady=10)

        self.round_inputs = []
        for i, player in enumerate(self.players):
            player_frame = tk.LabelFrame(
                self.game_frame,
                text=f"{player} (当前: {self.scores[i]}分)",
                font=("Arial", 12),
                padx=10,
                pady=10,
            )
            player_frame.pack(fill=tk.X, pady=5)

            tk.Label(player_frame, text="卡牌总和:", font=("Arial", 10)).grid(
                row=0, column=0, sticky=tk.W
            )
            total_entry = tk.Entry(player_frame, font=("Arial", 10), width=8)
            total_entry.grid(row=0, column=1, padx=5)

            cabo_var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                player_frame, text="呼唤CABO", variable=cabo_var, font=("Arial", 10)
            ).grid(row=1, column=0, columnspan=2, sticky=tk.W)

            special_frame = tk.Frame(player_frame)
            special_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)

            shenfeng_var = tk.BooleanVar(value=False)
            tk.Checkbutton(
                special_frame,
                text="神锋特工队(12,12,13,13)",
                variable=shenfeng_var,
                font=("Arial", 9),
            ).pack(side=tk.LEFT)

            self.round_inputs.append(
                {"total": total_entry, "cabo": cabo_var, "shenfeng": shenfeng_var}
            )

        btn_frame = tk.Frame(self.game_frame)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="确定",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            command=self.submit_round,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="显示总分",
            font=("Arial", 12),
            bg="#FF9800",
            fg="white",
            command=self.show_scores,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="新游戏",
            font=("Arial", 12),
            bg="#9E9E9E",
            fg="white",
            command=self.new_game,
        ).pack(side=tk.LEFT, padx=5)

    def show_scores(self):
        result = "当前总分:\n\n"
        for i, player in enumerate(self.players):
            status = ""
            if self.scores[i] == 50:
                status = " (已触发凑满分)"
            elif self.scores[i] > 100:
                status = " (已淘汰)"
            result += f"{player}: {self.scores[i]}分{status}\n"

        min_score = min([s for s in self.scores if s <= 100], default=min(self.scores))
        leaders = [self.players[i] for i, s in enumerate(self.scores) if s == min_score]
        result += f"\n领先者: {', '.join(leaders)}"

        messagebox.showinfo("当前分数", result)

    def new_game(self):
        if messagebox.askyesno("确认", "确定要开始新游戏吗？"):
            self.scores = [0] * len(self.players)
            self.current_round = 1
            self.game_frame.pack_forget()
            self.setup_frame.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = CaboScoreTracker(root)
    root.mainloop()
