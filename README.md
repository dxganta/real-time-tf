# Realtime Time-Frequency Visualization

Realtime Time Frequency Plotting of EEG data from Muse headset

https://github.com/dxganta/real-time-tf/assets/47485188/a0484f7d-1aea-43df-84ad-d772f191bb85

## Requirements

Compatible with Python 3.x

Compatible with all muse headsets supported by muselsl library

## Getting Started

First install [muselsl](https://github.com/alexandrebarachant/muse-lsl), connect to your muse headset and start a muse stream using <br>

```
muselsl stream
```

Then install the realtime_tf package using

```
pip install real-time-tf
```

Keep the muselsl stream running and in a separate terminal run

```
realtime_tf
```

to visualize the realtime time frequency plot of the streamed eeg data from your muse headset.

The time-frequency plot is shown of 1 second EEG data and the plot is updated every 0.2 seconds by default. But you can update these parameters if required using

```
realtime_tf --show_time_window NEW_VALUE --update_time_window NEW_VALUE
```

The muse headset generally has 4 EEG electrodes/channels ('TP9', 'AF7', 'AF8', 'TP10'). By default the time-frequency plot average across all 4 channels is shown. But you can output only the time-frequency plot for a specific channel using

```
realtime_tf --channel 0
```

This will output the tf plot for channel 0 which is 'TP9'.

## References

https://www.udemy.com/course/solved-challenges-ants/
