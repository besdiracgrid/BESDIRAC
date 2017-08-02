''' AccessTest

The base access test class to test the access to ces, clouds and ses.

'''

import subprocess, re
from datetime import datetime
from DIRAC import S_OK, S_ERROR, gConfig
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import TestBase
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEAccessTest import CEAccessTest
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CLOUDAccessTest import CLOUDAccessTest
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.SEAccessTest import SEAccessTest


class AccessTest( TestBase ):
  ''' AccessTest
  '''

  def __init__(self, args=None, apis=None):
    super( AccessTest, self ).__init__( args, apis )

    self.timeout = self.args.get( 'timeout', 5 )
    self.ce = CEAccessTest()
    self.cloud = CLOUDAccessTest()
    self.se = SEAccessTest()

  def doTest(self, elementDict):
    '''
      Use nc tool to test the access to the specified element.
      Test command is like 'nc -v -w 5 -z 202.122.33.148 22'.
    '''

    elementName = elementDict[ 'ElementName' ]
    elementType = elementDict[ 'ElementType' ]

    params = self._getAccessParams( elementName, elementType )
    if not params[ 'OK' ]:
      return params
    host, port = params[ 'Value' ]

    command = 'nc -v -w %d -z %s %s' % ( self.timeout, host, port )
    submissionTime = datetime.utcnow().replace( microsecond = 0 )
    subp = subprocess.Popen( command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    stdout, stderr = subp.communicate()
    completionTime = datetime.utcnow().replace( microsecond = 0 )
    applicationTime = (completionTime - submissionTime).total_seconds()

    if subp.returncode == 0:
      status = 'OK'
      log = stdout
    else:
      status = 'Bad'
      log = stderr

    result = { 'Result' : { 'Status' : status,
                           'Log' : log,
                           'SubmissionTime' : submissionTime,
                           'CompletionTime' : completionTime,
                           'ApplicationTime' : applicationTime },
              'Finish' : True }

    return S_OK(result)


  def _getAccessParams( self, elementName, elementType ):
    '''
      get the access host and port for the specified element.
    '''

    if elementType == 'ComputingElement':
      return self.ce._getAccessParams( elementName )
    elif elementType == "CLOUD":
      return self.cloud._getAccessParams( elementName )
    elif elementType == "StorageElement":
      return self.se._getAccessParams( elementName )
    else:
      return S_ERROR( "The elementType is not vaild." )
