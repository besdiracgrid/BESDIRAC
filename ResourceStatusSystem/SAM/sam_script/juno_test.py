#!/usr/bin/env python

import socket, subprocess, time

hostname = socket.gethostname()

commands = """
ls /cvmfs/juno.ihep.ac.cn
source /cvmfs/juno.ihep.ac.cn/sl6_amd64_gcc44/J16v2r1-Pre2/setup.sh
python /cvmfs/juno.ihep.ac.cn/sl6_amd64_gcc44/J16v2r1-Pre2/offline/Examples/Tutorial/share/tut_detsim.py gun
"""

start = time.time()
subp = subprocess.Popen( ['bash', '-c', commands], stdout = subprocess.PIPE, stderr = subprocess.PIPE )
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
