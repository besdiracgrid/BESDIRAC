""" SETest

  A test class to test the availability of SE.

"""

import os, time
from datetime                                           import datetime
from DIRAC                                              import S_OK, S_ERROR, gLogger
from DIRAC.Core.Utilities.Subprocess                    import systemCall
from DIRAC.DataManagementSystem.Client.DataManager      import DataManager
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import TestBase
from BESDIRAC.ResourceStatusSystem.Utilities            import BESUtils



class SETest( TestBase ):
  """
    SETest is used to test the availability of SE.
  """

  def __init__( self, args = None, apis = None ):
    super( SETest, self ).__init__( args, apis )

    self.timeout = self.args.get( 'timeout', 60 )
    self.__lfnPath = '/{vo}/user/z/zhangxm/'
    self.__testFile = 'test.dat'
    self.__localPath = '/tmp/'
    self.__scriptPath = '/opt/dirac/pro/BESDIRAC/ResourceStatusSystem/SAM/sam_script'
    self.__scriptName = 'se_test.py'

    if 'DataManager' in self.apis:
      self.dm = self.apis[ 'DataManager' ]
    else:
      self.dm = DataManager()


  def doTest( self, elementDict ):
    """
      Test upload and download for specified SE.
    """

    elementName = elementDict[ 'ElementName' ]
    vo = elementDict[ 'VO' ]

    testFilePath = self.__localPath + self.__testFile
    if not os.path.exists( testFilePath ) or not os.path.isfile( testFilePath ):
      f = open( testFilePath, 'w' )
      f.write( 'hello' )
      f.close()

    status = 'OK'
    log = ''
    lfnPath = self.__lfnPath.format(vo=vo) + elementName + '-' + self.__testFile
    submissionTime = datetime.utcnow().replace( microsecond = 0 )

    proxyPath = BESUtils.getProxyByVO( 'zhangxm', vo )
    if not proxyPath[ 'OK' ]:
      gLogger.error('Can not get proxy for VO %s' % vo)
      return proxyPath
    proxyPath = proxyPath[ 'Value' ]

    env_test = os.environ.copy()
    env_test[ 'X509_USER_PROXY' ] = proxyPath
    cmd = [os.path.join(self.__scriptPath, self.__scriptName), '-o', '/DIRAC/Security/UseServerCertificate=no', lfnPath, testFilePath, elementName]
    result = systemCall(300, cmd, env=env_test)
    print result
    if not result['OK']:
      status = 'Bad'
      log += 'Call %s failed: %s' % (self.__scriptName, result['Message'])
    elif result['Value'][0] != 0:
      status = 'Bad'
      log += '%s exit with error %s:\n%s' % (self.__scriptName, result['Value'][0], result['Value'][1])
    else:
      log += '%s exit successfully:\n%s' % (self.__scriptName, result['Value'][1])

    completionTime = datetime.utcnow().replace( microsecond = 0 )
    applicationTime = ( completionTime - submissionTime ).total_seconds()

    result = { 'Result' : { 'Status' : status,
                            'Log' : log,
                            'SubmissionTime' : submissionTime,
                            'CompletionTime' : completionTime,
                            'ApplicationTime' : applicationTime },
               'Finish' : True }

#    if os.path.exists( testFilePath ) and os.path.isfile( testFilePath ):
#      os.remove( testFilePath )
    localFile = self.__localPath + elementName +'-' + self.__testFile
    if os.path.exists( localFile ) and os.path.isfile( localFile ):
      os.remove( localFile )

    return S_OK( result )

