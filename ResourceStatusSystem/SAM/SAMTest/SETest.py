""" SETest

  A test class to test the availability of SE.

"""

import os, time
from datetime                                           import datetime
from DIRAC                                              import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Client.DataManager      import DataManager
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import TestBase
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import LOCK
from BESDIRAC.ResourceStatusSystem.Utilities import BESUtils



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

    LOCK.acquire()
    proxyPath = BESUtils.getProxyByVO( 'zhangxm', vo )
    if not proxyPath[ 'OK' ]:
      LOCK.release()
      return proxyPath
    proxyPath = proxyPath[ 'Value' ]
    oldProxy = os.environ.get( 'X509_USER_PROXY' )
    os.environ[ 'X509_USER_PROXY' ] = proxyPath
    start = time.time()
    result = self.dm.putAndRegister( lfnPath, testFilePath, elementName )
    uploadTime = time.time() - start
    if result[ 'OK' ]:
      log += 'Succeed to upload file to SE %s.\n' % elementName
      log += 'Upload Time : %ss\n' % uploadTime

      start = time.time()
      result = self.dm.getReplica( lfnPath, elementName, self.__localPath )
      downloadTime = time.time() - start
      if result[ 'OK' ]:
        log += 'Succeed to download file from SE %s.\n' % elementName
        log += 'Download Time : %ss\n' % downloadTime
      else:
        status = 'Bad'
        log += 'Failed to download file from SE %s : %s\n' % ( elementName, result[ 'Message' ] )

      result = self.dm.removeFile( lfnPath )
      if result[ 'OK' ]:
        log += 'Succeed to delete file from SE %s.\n' % elementName
      else:
        log += 'Faile to delete file from SE %s : %s\n' % ( elementName, result[ 'Message' ] )

    else:
      status = 'Bad'
      log += 'Failed to upload file to SE %s : %s\n' % ( elementName, result[ 'Message' ] )
    if oldProxy is None:
      del os.environ[ 'X509_USER_PROXY' ]
    else:
      os.environ[ 'X509_USER_PROXY' ] = oldProxy
    LOCK.release()

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

