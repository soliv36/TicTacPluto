import adi
import numpy as np
import matplotlib.pyplot as plt
import tx_rx
from game import Player, Game
import threading
import logging


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
logging.info('Receive Started')

#game setup
player = Player(2, 'O', False)
game_board = Game()
is_end = False

try:
    while is_end == False:
        if player.is_turn == True:
            game_board.get_current_player(player)
            game_board.get_move()
            game_board.play_move('O')
            game_board.display()
            game_board.increment_total_moves()

            if game_board.check_winner == True:
                game_board.current_move = 'WIN'
                print('\033[0;92m You have won the game!')
                is_end = True

            if game_board.check_draw() == True:
                game_board.current_move = 'DRAW'
                print('\033[0;92m The game has ended in a draw.')
                is_end = True

            #transmit the move to the other player, wait for the stop message to stop transmitting
            tx_samples = tx_rx.text_to_bpsk_samps(game_board.current_move)
            tx_thread = threading.Thread(target=tx_rx.tx_samples, args=(sdr, tx_samples))
            
            rx_thread = threading.Thread(target=tx_rx.rx_text, args=(sdr,))
            rx_thread.start()
            tx_thread.start()

            rx_thread.join()
            tx_thread.join()
            logging.info('---Move received---')
        else:
            text = tx_rx.rx_text(sdr)
            if text == 'WIN':
                print('You Lose! Player #1 has won the game!')
                is_end = True
            elif text == 'DRAW':
                print('The game has ended in a draw!')
                is_end = True
            else:
                game_board.current_move = text
                game_board.increment_total_moves()
                game_board.get_current_player(player)
                game_board.play_move('X')
                game_board.display()
        
                    
except KeyboardInterrupt:
    logging.info('Keyboard Interrupt: destroying buffers, exiting')
    sdr.tx_destroy_buffer()
    sdr.rx_destroy_buffer()
finally:
    logging.info('Cleanup Done: exiting')
    exit(0)
                