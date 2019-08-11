import scipy.io
from scipy import stats
from scipy.signal import find_peaks
import numpy as np
import matplotlib as mpl
import heapq
mpl.use("TkAgg")
import matplotlib.pyplot as plt
from decode_helper import approx_threshold_deltat

def decode(fileName, threshold):
  # Load Data
  mat = scipy.io.loadmat(fileName)

  amp = mat['C'].transpose().flatten()

  time = np.arange(np.shape(amp)[0])*mat['Tinterval'][0]

  #find meaningful statistics
  approximated_threshold, deltat_list, first_tr_ind = approx_threshold_deltat(amp, time, threshold)

  #Zero out all peaks less than threshold
  threshold_amp = np.where(amp>approximated_threshold, amp, 0)

  delta_t = np.median(deltat_list)*1e-6
  delta_t_idx = int(delta_t/(time[1]-time[0]))

  #Locally maximize peaks
  all_peak_ind, _ = find_peaks(threshold_amp, distance = int(delta_t_idx*.05))
  tr_peak_ind = []

  #Find first reference peak - currently one with greater amplitude, but needs
  #to be changed
  if amp[all_peak_ind[0]] < amp[all_peak_ind[1]]:
    tr_peak_ind.append(all_peak_ind[1])
  else:
    tr_peak_ind.append(all_peak_ind[0])

  #Reference peak windowing to find proper reference peaks
  temp_idx = tr_peak_ind[0]
  time_in_range = np.zeros((time.shape))

  while temp_idx < len(amp):
    window = temp_idx + delta_t_idx
    windowSize = int(delta_t_idx*.1)
    curr_window_l, curr_window_r = window - windowSize, window + windowSize
    time_in_range[curr_window_l:curr_window_r] = -1
    
    greaterL = all_peak_ind[all_peak_ind > curr_window_l]
    lessR = greaterL[greaterL < curr_window_r]
    if np.any(lessR):
      tr_peak_ind.append(lessR[np.argmax(lessR)])
      temp_idx = lessR[0]
    else:
      temp_idx += delta_t_idx

  if amp[tr_peak_ind[0]] < amp[tr_peak_ind[1]]:
    tr_peak_ind = tr_peak_ind[1:]

  first_tr_ind = tr_peak_ind[0]

  #find ts peak index
  ts_peak_ind, _ = find_peaks(threshold_amp, distance = int(delta_t_idx*.05))
  ts_peak_ind = np.setdiff1d(ts_peak_ind, tr_peak_ind)

  #shift all data to start from first reference peak
  amp = amp[first_tr_ind:]
  threshold_amp = threshold_amp[first_tr_ind:]
  time = time[first_tr_ind:]
  time_in_range = time_in_range[first_tr_ind:]
  tr_peak_ind = np.subtract(tr_peak_ind, first_tr_ind)
  ts_peak_ind = np.subtract(ts_peak_ind, first_tr_ind)


  #tr window
  window_size = int((delta_t_idx*.1)/2)
  tr_window = np.zeros(len(amp))
  for i in range(0, len(tr_peak_ind)-1):
    curr_idx = tr_peak_ind[i]
    for j in range(-window_size, window_size):
      if curr_idx+j < 0 or curr_idx+j > len(amp)-1:
        pass
      else:
        tr_window[curr_idx+j] = amp[curr_idx]

  #calculate ts-tr, final decoding
  fin_delta_t = []
  timestamp = []
  chosen_ts_list = []
  dist_figure = np.zeros(time.shape)

  def find_least_delta(prev_values, potential_list):
    if not prev_values:
      return potential_list[0]
    else:
      latest_val = prev_values[-1]
      subtracted = np.absolute(np.subtract(potential_list, latest_val))
      most_likely = potential_list[np.argmin(subtracted)]

      # to avoid outliers
      if abs(most_likely - latest_val) < 5*1e-6:
        return most_likely
      else:
        return 0

  for i, tr_idx in enumerate(tr_peak_ind[:-1]):
    ts_between = ts_peak_ind[np.where((ts_peak_ind > tr_idx) & (ts_peak_ind < tr_idx + delta_t_idx))[0]]

    if ts_between.any():
      if len(ts_between) == 1:
        if chosen_ts_list:
          to_append = (ts_between[0]-tr_idx)*(time[1]-time[0])
          if abs(to_append - fin_delta_t[-1]) > 30*1e-6:
            to_append = 0
        else:
          to_append = (ts_between[0]-tr_idx)*(time[1]-time[0])
      else:
        possible_dt_list = np.subtract(ts_between, tr_idx)*(time[1]-time[0])
        to_append = find_least_delta(fin_delta_t, possible_dt_list) 

      if to_append != 0:
        fin_delta_t.append(to_append)
        timestamp.append(tr_idx*(time[1]-time[0]))
        chosen_ts_list.append(int(to_append/(time[1]-time[0])+tr_idx))
        to_append_idx = int(to_append/(time[1]-time[0]))
        dist_figure[tr_idx:tr_idx+to_append_idx] = 1
        
  #handle outliers
  standDev = np.std(fin_delta_t)
  print(fin_delta_t)
  fin_delta_t_mean = np.mean(fin_delta_t)
  overStd = [fin_delta_t <= fin_delta_t_mean+2*standDev]
  underStd = [fin_delta_t >= fin_delta_t_mean-2*standDev]
  comb = np.multiply(underStd, overStd)

  fin_delta_t = np.array(fin_delta_t)[np.where(comb)[1]]
  timestamp = np.array(timestamp)[np.where(comb)[1]]

  #make zeros to nan for dist_figure
  #dist_figure is the red line of decoded data
  dist_figure[ dist_figure==0 ] = np.nan

  timestamp = np.array(timestamp) * 1000

  chosen_ts_list = np.array(chosen_ts_list)

  time *= 1000
  threshold_amp *= 1000
  tr_window *= 1000
  fin_delta_t = np.multiply(fin_delta_t,1e6)
  
  return timestamp, fin_delta_t, time, threshold_amp, tr_window, ts_peak_ind, chosen_ts_list, dist_figure, approximated_threshold, time_in_range