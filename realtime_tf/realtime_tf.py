import time
from pylsl import StreamInlet, resolve_byprop
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import argparse
import sys

from .time_frequency import time_frequency, get_cmwX
from .constants import srate, channel_labels


class MuseLsl():
    def __init__(self):
        self.inlet = None
        self.retry_attempts = 5
        self.retry_delay = 2  # seconds

    # create a figure
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        plt.ion()
        self.fig.show()
        self.fig.canvas.draw()

    def connect(self):
        for i in range(self.retry_attempts):
            try:
                streams = resolve_byprop('type', 'EEG', timeout=2)
                if len(streams) > 0:
                    self.inlet = StreamInlet(streams[0])
                    print('Successfully connected to EEG stream.')
                    return
                else:
                    print(f'Attempt {i+1} failed. Could not find EEG stream. Retrying in {self.retry_delay} seconds.')
                    time.sleep(self.retry_delay)
            except Exception as e:
                print(f'Attempt {i+1} failed with error: {e}. Retrying in {self.retry_delay} seconds.')
                time.sleep(self.retry_delay)
        
        raise RuntimeError('Failed to connect to EEG stream after multiple attempts.')

    def disconnect(self):
        if self.inlet is not None:
            self.inlet.close_stream()
            print('Disconnected from EEG stream.')

    def read_and_plot_data(self, show_time_window, update_time_window, channel):
        if self.inlet is None:
            raise RuntimeError('Must be connected to EEG stream to read data.')
        
        try:
            nData = round(srate*show_time_window)
            temp_data = deque([[0,0,0,0,0] for _ in range(nData)], maxlen=nData)
            counter = 0
            loops = 0  # to keep track of the number of loops total for the times array


            cmwX, nKern, frex = get_cmwX(nData)
            while True:
               
                sample, _ = self.inlet.pull_sample()
                
                if counter < update_time_window * srate:
                    temp_data.popleft()
                    temp_data.append(sample)
                    counter += 1
                else:
                    
                    data = np.array(temp_data)[:,:len(channel_labels)].T
                    self.plot_data(data, cmwX, nKern, frex, show_time_window, channel, loops )
                    
                    counter = 0
                    loops += update_time_window

        except KeyboardInterrupt:
            print('Stopping data collection.')
        finally:
            self.disconnect()

    def _filter_channel(self, tf , channel):
        '''
            tf must be of shape channels x time

            returns tf array and title
        '''
        if channel != 'avg':
            assert int(channel) < len(channel_labels), f'Channel numbers range from 0 to {len(channel_labels)}. Please input a valid number'
        
        match channel:            
            case 'avg':
                return np.mean(tf, axis=0), 'Average Power Spectrum over all channels'
            case _ :
                return tf[int(channel), :], f'Power Spectrum across channel {channel_labels[int(channel)]}'
            
    def plot_data(self, new_data, cmwX, nKern, frex, show_time_window,channel, loops=0):
        times = np.linspace(loops, show_time_window+loops, new_data.shape[1]) 

        # Perform the time-frequency analysis on new_data
        tf_data = time_frequency(new_data, cmwX, nKern)

        tf_data, title = self._filter_channel(tf_data, channel)

        
        # Clear the current plot
        self.ax.clear()
        
        # Update the plot with the new time-frequency representation
        self.ax.contourf(times, frex, tf_data, 40, cmap='jet') 
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Frequencies (Hz)')
        self.ax.set_title(title)
        
        # Redraw the figure
        self.fig.canvas.draw()
        plt.pause(0.01)  # pause a bit so that plots are updated


def main():
    parser = argparse.ArgumentParser(description="Generate time-frequency plot of real-time EEG data.")
    parser.add_argument("--show_time_window", type=float, default=2,
                        help="The total time window for which to calculate the time-frequency plot.")
    parser.add_argument("--update_time_window", type=float, default=0.2,
                        help="The time window to update at each frame to the new data and calculate time frequency.")
    parser.add_argument("--channel", type=str, default='avg',
                        help="The channel for which to plot the time-frequency plot. Plots the average across all channels by default.")
    args = parser.parse_args()

    run_muse(args.show_time_window, args.update_time_window, args.channel)


def run_muse(show_time_window, update_time_window, channel):
    muse_lsl = MuseLsl()
    try:
        muse_lsl.connect()
        muse_lsl.read_and_plot_data(show_time_window, update_time_window, channel)
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        muse_lsl.disconnect()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'An error occurred: {e}', file=sys.stderr)
