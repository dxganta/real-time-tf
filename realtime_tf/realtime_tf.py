import time
from pylsl import StreamInlet, resolve_byprop
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import argparse
import sys

from .time_frequency import time_frequency, get_cmwX
from .constants import srate


class MuseLsl():
    def __init__(self):
        self.inlet = None
        self.retry_attempts = 5
        self.retry_delay = 2  # seconds

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

    def read_data(self, show_time_window, update_time_window):
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
                    
                    data = np.array(temp_data)[:,:4].T
                    process_new_data(data, cmwX, nKern, frex, show_time_window, loops)
                    
                    counter = 0
                    loops += update_time_window

        except KeyboardInterrupt:
            print('Stopping data collection.')
        finally:
            self.disconnect()


# create a figure
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()
fig.show()
fig.canvas.draw()

def process_new_data(new_data, cmwX, nKern, frex,show_time_window, loops=0):
    times = np.linspace(loops, show_time_window+loops, new_data.shape[1]) 

    # Perform the time-frequency analysis on new_data
    tf_data = time_frequency(new_data, cmwX, nKern)
    
    # Clear the current plot
    ax.clear()
    
    # Update the plot with the new time-frequency representation
    ax.contourf(times, frex, tf_data, 40, cmap='jet') 
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequencies (Hz)')
    ax.set_title('Real-Time Power Spectrum')
    
    # Redraw the figure
    fig.canvas.draw()
    plt.pause(0.01)  # pause a bit so that plots are updated


def main():
    parser = argparse.ArgumentParser(description="Generate time-frequency plot of real-time EEG data.")
    parser.add_argument("--show_time_window", type=float, default=2,
                        help="The total time window for which to calculate the time-frequency plot.")
    parser.add_argument("--update_time_window", type=float, default=0.2,
                        help="The time window to update at each frame to the new data and calculate time frequency.")
    args = parser.parse_args()

    run_muse(args.show_time_window, args.update_time_window)


def run_muse(show_time_window, update_time_window):
    muse_lsl = MuseLsl()
    try:
        muse_lsl.connect()
        muse_lsl.read_data(show_time_window, update_time_window)
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        muse_lsl.disconnect()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'An error occurred: {e}', file=sys.stderr)
