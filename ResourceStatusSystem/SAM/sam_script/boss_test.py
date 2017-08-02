#!/usr/bin/env python

import socket, subprocess, time

hostname = socket.gethostname()

commands = """
cd $TMPDIR
source /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/setup.sh
source /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/scripts/6.6.4.p01/setup.sh
source /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/dist/6.6.4.p01/TestRelease/*/cmt/setup.sh
cp /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/dist/6.6.4.p01/TestRelease/*/run/rhopi.dec .
cp /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/dist/6.6.4.p01/TestRelease/*/run/jobOptions_sim.txt .
cp /cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/dist/6.6.4.p01/TestRelease/*/run/jobOptions_rec.txt .

cat jobOptions_rec.txt | grep -v "BESEVENTMIXER" > jobOptions_rec1.txt
echo "DatabaseSvc.DbType=\\"sqlite\\";" >> jobOptions_sim.txt
echo "DatabaseSvc.SqliteDbPath=\\"/cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/database/\\";" >>  jobOptions_sim.txt
echo "DatabaseSvc.DbType=\\"sqlite\\";" >> jobOptions_rec1.txt
echo "DatabaseSvc.SqliteDbPath=\\"/cvmfs/boss.cern.ch/slc5_amd64_gcc43/6.6.4.p01/database/\\";" >>  jobOptions_rec1.txt
echo "MessageSvc.OutputLevel = 6;" >>  jobOptions_sim.txt
echo "MessageSvc.OutputLevel = 6;" >>  jobOptions_rec1.txt

time boss.exe jobOptions_sim.txt
time boss.exe jobOptions_rec1.txt

ls -latr .
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
