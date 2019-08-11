import subprocess
import time

#Makes picoscope to save the current displaying data
#Currently saves one folder down
def saveData(buffer):
  time.sleep(.5)
  subprocess.call(['picoscope', '/a', 'File.SaveAs.IO=' + 'buffer' + str(buffer)+ '.mat'])
  time.sleep(1.2)
  return ("../" + "buffer" + str(buffer) + ".mat")

# Opens picoscope application, but encountered errors after opening
def openPicoScope():
  try:
      subprocess.call(['picoscope'])
  except:
      pass
  time.sleep(10)

#After paused by saving the file, runPico() makes pico run again
def runPico(self):
  subprocess.call(['picoscope', '/a', 'Run'])