import scipy.io
from scipy import stats
from scipy.signal import find_peaks
import numpy as np
import time

#used when the input source is shifting
#takes in the input matlab file and writes over the current matlab file
#file size increases, needs to be worked on
def transform(inputFile):
  mat = scipy.io.loadmat(inputFile)
  amp = mat['C'].transpose().flatten()
  tInterval = mat['Tinterval'][0]
  time = np.arange(np.shape(amp)[0])*tInterval

  def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

  windowSize = 4500

  s = moving_average(amp, windowSize)

  for i, e in enumerate(s):
    if e == float('inf'):
      s[i] = s[i-1]

  amp = np.subtract(amp[windowSize//2:windowSize//2+len(s)], s)
  time = time[windowSize//2:windowSize//2+len(s)]
  m = {}
  m['C'] = amp.transpose()
  m['Tinterval'] = [tInterval]

  print(m['C'].transpose().flatten())

  scipy.io.savemat(inputFile, m)