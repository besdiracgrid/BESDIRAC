#!/usr/bin/env python

from DIRAC.Core.Base import Script
Script.parseCommandLine(ignoreErrors = False)
args = Script.getPositionalArgs()

import time
import tempfile

from DIRAC import S_OK, S_ERROR, gLogger, exit

from DIRAC.DataManagementSystem.Client.DataManager      import DataManager

lfn = args[0]
pfn = args[1]
se = args[2]

exit_code = 0
log = ''

dm = DataManager()

start = time.time()
result = dm.removeFile( lfn )
result = dm.putAndRegister( lfn, pfn, se )
uploadTime = time.time() - start
if result[ 'OK' ]:
  log += 'Succeed to upload file to SE %s.\n' % se
  log += 'Upload Time : %ss\n' % uploadTime

  start = time.time()
  result = dm.getReplica( lfn, se, tempfile.gettempdir() )
  downloadTime = time.time() - start
  if result[ 'OK' ]:
    log += 'Succeed to download file from SE %s.\n' % se
    log += 'Download Time : %ss\n' % downloadTime
  else:
    exit_code = 1
    log += 'Failed to download file from SE %s : %s\n' % ( se, result[ 'Message' ] )

  result = dm.removeFile( lfn )
  if result[ 'OK' ]:
    log += 'Succeed to delete file from SE %s.\n' % se
  else:
    log += 'Faile to delete file from SE %s : %s\n' % ( se, result[ 'Message' ] )

else:
  exit_code = 1
  log += 'Failed to upload file to SE %s : %s\n' % ( se, result[ 'Message' ] )

print(log)
exit(exit_code)
