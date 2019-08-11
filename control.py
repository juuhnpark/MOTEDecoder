import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqtgraph.Qt import QtGui, QtCore

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib as mpl
mpl.use("TkAgg")
import matplotlib.pyplot as plt
import random
import time
from decode import decode
from picoscope import *
from saving import *
from transform import *

class App(QWidget):
  
  def __init__(self):
    super().__init__()
    
    self.initUI()
      
  def initUI(self):
    self.setWindowTitle('Signal Decoder')    
    self.decoding = True
    self.threshold = None
    self.runNum = 0
    self.manualThreshold = False
    self.buffer = 0
    self.maxBuffer = 5
    self.saving = False
    self.transform = True
    
    grid = QGridLayout()
    self.setLayout(grid) 
    
    #row 1
    #Decode Only Button
    self.decodeOnlyBtn = QRadioButton('Decode Only')
    self.decodeOnlyBtn.setChecked(True)
    self.decodeOnlyBtn.toggled.connect(lambda:self.radioButtonFn(self.decodeOnlyBtn))
    grid.addWidget(self.decodeOnlyBtn, 1, 0)

    #Decode and Save Button
    self.decodeAndSaveBtn = QRadioButton('Decode and Save')
    self.decodeAndSaveBtn.toggled.connect(lambda:self.radioButtonFn(self.decodeAndSaveBtn))
    grid.addWidget(self.decodeAndSaveBtn, 1, 1)

    #Decode Button
    decodeButton = QPushButton('Decode')
    decodeButton.clicked.connect(self.resumePressed)
    grid.addWidget(decodeButton, 1, 2)

    #Pause Button
    pauseButton = QPushButton('Pause')
    pauseButton.clicked.connect(self.pausePressed)
    grid.addWidget(pauseButton, 1, 3)

    #Log Button
    logButton = QPushButton('Log')
    logButton.clicked.connect(self.logPressed)
    grid.addWidget(logButton, 1, 4)

    #Exit Button
    exitButton = QPushButton('Exit')
    exitButton.clicked.connect(self.exitPressed)
    grid.addWidget(exitButton, 1, 5)

    #row 2
    self.thresholdCheckBox = QCheckBox('Manual Threshold')
    grid.addWidget(self.thresholdCheckBox, 2, 0)
    self.thresholdCheckBox.setChecked(False)
    self.thresholdCheckBox.stateChanged.connect(self.checkboxChange)

    thresholdLabel = QLabel('Current Threshold: ')
    thresholdLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    grid.addWidget(thresholdLabel, 2, 1)

    maxThreshold = 0.300

    #Spinbox for Manual Threshold
    self.thresholdSpinBox = QDoubleSpinBox()
    if self.threshold:
      self.thresholdSpinBox.setValue(self.threshold)
    self.thresholdSpinBox.setMaximum(maxThreshold)
    self.thresholdSpinBox.setMinimum(0.000)
    self.thresholdSpinBox.setSingleStep(0.001)
    self.thresholdSpinBox.valueChanged.connect(self.spinboxChange)
    self.thresholdSpinBox.setDecimals(3)
    grid.addWidget(self.thresholdSpinBox, 2, 2)

    #Slider for Manual Threshold
    self.thresholdSlider = QSlider(QtCore.Qt.Horizontal)
    self.thresholdSlider.setMinimum(0)
    self.thresholdSlider.setMaximum(maxThreshold*1000)
    if self.threshold:
      self.thresholdSlider.setValue(self.threshold*1000)
    self.thresholdSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
    self.thresholdSlider.setTickPosition(QSlider.TicksBothSides)
    self.thresholdSlider.setTickInterval(1)
    grid.addWidget(self.thresholdSlider, 2, 3, 1, 1)
    self.thresholdSlider.valueChanged.connect(self.sliderValueChange)
    
    #Threshold Reset Button
    resetButton = QPushButton('Reset Threshold')
    resetButton.clicked.connect(self.resetPressed)
    grid.addWidget(resetButton, 2, 4)

    #Offset Removal Button    
    self.offsetCheckBox = QCheckBox('Offset Removal')
    grid.addWidget(self.offsetCheckBox, 2, 0)
    self.offsetCheckBox.setChecked(False)
    self.offsetCheckBox.stateChanged.connect(self.offsetCheckboxChange)

    #row 3 + 4 - decoded plot
    self.decodedPlot = PlotCanvas(self, width=10, height=3)
    plotToolbar = NavigationToolbar(self.decodedPlot, self.decodedPlot)
    grid.addWidget(plotToolbar, 3, 0, 1, 6)    
    grid.addWidget(self.decodedPlot, 4, 0, 1, 6)

    #row 5 + 6 - raw data (decoded) plot
    self.decodedData = PlotCanvas(self, width=10, height=3)
    dataToolbar = NavigationToolbar(self.decodedData, self.decodedData)
    grid.addWidget(dataToolbar, 5, 0, 1, 6)
    grid.addWidget(self.decodedData, 6, 0, 1, 6)
    

    self.decodedPlot.setAxesTitle('Decoded Plot', 'Time (ms)', 'Δt (μs)')
    self.decodedData.setAxesTitle('Decoded Data', 'Time (ms)', 'Voltage (mV)')

    self.show()
  
  def logPressed(self):
    t = log()
    print("Log Success: ", t)

  def radioButtonFn(self, b):
    if b.text() == "Decode Only":
      if b.isChecked() == True:
        self.saving = False
    
    if b.text() == "Decode and Save":
      if b.isChecked() == True:
        self.saving = True

  def resetPressed(self):
    self.threshold = None
    self.thresholdSpinBox.setValue(0)
  
  def sliderValueChange(self):
    if self.manualThreshold:
      self.threshold = self.thresholdSlider.value()/1000
      self.thresholdSpinBox.setValue(self.threshold)
    print(self.threshold)

  def spinboxChange(self, currThreshold):
    if self.manualThreshold:
      try: 
        self.threshold = currThreshold
        self.thresholdSlider.setValue(self.threshold*1000)
      except:
        self.threshold = 0.0
    print(self.threshold)

  def offsetCheckboxChange(self, state):
    if state == QtCore.Qt.Checked:
      self.transform = True
    else:
      self.transform = False
    print(f"Offset Removal")


  def checkboxChange(self, state):
    if state == QtCore.Qt.Checked:
      self.manualThreshold = True
    else:
      self.manualThreshold = False
    print("Manual Threshold: ", self.manualThreshold)

  def resumePressed(self):
    self.decoding = True
    print("Resumed")

  def pausePressed(self):
    self.decoding = False
    print("Paused")

  def exitPressed(self):
    print("Exit")
    self.close()

  def start(self):
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      QtGui.QApplication.instance().exec_()

  #can control the timer.start() parameter to inc/decrease speed
  def animation(self):
    timer = QtCore.QTimer()
    timer.timeout.connect(self.update)
    timer.start(3000)
    self.start()
  
  def update(self):
    if self.decoding:
      print(self.runNum)
      self.runNum += 1
      self.decodedPlot.clear()
      self.decodedData.clear()
      
      dataPath = saveData(self.buffer)

      if self.transform:
        transform(dataPath)
      # dataPath = '20190723_MOTE_V4_C1_Released_50mVpp_500Hz_9A_A=0p5_3.mat'

      timestamp, fin_delta_t, timeData, threshold_amp, tr_window, ts_peak_ind, chosen_ts_list, dist_figure, prevThreshold, time_in_range = decode(dataPath, self.threshold)

      if not self.manualThreshold:
        self.threshold = prevThreshold
        self.thresholdSpinBox.setValue(self.threshold)

      self.decodedPlot.plot(x_data=timestamp, y_data=fin_delta_t, color='r')
      self.decodedPlot.plot(x_data=timestamp, y_data=fin_delta_t, color='.')

      self.decodedData.plot(x_data=timeData, y_data=threshold_amp, color='y')
      self.decodedData.plot(x_data=timeData, y_data=tr_window, color='b')
      self.decodedData.plot(x_data=timeData[ts_peak_ind], y_data=threshold_amp[ts_peak_ind], color='p')
      self.decodedData.plot(x_data=timeData[chosen_ts_list], y_data=threshold_amp[chosen_ts_list], color='g')
      self.decodedData.plot(x_data=timeData, y_data=dist_figure, color='r')
      self.decodedData.plot(x_data=timeData, y_data=time_in_range, color='c')

      self.decodedPlot.setAxesTitle('Decoded Plot', 'Time (ms)', 'Δt (μs)')
      self.decodedData.setAxesTitle('Decoded Data', 'Time (ms)', 'Voltage (mV)')

      if self.saving:
        outputName, finalPath = createFolder()
        self.decodedPlot.saveFig(finalPath + '/Decoded Plot.png')
        self.decodedData.saveFig(finalPath + '/Decoded Data.png')
        copy(dataPath, finalPath + '/' + outputName + '.mat')
      
      self.buffer = (self.buffer + 1)%self.maxBuffer
      runPico()

class PlotCanvas(FigureCanvas):

  def __init__(self, parent=None, width=5, height=4, dpi=100):
    self.fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = self.fig.add_subplot(111)

    FigureCanvas.__init__(self, self.fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self,
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
    FigureCanvas.updateGeometry(self)

  def setAxesTitle(self, title, x_axis, y_axis):
    self.axes.set_title(title)
    self.axes.set_xlabel(x_axis)
    self.axes.set_ylabel(y_axis)

  def plot(self, x_data, y_data, color):
    # ax = self.figure.add_subplot(111)
    self.axes.plot(x_data, y_data, color)
    self.draw()

  def saveFig(self, fileName):
    self.fig.savefig(fileName, dpi = 300)

  def clear(self):
    self.axes.clear()
        
if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = App()
  ex.animation()