""" TestExecutor

  TestExecutor is the end-point to executor SAM tests. It loads the tests which
  need to be executed dynamically and executes all the tests. At last, it stores
  the test results to database.
"""

import Queue
from datetime import datetime
from DIRAC                                                         import S_OK, S_ERROR, gLogger
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient import ResourceManagementIHEPClient


__RCSID__ = '$Id:  $'


class TestExecutor( object ):
  """ TestExecutor
  """

  def __init__( self, tests, apis = None ):
    """ Constructor

    examples:
      >>> tests = { 'WMS-Test' : { 'module' : 'WMSTest',
                                                           'args' : { 'executable' : [ '/usr/bin/python',
                                                                           'wms_test.py' ], 'timeout' : 1800 } } }
      >>> elements = { 'ComputingElement' : [ 'chenj01.ihep.ac.cn' ],
                                       'StorageElement', [ 'IHEPD-USER' ],
                                       'CLOUD' : [ 'CLOUD.IHEP-OPENSTACK.cn' ] }
      >>> executor = TestExecutor( tests, elements )
      >>> executor1 = TestExecutor( tests, elements, { 'ResourceManagementClient' :
                                                                                                     ResourceManagementClient() } )

    :Parameters:
      **tests** - `dict`
        dictionary with tests to be executed. The test class is loaded according to the
        'module' key and instantiated with 'args' key.
      **elements** - `dict`
        the elements need to be tested. The elements is grouped by type.
      **apis** - 'dict'
        dictionary with clients to be used in the commands issued by the policies.
        If not defined, the commands will import them.
    """

    self.apis = apis or {}
    self.__tests = tests
    self.log = gLogger.getSubLogger( 'TestExecutor' )

    if 'ResourceManagementIHEPClient' in self.apis:
      self.rmClient = self.apis[ 'ResourceManagementIHEPClient' ]
    else:
      self.rmClient = ResourceManagementIHEPClient()


  def __matchTests( self, matchArgs ):
    execTests = []

    for testType, testDict in self.__tests.items():

      testMatchArgs = testDict[ 'match' ]

      match = True
      for name, value in matchArgs.items():
        if not value:
          continue

        if type( value ) == str:
          value = ( value, )

        if not testMatchArgs.has_key( name ):
          continue

        target = testMatchArgs[ name ]
        if type( target ) == str:
          target = ( target, )

        match = False
        for val in value:
          if val in target:
            match = True
            break

        if not match:
          break

      if match:
        execTests.append( testType )

    return execTests


  def __storeTestResults( self, elementName, elementType, testResults ):
    """
      store the test results.
    """
    for testType, testDict in testResults.items():
      testDict[ 'CompletionTime' ] = testDict.get( 'CompletionTime' ) or '0000-0-0'
      testDict[ 'ApplicationTime' ] = testDict.get( 'ApplicationTime' ) or 0

      resQuery = self.rmClient.addOrModifySAMResult(
                                                         elementName,
                                                         testType,
                                                         elementType,
                                                         testDict.get( 'Status' ),
                                                         testDict.get( 'Log' ),
                                                         testDict.get( 'JobID' ),
                                                         testDict.get( 'SubmissionTime' ),
                                                         testDict.get( 'CompletionTime' ),
                                                         testDict.get( 'ApplicationTime' ),
                                                         testDict.get( 'LastCheckTime' )
                                                         )
      if not resQuery[ 'OK' ]:
        return resQuery

    return S_OK()


  def execute( self, element, lastCheckTime = None ):
    """ Main method which executes the tests and obtains the results. Use
    two loops to do all the work. In the first loop, execute all the tests for
    corresponding elements and put the executed tests into  executedTestsQueue.
    In the second loop, traverse executedTestsQueue to obtain test results.

    examples:
      >>> executor.execute()[ 'Value' ]
          { 'Records' : ( ( 'chenj01.ihep.ac.cn', 'WMS-Test', 'ComputingElement', 'OK',
                                       'balabala', 1, '2016-5-8 00:00:00', '2016-5-8 00:05:23', 0.1234 ),
                                    ( 'chenj01.ihep.ac.cn', 'BOSS-Test', 'ComputingElement', 'Bad',
                                       'balabala', 2, '2016-5-8 00:00:00', '0000-0-0', 0 ),
                                    ( 'IHEPD-USER', 'SE-Test', 'StorageElement', 'Bad',
                                      'balabala', None, '2016-5-8 00:00:00', '0000-0-0', 0 ) ),
             'Columns' : ( 'ElementName', 'TestType', 'ElementType', 'Status',
                                      'Log', 'JobID', 'SubmissionTime', 'CompletionTime', 'ApplicationTime' ) }

    :return: S_OK( { 'Records' : `tuple`, 'Columns' : `tuple` } ) / S_ERROR
    """

    elementName = element['ElementName' ]
    elementType = element[ 'ElementType' ]
    lastCheckTime = lastCheckTime or datetime.utcnow().replace( micresecond = 0 )

    matchArgs = { 'ElementType' : elementType, 'VO' : element.get( 'VO' ) }
    execTests = self.__matchTests( matchArgs )
    if execTests == []:
      return S_ERROR( 'No SAM test matched for %s' % elementName )

    testResults = {}
    runningTestsQueue = Queue.Queue()
    for testType in execTests:
      testObj = self.__tests[ testType ][ 'object' ]
      result = testObj.doTest( element )
      if not result[ 'OK' ]:
        self.log.error( 'Failed to execute %s for %s' % ( testType, elementName ) )
        self.log.error( result[ 'Message' ] )
        return S_ERROR( 'Failed to execute SAM tests.' )
      result = result[ 'Value' ]
      result[ 'Result' ][ 'LastCheckTime' ] = lastCheckTime
      testResults[ testType ] = result[ 'Result' ]
      if not result[ 'Finish' ]:
        runningTestsQueue.put( testType )

    while not runningTestsQueue.empty():
      testType = runningTestsQueue.get_nowait()
      testObj = self.__tests[ testType ][ 'object' ]
      jobID = testResults[ testType ][ 'JobID' ]
      vo = testResults[ testType ][ 'VO' ]
      submissionTime = testResults[ testType ][ 'SubmissionTime' ]
      result = testObj.getTestResult( elementName, vo, jobID, submissionTime )
      if not result[ 'OK' ]:
        self.log.error( 'Failed to get %s result for %s' % ( testType, elementName ) )
        self.log.error( result[ 'Message' ] )
        return S_ERROR( 'Failed to get SAM test results.' )
      result = result[ 'Value' ]
      if not result:
        runningTestsQueue.put( testType )
      else:
        testResults[ testType ].update( result )
      runningTestsQueue.task_done()

    runningTestsQueue.join()

    storeRes = self.__storeTestResults( elementName, elementType, testResults )
    if not storeRes[ 'OK' ]:
      return S_ERROR( 'Failed to store SAM test results: %s' % storeRes[ 'Message' ] )

    testsStatus = {}
    for testType, testDict in testResults.items():
      testsStatus[ testType ] = testDict[ 'Status' ]
    return S_OK( testsStatus )
