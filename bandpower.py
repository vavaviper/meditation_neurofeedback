import time
import brainflow
import numpy as np
import matplotlib.pyplot as plt
import keyboard
import pandas as pd
from playsound import playsound
import winsound
import random as rand

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations

def main():
    BoardShim.enable_dev_board_logger()
    
    winsound.PlaySound("meditation.mp3", winsound.SND_ASYNC | winsound.SND_ALIAS )

    #setting up brainflow params and board
    #comment out ganglion and uncomment synthetic board to do demo without a board
    #board_id = BoardIds.SYNTHETIC_BOARD.value

    params = BrainFlowInputParams ()
    params.board_id = 1
    board_id = 1
    params.serial_port = 'COM3'
    sampling_rate = BoardShim.get_sampling_rate (board_id)
    BoardShim.enable_dev_board_logger ()

    board = BoardShim (board_id, params)
    board.prepare_session ()

    board.start_stream()
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    time.sleep(5)
    nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
    data = board.get_board_data()
    

    eeg_channels = BoardShim.get_eeg_channels(board_id)
    # second eeg channel of synthetic board is a sine wave at 10Hz, should see huge alpha
    eeg_channel = eeg_channels[1]
    # optional detrend
    DataFilter.detrend(data[eeg_channel], DetrendOperations.LINEAR.value)
    psd = DataFilter.get_psd_welch(data[eeg_channel], nfft, nfft // 2, sampling_rate,
                                   WindowFunctions.BLACKMAN_HARRIS.value)
    
    #initializing variables needed for later
    button = True
    counter = 0
    counter_2 = 0

    while button == True:
        #get the amount of each wave by frequency
        gamma = DataFilter.get_band_power(psd, 30.0, 100.0)
        beta = DataFilter.get_band_power(psd, 12.0, 30.0)
        alpha = DataFilter.get_band_power(psd, 8.0, 12.0)
        theta = DataFilter.get_band_power(psd, 4.0, 8.0)
        delta = DataFilter.get_band_power(psd, 1.0, 4.0)

        band_dict = {gamma: 'concentration', beta: 'normal', alpha: 'light meditation', theta:'deep meditation', delta: 'sleep'}
        counter_2 += 1
        if counter_2 % 5 == 0:
            if max(band_dict) == beta or max(band_dict) == gamma:
                if rand.randint(0,2) % 2 == 0:
                    playsound('clear mind.m4a')
                if rand.randint() % 2 == 1:
                    playsound('relax.m4a') 
        if counter_2 % 20 == 0:
            if max(band_dict) == theta:
                playsound('keep going.m4a')

        if keyboard.is_pressed('space'):
            print('here are your results')
            break 
        print('hold spacebar if you want to stop')

        #making an axis for the graph
        bands = [gamma, beta, alpha, theta, delta]
        band_names = ['concentration', 'normal', 'light med.', 'deep med.', 'sleep']
                
        '''bar graph showing you the type of waves but its not needed

        fig = plt.bar(band_names, bands)
        #plt.xlabel("Type of Wave")
        #plt.ylabel("Frequency")
        #plt.title("Amount of Each State")
        #plt.show()
        #time.sleep(5)
        #plt.close('fig')
        '''
        #printing the amount in each state
        print('concentration', gamma)
        print('normal: ', alpha)
        print('light meditation: ', beta)
        print('deep meditation: ', theta)
        print('sleep', delta)

        #setting a timer
        counter += 5 

        #timer for how many seconds are in each state
        c_gamma = 0
        c_alpha = 0
        c_beta = 0
        c_theta = 0
        c_delta = 0

        #adding seconds to the timer
        if max(bands) == gamma:
            c_gamma += 5
            counter += 5
        elif max(bands) == alpha:
            c_alpha += 5
            counter += 5
        elif max(bands) == beta:
            c_beta += 5
            counter += 5
        elif max(bands) == theta:
            c_theta += 5
            counter += 5
        elif max(bands) == delta:
            c_delta += 1
            counter += 5

    #converting from seconds into minutes
    c_gamma /= 5
    c_alpha /= 5
    c_beta /= 5
    c_theta /= 5
    c_delta /= 5
    counter /= 5    

    #calculating the percent in each state
    percent_b = [c_gamma, c_alpha, c_beta, c_theta, c_delta]
    percent = []
    for i in percent_b:
        i /= counter
        i *= 10
        percent.append(i)
    print(percent)

    #final graph showing the percent in each state
    plt.bar(band_names, percent)
    plt.xlabel("Type of Wave")
    plt.ylabel("Minutes")
    plt.title("Amount of Each State")
    plt.show()
    time.sleep(5)
    plt.close('all')

    #printing how many minutes in each state
    print('concentration:', c_gamma, 'mins')
    print('normal: ', c_alpha, 'mins')
    print('light meditation: ', c_beta, 'mins')
    print('deep meditation: ', c_theta, 'mins')
    print('sleep:', c_delta, 'mins')

    board.stop_stream()
    board.release_session()
     

if __name__ == "__main__":
    main()
