""" CEBaseTest

  Base class for all the CE test classes.

"""

import os, threading
from datetime                                           import datetime, timedelta
from DIRAC                                              import S_OK
from DIRAC.Interfaces.API.Job                           import Job
from DIRAC.Interfaces.API.Dirac                         import Dirac
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import TestBase
from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.TestBase import LOCK
from BESDIRAC.ResourceStatusSystem.Utilities import BESUtils


__RCSID__ = '$Id: $'




class CEBaseTest( TestBase ):
  """
    CEBaseTest is base class for all the CE test classes. Real  CE test should
    implement its _judge method.
  """

  def __init__( self, args = None, apis = None ):
    super( CEBaseTest, self ).__init__( args, apis )

    self.timeout = self.args.get( 'timeout', 1800 )
    self.vo = self.args.get( 'VO' )
    self.testType = self.args[ 'TestType' ]
    self.executable = self.args[ 'executable' ]
    self.__logPath = '/opt/dirac/pro/BESDIRAC/ResourceStatusSystem/SAM/log'
    self.__scriptPath = '/opt/dirac/pro/BESDIRAC/ResourceStatusSystem/SAM/sam_script'

    if 'WMSAdministrator' in self.apis:
      self.wmsAdmin = self.apis[ 'WMSAdministrator' ]
    else:
      self.wmsAdmin = RPCClient( 'WorkloadManagement/WMSAdministrator' )

    if 'Dirac' in self.apis:
      self.dirac = self.apis[ 'Dirac' ]
    else:
      self.dirac = Dirac()


  def doTest( self, elementDict ):
    """
      submit test job to the specified ce or cloud..
    """

    elementName = elementDict[ 'ElementName' ]
    elementType = elementDict[ 'ElementType' ]
    vos = elementDict[ 'VO' ]

    site = None; ce = None
    if elementType == 'ComputingElement':
      ce = elementName
    if elementType == 'CLOUD':
      site = elementName

    if self.vo:
      submitVO = self.vo
    elif vos:
      submitVO = vos[ 0 ]
    else:
      submitVO = 'bes'

    submissionTime = datetime.utcnow().replace( microsecond = 0 )
    sendRes = self.__submit( site, ce, submitVO )
    if not sendRes[ 'OK' ]:
      return sendRes
    jobID = sendRes[ 'Value' ]

    result = { 'Result' : { 'JobID' : jobID,
                           'VO' : submitVO,
                           'SubmissionTime' : submissionTime },
              'Finish' : False }

    return S_OK( result )


  def __submit( self, site, CE, vo ):
    """
      set the job and submit.
    """

    job = Job()
    job.setName( self.testType )
    job.setJobGroup( 'CE-Test' )
    job.setExecutable( self.executable )
    job.setInputSandbox( '%s/%s' % ( self.__scriptPath, self.executable ) )
    if site and not CE:
      job.setDestination( site )
    if CE:
      job.setDestinationCE( CE )

    LOCK.acquire()
    proxyPath = BESUtils.getProxyByVO( 'zhangxm', vo )
    if not proxyPath[ 'OK' ]:
      LOCK.release()
      return proxyPath
    proxyPath = proxyPath[ 'Value' ]
    oldProxy = os.environ.get( 'X509_USER_PROXY' )
    os.environ[ 'X509_USER_PROXY' ] = proxyPath
    result = self.dirac.submit( job )
    if oldProxy is None:
      del os.environ[ 'X509_USER_PROXY' ]
    else:
      os.environ[ 'X509_USER_PROXY' ] = oldProxy
    LOCK.release()

    return result


  def getTestResult( self, elementName, vo, jobID, submissionTime ):
    """
      download output sandbox and judge the test status from the log file.
    """

    isFinish = False

    res = self.__getJobOutput( jobID, vo )
    if not res[ 'OK' ]:
      return res
    output = res[ 'Value' ]
    status = res[ 'Status' ]

    resDict = { 'CompletionTime' : None, 'Status' : None, 'Log' : None, 'ApplicationTime' : None }
    utcNow = datetime.utcnow().replace( microsecond = 0 )

    if output:
      isFinish = True
      resDict[ 'CompletionTime' ] = utcNow
      log = output[ 'Log' ]
      if not output[ 'Download' ]:
        resDict[ 'Status' ] = 'Unknown'
        resDict[ 'Log' ] = 'Fail to download log file for job %s: %s' % ( jobID, log )
      else:
        resDict[ 'Log' ] = log
        resDict[ 'Status' ] = self._judge( log )
        resDict[ 'AppliactionTime' ] = self.__getAppRunningTime( log )

    else:
      if utcNow - submissionTime >= timedelta( seconds = self.timeout ):
        isFinish = True
        if elementName.split( '.' )[ 0 ] == 'CLOUD':
          site = elementName
        else:
          site = BESUtils.getSiteForCE( elementName )
        jobCount = self.wmsAdmin.getSiteSummaryWeb( { 'Site' : site }, [], 0, 0 )
        if not jobCount[ 'OK' ]:
          return jobCount
        params = jobCount[ 'Value' ][ 'ParameterNames' ]
        records = jobCount[ 'Value' ][ 'Records' ][ 0 ]
        run = records[ params.index( 'Running' ) ]
        done = records[ params.index( 'Done' ) ]
        if status == 'Waiting' and run == 0 and done == 0:
          resDict[ 'Status' ] = 'Bad'
          resDict[ 'Log' ] = 'The test job is waiting for %d seconds, but no running and done jobs at this site.' % self.timeout
        else:
          if run != 0:
            resDict[ 'Status' ] = 'Busy'
            resDict[ 'Log' ] = 'Site %s is too busy to execute this test job, job status is %s' % ( site, status )
          else:
            resDict[ 'Status' ] = 'Unknown'
            resDict[ 'Log' ] = 'Test did not complete within the timeout of %d seconds, job status is %s' % ( self.timeout, status )
        self.dirac.kill( jobID )

    if not isFinish:
      return S_OK()
    else:
      return S_OK( resDict )


  def __getJobOutput( self, jobID, vo ):
    status = self.dirac.status( jobID )
    if not status[ 'OK' ]:
      return status
    status = status[ 'Value' ][ jobID ][ 'Status' ]

    if status in ( 'Done', 'Failed' ):
      LOCK.acquire()
      proxyPath = BESUtils.getProxyByVO( 'zhangxm', vo )
      if not proxyPath[ 'OK' ]:
        LOCK.release()
        return proxyPath
      proxyPath = proxyPath[ 'Value' ]
      oldProxy = os.environ.get( 'X509_USER_PROXY' )
      os.environ[ 'X509_USER_PROXY' ] = proxyPath
      outputRes = self.dirac.getOutputSandbox( jobID, self.__logPath )
      if oldProxy is None:
        del os.environ[ 'X509_USER_PROXY' ]
      else:
        os.environ[ 'X509_USER_PROXY' ] = oldProxy
      LOCK.release()

      if not outputRes[ 'OK' ]:
        ret = S_OK( { 'Download'  : False, 'Log' : outputRes[ 'Message' ] } )
      else:
        try:
          logfile = open( '%s/%d/Script1_CodeOutput.log' % ( self.__logPath, jobID ), 'r' )
          log = logfile.read()
          logfile.close()
        except IOError, e:
          raise IOError
        os.system( 'rm -rf %s/%d' % ( self.__logPath, jobID ) )
        ret = S_OK( { 'Download' : True, 'Log' : log } )
    else:
      ret = S_OK()

    ret[ 'Status' ] = status
    return ret


  @staticmethod
  def __getAppRunningTime( log ):
    index = log.find( 'Running Time :' )
    runtime = ''
    while log[ index ] != '\n':
      runtime += log[ index ]
      index += 1
    runtime = float( runtime[ len( 'Running Time :'  ) : ].strip() )

    return runtime


  @staticmethod
  def _judge( log ):
    """
      to be extended by real ce tests.
    """

    return 'OK'
