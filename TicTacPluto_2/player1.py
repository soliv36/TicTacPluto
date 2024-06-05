import adi
import numpy as np
import tx_rx
from game import Player, Game
import threading
import logging
from colorama import Fore, Style

#initialize logging
logging.basicConfig(level=logging.INFO)

#SDR setup
sample_rate = 1e6
rx_center_freq = 915e6
tx_center_freq = 900e6
rx_buff_size = 4096

sdr = adi.Pluto('ip:192.168.2.1')
tx_rx.config_rx(sdr, sample_rate, rx_center_freq, rx_buff_size, 'manual', 70.0)
tx_rx.config_tx(sdr, sample_rate, tx_center_freq, -40)
 
#game setup
player = Player(1, 'X', True)
game_board = Game()
is_end = False

try:
    while is_end == False:
        if player.is_turn == True:
            game_board.get_current_player(player)
            game_board.get_move()
            game_board.play_move(player.player_symbol)
            game_board.display()
            game_board.increment_total_moves()

            if game_board.check_winner() == True:
                game_board.current_move = 'WIN'
                print(f'{Fore.RED}You have won the game!{Style.RESET_ALL}')
                is_end = True

            if game_board.check_draw() == True:
                game_board.current_move = 'DRAW'
                print(f'{Fore.RED}The game has ended in a draw.{Style.RESET_ALL}')
                is_end = True

            #transmit the move to the other player, wait for the stop message to stop transmitting
            tx_samples = tx_rx.text_to_bpsk_samps(game_board.current_move)
            tx_thread = threading.Thread(target=tx_rx.tx_samples, args=(sdr, tx_samples))
            
            rx_thread = threading.Thread(target=tx_rx.rx_text, args=(sdr, game_board))
            rx_thread.start()
            tx_thread.start()

            rx_thread.join()
            tx_thread.join()
            logging.info('---Move received---')

        else:
            logging.info('Waiting for other player\'s move...')
            
            #receive the other player's move
            text = tx_rx.rx_text(sdr)
            game_board.current_move = text

            #transmit the stop bits, stop transmitting when the other user has received the stop bits
            tx_samples = tx_rx.text_to_bpsk_samps('STOP')

            tx_thread = threading.Thread(target=tx_rx.tx_samples, args=(sdr, tx_samples))
            rx_thread = threading.Thread(target=tx_rx.rx_text(sdr, game_board))

            rx_thread.start()
            tx_thread.start()

            rx_thread.join()
            tx_thread.join()
            
            if text == 'WIN':
                print(f'{Fore.LIGHTRED_EX}You Lose! Player #2 has won the game!{Style.RESET_ALL}')
                is_end = True
            elif text == 'DRAW':
                print(f'{Fore.LIGHTRED_EX}The game has ended in a draw!{Style.RESET_ALL}')
                is_end = True
            else:
                game_board.increment_total_moves()
                game_board.get_current_player(player)
                game_board.play_move('O')
                game_board.display()
        
                    
except KeyboardInterrupt:
    logging.info('Keyboard Interrupt: exiting')
    sdr.tx_destroy_buffer()
    sdr.rx_destroy_buffer()
finally:
    logging.info('Goodbye')
    exit(0)
                