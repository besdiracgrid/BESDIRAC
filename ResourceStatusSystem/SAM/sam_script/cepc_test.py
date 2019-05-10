#!/usr/bin/env python

import socket, subprocess, time

hostname = socket.gethostname()

commands = """
wget http://cvmfs.ihep.ac.cn/pub/cepc/cepc_test_job.tgz
tar xvfz cepc_test_job.tgz
cd cepc_test_job
echo
echo Job Start
./simu.sh
echo
if [ $? -eq 0 ]; then
    echo Job Done.
else
    echo Job Failed.
fi
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
