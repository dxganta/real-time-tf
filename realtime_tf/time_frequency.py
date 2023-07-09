import numpy as np
from scipy.fft import fft, ifft
from .constants import srate

def time_frequency(data, cmwX, nKern, channel_labels=None):
    '''
        creates a time frequency power plot of the data and plots it for
        every channel
        
        data -> of shape channels x time
        times -> the times array for the given data
        freqrange -> extract only these frequencies (in Hz)
        numfrex -> number of frequencies between lowest and highest

        returns average time frequency plot and frequency range
    '''
    assert data.shape[0] < data.shape[1], "data shape incorrect"
    assert channel_labels is None or len(channel_labels) == data.shape[0], "channel_labels must be of same length as number of channels"

    # set up convolution parameters
    nData   = data.shape[1]
    nConv   = nData + nKern - 1
    halfwav = (nKern-1)//2

    # initialize time-frequency output matrix
    tf = np.zeros((data.shape[0], cmwX.shape[0], data.shape[1])) # channels X frequency X times

    # loop over channels
    for chani in range(data.shape[0]):

        # compute Fourier coefficients of EEG data 
        eegX = fft(data[chani, :] , nConv)

        # perform convolution and extract power (vectorized across frequencies)
        as_ = ifft(cmwX * eegX[None, :], axis=1)
        as_ = as_[:, halfwav: -halfwav]
        tf[chani, :, :] = np.abs(as_) ** 2
        
    tf = np.mean(tf, axis=0)

    return tf


def get_cmwX(nData, freqrange=[1,40], numfrex=42):
    '''
        returns cmwX of shape frequency x nConv
    '''
    pi = np.pi
    wavtime = np.arange(-2,2-1/srate,1/srate)
    nKern = len(wavtime)
    nConv = nData + nKern - 1
    frex = np.linspace(freqrange[0],freqrange[1],numfrex)
   # create complex morlet wavelets array
    cmwX = np.zeros((numfrex, nConv), dtype=complex)

    # number of cycles
    numcyc = np.linspace(3,15,numfrex);
    for fi in range(numfrex):
        # create time-domain wavelet
        s = numcyc[fi] / (2*pi*frex[fi])
        twoSsquared = (2*s) ** 2
        cmw = np.exp(2*1j*pi*frex[fi]*wavtime) * np.exp( (-wavtime**2) / twoSsquared )


        # compute fourier coefficients of wavelet and normalize
        cmwX[fi, :] = fft(cmw, nConv)
        cmwX[fi, :] = cmwX[fi, :] / max(cmwX[fi, :])

    return cmwX, nKern, frex