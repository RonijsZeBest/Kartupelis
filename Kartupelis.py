import tkinter as tk 
import random
from PIL import Image, ImageTk


class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Battleship Game")

        self.grid_size = 10
        self.player_board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.computer_board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.ships_to_place = {5: 1, 3: 2, 2: 3}
        self.current_ship_size = None
        self.orientation = "vertical"
        self.all_ships_placed = False
        self.game_started = False
        
        # This will store the (row, col) cells currently previewed.
        self.last_preview = []

        player_wins = 0
        computer_wins = 0

        self.create_ui()
        self.place_ships_evenly(self.computer_board)

        
    def load_ship_images(self):
        self.ship_images = {
            5: ImageTk.PhotoImage(Image.open("ShipBattleshipHull.png").resize((100, 40))),
            3: ImageTk.PhotoImage(Image.open("ShipCruiserHull.png").resize((60, 40))),
            2: ImageTk.PhotoImage(Image.open("ShipPatrolHull.png").resize((40, 40)))
        }

    
    def create_ui(self):
        # Top info label
        self.info_label = tk.Label(self.root, text="Choose a ship size and place it.", font=("Arial", 16))
        self.info_label.pack(pady=10)
        
        # Top right control frame for Retry and Exit buttons.
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.TOP, anchor="ne", padx=10, pady=10)
        self.retry_button = tk.Button(self.control_frame, text="Retry", command=self.restart_game)
        self.retry_button.pack(side=tk.LEFT, padx=5)
        self.exit_button = tk.Button(self.control_frame, text="Exit Game", command=self.root.destroy)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # Main game frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        #Spēlētāja laukums
        self.player_frame = tk.Frame(self.main_frame)
        self.player_frame.grid(row=0, column=0, padx=20)
        tk.Label(self.main_frame, text="Your Board", font=("Arial", 14)).grid(row=1, column=0)
        self.player_buttons = []
        self.create_board_with_labels(self.player_frame, self.player_buttons, self.place_ship)

        self.computer_frame = tk.Frame(self.main_frame)
        self.computer_frame.grid(row=0, column=1, padx=20)
        tk.Label(self.main_frame, text="Enemy Board", font=("Arial", 14)).grid(row=1, column=1)
        self.computer_buttons = []
        self.create_board_with_labels(self.computer_frame, self.computer_buttons, self.shoot)

        self.ship_palette = tk.Frame(self.root)
        self.ship_palette.pack(pady=10)
        self.create_ship_palette()

        self.orientation_button = tk.Button(self.root, text="Toggle Orientation", command=self.toggle_orientation)
        self.orientation_button.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game, state="disabled", bg="lightgreen", fg="black",font=("Arial", 16, "bold"), width=15, height=2)
        self.start_button.pack(side=tk.RIGHT, padx=20, pady=10)

    def create_board_with_labels(self, container, button_list, command):
        
        board_frame = tk.Frame(container)
        board_frame.pack()

        corner = tk.Label(board_frame, text="", font=("Arial", 12))
        corner.grid(row=0, column=0, padx=2, pady=2)

        letters = "KARTUPELIS"
        for col in range(self.grid_size):
            lbl = tk.Label(board_frame, text=letters[col], font=("Arial", 12))
            lbl.grid(row=0, column=col+1, padx=2, pady=2)

        for row in range(self.grid_size):
            lbl = tk.Label(board_frame, text=str(row+1), font=("Arial", 12))
            lbl.grid(row=row+1, column=0, padx=2, pady=2)
            row_buttons = []
            for col in range(self.grid_size):
                btn = tk.Button(board_frame, width=8, height=4, bg="lightblue", relief="ridge",
                                command=lambda r=row, c=col: command(r, c))
                btn.grid(row=row+1, column=col+1, padx=2, pady=2)
                row_buttons.append(btn)
                if command == self.place_ship:
                    btn.bind("<Enter>", lambda event, r=row, c=col: self.preview_ship(event, r, c))
                    btn.bind("<Leave>", lambda event: self.clear_preview())
            button_list.append(row_buttons)

    def create_ship_palette(self):
        for size, count in self.ships_to_place.items():
            btn = tk.Button(self.ship_palette, text=f"Size {size} ({count})", command=lambda s=size: self.select_ship(s))
            btn.pack(side=tk.LEFT, padx=5)

    def select_ship(self, size):
        if self.ships_to_place[size] > 0:
            self.current_ship_size = size
            self.info_label.config(text=f"Selected ship size {size}. Place it on the board.")
        else:
            self.info_label.config(text=f"No ships of size {size} remaining.")

    def toggle_orientation(self):
        self.orientation = "horizontal" if self.orientation == "vertical" else "vertical"
        self.info_label.config(text=f"Orientation: {self.orientation.capitalize()}.")

    def preview_ship(self, event, row, col):
        self.clear_preview()
        if self.current_ship_size is None:
            return

        size = self.current_ship_size
        if not self.can_place_ship(row, col, size):
            return

        preview_cells = []
        for i in range(size):
            if self.orientation == "vertical":
                r, c = row + i, col
            else:
                r, c = row, col + i
            if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                preview_cells.append((r, c))
                self.player_buttons[r][c].config(bg="light green")
        self.last_preview = preview_cells

    def clear_preview(self):
        for (r, c) in self.last_preview:
            if self.player_board[r][c] == 0:
                self.player_buttons[r][c].config(bg="lightblue")
        self.last_preview = []

    def place_ship(self, row, col):
        self.clear_preview()

        if not self.current_ship_size:
            self.info_label.config(text="Select a ship size first.")
            return

        size = self.current_ship_size
        if self.can_place_ship(row, col, size):
            for i in range(size):
                r, c = (row + i, col) if self.orientation == "vertical" else (row, col + i)
                self.player_board[r][c] = 1
                self.player_buttons[r][c].config(bg="green")

            self.ships_to_place[size] -= 1
            self.current_ship_size = None
            self.info_label.config(text="Ship placed. Select another ship or start the game.")
            self.update_ship_palette()

            if all(count == 0 for count in self.ships_to_place.values()):
                self.all_ships_placed = True
                self.start_button.config(state="normal")
                self.info_label.config(text="All ships placed. Press 'Start Game' to begin!")
        else:
            self.info_label.config(text="Cannot place ship here!")

    def can_place_ship(self, row, col, size):
    
        if self.orientation == "vertical":
            if row + size > self.grid_size:
                return False
        else:
            if col + size > self.grid_size:
                return False

        for i in range(size):
            r, c = (row + i, col) if self.orientation == "vertical" else (row, col + i)

            if self.player_board[r][c] != 0:
                return False

            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                        if self.player_board[nr][nc] == 1:
                            return False

        return True

    def update_ship_palette(self):
        for widget in self.ship_palette.winfo_children():
            widget.destroy()
        self.create_ship_palette()

    def place_ships_evenly(self, board):
        ship_sizes = [5, 3, 3, 2, 2, 2]
        sections = [(0, 0, 5, 5), (0, 5, 5, 10), (5, 0, 10, 5), (5, 5, 10, 10)]
        random.shuffle(sections)

        for size in ship_sizes:
            placed = False
            while not placed:
                sec_x1, sec_y1, sec_x2, sec_y2 = random.choice(sections)
                orientation = random.choice(["vertical", "horizontal"])
                
                row = random.randint(sec_x1, sec_x2 - 1)
                col = random.randint(sec_y1, sec_y2 - 1)

                if self.can_place_ship_ai(board, row, col, size, orientation):
                    for i in range(size):
                        r, c = (row + i, col) if orientation == "vertical" else (row, col + i)
                        board[r][c] = 1
                    placed = True

    def can_place_ship_ai(self, board, row, col, size, orientation):
        if orientation == "vertical":
            if row + size > self.grid_size:
                return False
            for i in range(size):
                if not self.is_valid_ai_position(board, row + i, col):
                    return False
        else:
            if col + size > self.grid_size:
                return False
            for i in range(size):
                if not self.is_valid_ai_position(board, row, col + i):
                    return False
        return True

    def is_valid_ai_position(self, board, row, col):
        if board[row][col] != 0:
            return False
        
        for r in range(max(0, row - 1), min(self.grid_size, row + 2)):
            for c in range(max(0, col - 1), min(self.grid_size, col + 2)):
                if board[r][c] == 1:
                    return False
        return True               

    def start_game(self):
        if not self.all_ships_placed:
            self.info_label.config(text="Place all your ships first!")
            return
        self.game_started = True
        self.info_label.config(text="Game started! Shoot the enemy board.")

    def shoot(self, row, col):
        if not self.game_started:
            self.info_label.config(text="Press 'Start Game' before shooting!")
            return

        button = self.computer_buttons[row][col]
        if self.computer_board[row][col] == 1:
            button.config(bg="red", text="X", state="disabled")
        else:
            button.config(bg="gray", state="disabled")
        self.computer_board[row][col] = -1
        
        self.check_game_over()
        if self.game_started:
            self.bot_turn()

    def bot_turn(self):
        while True:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            if self.player_board[row][col] in [0, 1]:
                if self.player_board[row][col] == 1:
                    self.player_buttons[row][col].config(bg="red")
                else:
                    self.player_buttons[row][col].config(bg="gray")
                self.player_board[row][col] = -1
                break
        self.check_game_over()


    def show_end_screen(self, message):
    # Create a fullscreen top-level window for the end screen
        end_screen = tk.Toplevel(self.root)
        end_screen.attributes("-fullscreen", True)
        end_screen.configure(bg="black")

    # Title Message (Win/Lose)
        title = tk.Label(end_screen, text=message, font=("Arial", 48, "bold"), fg="white", bg="black")
        title.pack(pady=50)

    # Display the total wins
        win_message = f"Player Wins: {self.player_wins}   |   Computer Wins: {self.computer_wins}"
        win_label = tk.Label(end_screen, text=win_message, font=("Arial", 24), fg="white", bg="black")
        win_label.pack(pady=20)

    # Button Frame
        button_frame = tk.Frame(end_screen, bg="black")
        button_frame.pack(pady=50)

    # Play Again Button
        play_again_button = tk.Button(button_frame, text="Play Again", font=("Arial", 20),
            command=lambda: [end_screen.destroy(), self.restart_game()],
            bg="green", fg="white", width=15, height=2)
        play_again_button.pack(side=tk.LEFT, padx=20)

    # Exit Button
        exit_button = tk.Button(button_frame, text="Exit Game", font=("Arial", 20),
            command=self.root.destroy, bg="red", fg="white", width=15, height=2)
        exit_button.pack(side=tk.LEFT, padx=20)


    def check_game_over(self):
        enemy_ships_remaining = any(cell == 1 for row in self.computer_board for cell in row)
        player_ships_remaining = any(cell == 1 for row in self.player_board for cell in row)

        if not enemy_ships_remaining:
            BattleshipGame.player_wins += 1  # ✅ Use class attribute instead
            self.game_started = False
            self.show_end_screen("YOU WIN!")
        elif not player_ships_remaining:
            BattleshipGame.computer_wins += 1  # ✅ Use class attribute instead
            self.game_started = False
            self.show_end_screen("YOU LOSE!")




    def restart_game(self):
        self.root.destroy()
        new_root = tk.Tk()
        new_root.attributes("-fullscreen", True)
        BattleshipGame(new_root)
        new_root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    game = BattleshipGame(root)
    root.mainloop()
