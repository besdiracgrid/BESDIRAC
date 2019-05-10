#!/usr/bin/env python

import socket, subprocess, time

hostname = socket.gethostname()

commands = """
ls /cvmfs/boss.cern.ch/
"""

start = time.time()
subp = subprocess.Popen( commands, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
stdout, stderr = subp.communicate()
runningTime = time.time() - start

print 'Host Name :', hostname
print 'Running Time :', runningTime
print '\n'
if stdout:
    print '==============================Standard Output==============================\n'
    print stdout
    print '\n'
if stderr:
    print '==============================Standard Error===============================\n'
    print stderr
