import scipy.io
from scipy import stats
from scipy.signal import find_peaks
import numpy as np
import matplotlib as mpl
import heapq
mpl.use("TkAgg")
import matplotlib.pyplot as plt

'''
approx_threshold_deltat takes in data of Amplitude and time in the form of a 
numpy array and returns the approxmiated threshold, list of delta_t and 
first reference peak index. The input prevThreshold is used to avoid calculating
threshold for every single run. If there prevThreshold exists, the function
uses it instead of approximating the threshold.
'''

def approx_threshold_deltat(ampData, timeData, prevThreshold):
  def hist_okay(dt_list):
    if len(dt_list) == 0:
      return True
    else:
      hist, bin_edges = np.histogram(dt_list, bins=10, density = True)
      normalized = hist*np.diff(bin_edges)
      bool_normalized = normalized > 0.5
      if bool_normalized.any():
        return False
      else:
        return True

  curr_threshold = 0.00 if not prevThreshold else prevThreshold - 0.01
  dt_list = []
  j = 0

  # until histogram looks right (has a majority)
  while hist_okay(dt_list) and j < 100:
    if True:
      threshold_ind = np.array([ampData>curr_threshold])

      peak_ind, _ = find_peaks(list((ampData * threshold_ind)[0]), distance = int(1e-6/(timeData[1]-timeData[0])))

      peak_odd = 0
      if ampData[peak_ind[0]] > ampData[peak_ind[1]]:
        peak_odd = 1
      else:
        peak_odd = 2
      
      peak_time = timeData[peak_ind]

      if peak_odd == 1:
        dt_list = np.diff(peak_time[::2])
      else:
        dt_list = np.diff(peak_time[1::2])
      curr_threshold += 0.01
      first_tr_idx = peak_ind[0] if peak_odd == 1 else peak_ind[1]
      j += 1
    else:
      curr_threshold += 0.005
      j += 1

  return curr_threshold, np.array(dt_list)/1e-6, first_tr_idx