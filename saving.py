import os
import datetime
from shutil import copyfile

'''
If candidate.txt does not exist in the root directory, creates and writes
the time the 'Log' Button is pressed.
'''
def log():
  currTime = datetime.datetime.now()

  date = currTime.strftime("%Y") + currTime.strftime("%m") + currTime.strftime("%d")

  timeStr = currTime.strftime("%X").replace(":", "")

  with open('candidate.txt', 'a') as file:
      file.write(date+"_"+timeStr+"\n")
      file.close()

  return(date+"_"+timeStr)

'''
Creates the path /log/{DATE}/{TIME}/, which is used to save data and graphs
while decoding
'''
def createFolder():

  currTime = datetime.datetime.now()

  date = currTime.strftime("%Y") + currTime.strftime("%m") + currTime.strftime("%d")

  timeStr = currTime.strftime("%X").replace(":", "")

  if not os.path.exists('log'):
    os.makedirs('log')

  os.chdir('log')

  if not os.path.exists(date):
    os.makedirs(date)

  os.chdir(date)
  os.makedirs(timeStr)
  os.chdir(timeStr)

  finPath = os.getcwd()

  os.chdir("../../../")

  return date+"_"+timeStr, finPath

'''
Copies one file to the path/name of outputFile. Used to copy the buffer and save
in the log
''' 
def copy(inputFile, outputFile):
  copyfile(inputFile, outputFile)