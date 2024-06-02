import os
from colorama import Fore, Style

class Player:
    def __init__(self, player_number, player_symbol, is_turn):
        self.player_number = player_number
        self.is_turn = is_turn
        self.player_symbol = player_symbol

class Game:
    def __init__(self):
        self.game_board = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]
        self.current_player = 1
        self.current_move = ''
        self.total_num_moves = 1
        self.player_symbols = ['X', 'O']

    def get_current_player(self, Player):
        if self.total_num_moves % 2 == 0:
            self.current_player = 1
            if Player.player_number == 1:
                Player.is_turn = True
            else:
                Player.is_turn = False
        else:
            self.current_player = 2
            if Player.player_number == 2:
                Player.is_turn = True
            else:
                Player.is_turn = False

    #Gets the user's move to be placed on the game board. Stores the play in the Game class. 
    def get_move(self):
        valid_moves = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        #print the game board key
        print(f'{Fore.CYAN}A1{Style.RESET_ALL} | {Fore.CYAN}A2{Style.RESET_ALL} | {Fore.CYAN}A3{Style.RESET_ALL} ')
        print('--------------')
        print(f'{Fore.CYAN}B1{Style.RESET_ALL} | {Fore.CYAN}B2{Style.RESET_ALL} | {Fore.CYAN}B3{Style.RESET_ALL} ')
        print(f'--------------')
        print(f'{Fore.CYAN}C1{Style.RESET_ALL} | {Fore.CYAN}C2{Style.RESET_ALL} | {Fore.CYAN}C3{Style.RESET_ALL} ')

        current_move = input('Enter your next move: ')
        if (current_move in valid_moves) and current_move not in self.game_board:
            self.current_move = current_move
            os.system('clear')
        else:
            while current_move:
                print('Invalid Input: enter a valid move')
                current_move = input('Enter your next move: ')

    #Adds the player's symbol to the respective space on the game board. Uses the last played move stored in the Game class.
    def play_move(self, player_symbol):
        game_board_indicies = {
            'A1': (0, 0),
            'A2': (0, 1),
            'A3': (0, 2),
            'B1': (1, 0),
            'B2': (1, 1),
            'B3': (1, 2),
            'C1': (2, 0),
            'C2': (2, 1),
            'C3': (2, 2),
        }
        
        if self.current_move in game_board_indicies:
            row, col = game_board_indicies[self.current_move]
            self.game_board[row][col] = player_symbol
        else:
            print("Invalid move")


    def check_winner(self):
        # Check rows, columns, and diagonals for 3 of the player's symbols in a row
        for symbol in self.player_symbols:
            for row in self.game_board:
                if all(cell == symbol for cell in row):
                    return True

            for col in range(3):
                if all(self.game_board[row][col] == symbol for row in range(3)):
                    return True

            if all(self.game_board[i][i] == symbol for i in range(3)):
                return True

            if all(self.game_board[i][2 - i] == symbol for i in range(3)):
                return True

        return False

    def check_draw(self):
        # Check if all spaces on the game board are filled
        for row in self.game_board:
            if ' ' in row:
                return False
        
        return True

    def display(self):
        os.system('clear')  # Clear the console
        print('\n\n')
        
        # Print each row with formatted f-strings
        print(f'    {Fore.CYAN}{self.game_board[0][0]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[0][1]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[0][2]:^3}{Style.RESET_ALL} ')
        print('    --------------')
        print(f'    {Fore.CYAN}{self.game_board[1][0]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[1][1]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[1][2]:^3}{Style.RESET_ALL} ')
        print('    --------------')
        print(f'    {Fore.CYAN}{self.game_board[2][0]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[2][1]:^3}{Style.RESET_ALL} | {Fore.CYAN}{self.game_board[2][2]:^3}{Style.RESET_ALL} ')

    def increment_total_moves(self):
        self.total_num_moves += 1