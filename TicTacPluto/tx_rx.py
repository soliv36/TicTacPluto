import adi
import numpy as np
import tx_rx
import matplotlib.pyplot as plt

"""
TX FUNCTIONS
"""
#configures the Pluto SDR to receive samples
def config_rx(sdr, sample_rate, center_freq, num_samples, gain_control_mode_chan0, rx_hardwaregain_chan0):
    sdr.rx_lo = int(center_freq)
    sdr.rx_rf_bandwidth = int(sample_rate)
    sdr.rx_buffer_size = num_samples
    sdr.gain_control_mode_chan0 = gain_control_mode_chan0
    sdr.rx_hardwaregain_chan0 = int(rx_hardwaregain_chan0)

#configures the Pluto SDR to transmit
def config_tx(sdr, sample_rate, center_freq, tx_hardwaregain_chan0):
    sdr.tx_rf_bandwidth = int(sample_rate)
    sdr.tx_lo = int(center_freq)
    sdr.tx_hardwaregain_chan0 = int(tx_hardwaregain_chan0)
    sdr.tx_cyclic_buffer = True

#converts a string to ascii binary
def str_to_binary(text):
    index = 0
    strings = []
    while index < len(text):
        strings.append(text[index])
        index = index + 1

    #convert to ascii binary
    strings = [bin(ord(char))[2:].zfill(8) for char in strings]

    #convert the list to indivdual bits
    bits = []

    for string in strings:
        for bit in string:
            bits.append(int(bit))

    return bits

#adds start and stop bits to the data
def frame_bits(bits):
    start_bits = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    stop_bits = [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
    framed_bits = np.concatenate((start_bits, bits, stop_bits))
    return framed_bits

#converts binary data to IQ samples
def bits_to_samples(bits):
    x_bits = np.array(bits)
    x_degrees = x_bits* -180 + 180
    x_radians = x_degrees*np.pi/180
    x_symbols = np.cos(x_radians) + 0.0j*np.sin(x_radians) #create complex samples
    samples = np.repeat(x_symbols, 24)
    samples *= 2**14

    return samples

#converts text to BPSK complex samples, returns a list
def text_to_bpsk_samps(text):
    bits = str_to_binary(text)
    bits = frame_bits(bits)
    samples = bits_to_samples(bits)
    return samples

def tx_stop(sdr, tx_samples):
    sdr.tx_cyclic_buffer = False #disable the cyclic buffer to transmit a finite number of samples
    for i in range(0, 500):
        sdr.tx(tx_samples)

def tx_samples(sdr, samples):
    sdr.tx_destroy_buffer() #clear the tx buffer
    sdr.tx_cyclic_buffer = True #transmit the samples on repeat
    sdr.tx(samples)

"""
RX
"""
#correct the samples to be either 0 or 1
def correct_samples(samples):
    index = 0
    corrected_samples = []

    for sample in samples:
        if sample >= 1:
            corrected_samples.append(1)
        else:
            corrected_samples.append(0)
    
    return corrected_samples

#find the index of the start or stop bits in the corrected samples
def find_index(samples, start_index, is_start):
    #start_bits = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    #stop_bits = [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
    error_tolerance = 3
    index = start_index
    count = 0
    num_8_bit_seqs = 0
    num_3_bit_seqs = 0
    count_total = 0

    while index != len(samples):
        if samples[index] == 1:
            while samples[index] == 1:
                index += 1
                count += 1

                if index == len(samples):
                    return -1

            if 24*8-error_tolerance <= count <= 24*8 + error_tolerance:
                num_8_bit_seqs += 1
                count_total += count
                if num_8_bit_seqs == 2 and num_3_bit_seqs == 1:
                    if is_start == True:
                        return index
                    else:
                        return index - (count_total-24)
            elif (24*3-error_tolerance <= count <= 24*3) + (error_tolerance and num_8_bit_seqs == 1):
                num_3_bit_seqs = 1
                count_total += count
            else:
                num_8_bit_seqs = 0
                num_3_bit_seqs = 0
                count_total = 0
            count = 0
        else:
            while samples[index] == 0 and index != len(samples):
                index += 1
                count += 1

                if index == len(samples):
                    return -1

            if 24*8-error_tolerance <= count <= 24*8 + error_tolerance:
                num_8_bit_seqs += 1
                count_total += count
                if num_8_bit_seqs == 2 and num_3_bit_seqs == 1:
                    if is_start == True:
                        return index
                    else:
                        return index - (count_total-24)
            elif (24*3-error_tolerance <= count <= 24*3) + (error_tolerance and num_8_bit_seqs == 1):
                num_3_bit_seqs = 1
                count_total += count
            else:
                num_8_bit_seqs = 0
                num_3_bit_seqs = 0
                count_total = 0
            count = 0
    return -1

def detect_phase(samples):
    if samples[0] == 1:
        temp = []
        for bit in samples:
            if bit == 1:
                temp.append(0)
            else: 
                temp.append(1)

        return temp
    else:
        return samples

#convert corrected samples to bits taking into account that they may not always be 24 samples per bit       
def samples_to_bits(samples, start_index, end_index, samps_per_symbol):
    count = 0
    index = 0
    count_append = 0
    samples = samples[start_index:end_index+1]
    temp = []

    while index <= len(samples):
        count_append = 0
        count = 0
        if samples[index] == 1:
            while samples[index] == 1 and index <= len(samples):
                count += 1
                index += 1

                if index == len(samples):
                    return temp
            
            count_append = round(count/samps_per_symbol)
            for i in range(0, count_append):
                temp.append(1)
        else:
            while samples[index] == 0 and index <= len(samples):
                count += 1
                index += 1

                if index == len(samples):
                    return temp
            
            count_append = round(count/samps_per_symbol)
            for i in range(0, count_append):
                temp.append(0)

    return temp

#convert ascii binary to text
def ascii_to_text(bits):
    remainder = len(bits) % 8

    for i in range(0, remainder):
        bits.pop()

    letters =  [bits[i:i+8] for i in range(0, len(bits), 8)]
    text = []

    for letter in letters:
        temp = ''.join(str(bit) for bit in letter)
        temp = int(temp, 2)
        temp = chr(temp)
        text.append(temp)

    return text

# Checks if the text received contains valid characters (alpha-numeric only)
def is_valid_text(text):
    for i in text:
        ascii_value = ord(i)
        if not (48 <= ascii_value <= 57 or 65 <= ascii_value <= 90 or 97 <= ascii_value <= 122):
            return False
    return True

def rx_text(sdr):
    valid_text = []
    received = False
    while received == False:
        samples = sdr.rx()
        samples = tx_rx.correct_samples(samples)
        start_index = tx_rx.find_index(samples[0:1000], 0, True)

        if start_index > 0:
            end_index = tx_rx.find_index(samples, start_index, False)

            if end_index != -1:
                bits = tx_rx.samples_to_bits(samples, start_index, end_index, 24) 
                text = tx_rx.ascii_to_text(bits)

                if tx_rx.is_valid_text(text) and text != []:
                    valid_text.append(text)
                    if (all(i == valid_text[0] for i in valid_text) == True) and len(valid_text) == 3:
                        print('Received Message:', ''.join(text)) #print received message
                        valid_text = ''.join(valid_text[0])
                        return valid_text
                    elif (all(i == valid_text[0] for i in valid_text) == False) and len(valid_text) == 3:
                        valid_text = []
                    else:
                        continue