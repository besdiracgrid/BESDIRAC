''' SAMTestAgent

  This agent executes SAM tests and evaluates resources and sites SAM status.

'''

import threading
from datetime import datetime
from DIRAC                                             import S_OK, gConfig, gLogger
from DIRAC.Core.Base.AgentModule                       import AgentModule
from DIRAC.Core.DISET.RPCClient                        import RPCClient
from DIRAC.ResourceStatusSystem.Utilities              import CSHelpers
from DIRAC.DataManagementSystem.Client.DataManager                 import DataManager
from DIRAC.ResourceStatusSystem.Utilities import Utils
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient
from BESDIRAC.ResourceStatusSystem.SAM.TestExecutor                import TestExecutor
from BESDIRAC.ResourceStatusSystem.SAM.StatusEvaluator             import StatusEvaluator
from BESDIRAC.ResourceStatusSystem.Utilities import BESUtils


__RCSID__ = '$Id:  $'
AGENT_NAME = 'ResourceStatus/SAMTestAgent'


class SAMTestAgent(AgentModule):
  """ SAMTestAgent
  
    The SAMTestAgent is used to execute SAM tests and evaluate SAM status
    periodically. It executes tests with TestExecutor and evaluates status with
    StatusEvaluator.
  """
    
  def __init__(self, *args, **kwargs):
    AgentModule.__init__(self, *args, **kwargs)
        
    self.tests = {}
    self.apis = {}
         
         
  def initialize(self):
    """ 
      specify the tests which need to be executed.
    """
    

    self.apis[ 'DataManager' ] = DataManager()
    self.apis[ 'ResourceManagementClient' ] = ResourceManagementClient()
    
    return S_OK()
        
        
  def execute(self):
    """ 
      The main method of the agent. It get elements which need to be tested and 
      evaluated from CS. Then it instantiates TestExecutor and StatusEvaluate and 
      calls their main method to finish all the work.
    """

    from BESDIRAC.ResourceStatusSystem.SAM.SAMTest import TestConfiguration
    self.tests = TestConfiguration.TESTS
    self.__loadTestObj()

    self.testExecutor = TestExecutor( self.tests, self.apis )
    self.statusEvaluator = StatusEvaluator( self.apis )

    elements = []
    sitesCEs = {}

    ses = gConfig.getValue( 'Resources/StorageElementGroups/SE-USER' )
    for se in ses.split( ', ' ):
      elements.append( { 'ElementName' : se, 
                                              'ElementType' : 'StorageElement' } )    

    noTestSites = [ site.strip() for site in self.am_getOption( 'noTestSite', '' ).split( ',' ) if site != '' ]
    wmsAdmin = RPCClient('WorkloadManagement/WMSAdministrator')
    activeSites = wmsAdmin.getSiteMask()
    if not activeSites[ 'OK' ]:
      return activeSites
    activeSites = [ site for site in activeSites[ 'Value' ] if site not in noTestSites ]

    for siteName in activeSites:
      domain = siteName.split('.')[ 0 ]
      vos = BESUtils.getSiteVO( siteName )
      if 'CLOUD' != domain:
        siteCEs = CSHelpers.getSiteComputingElements( siteName )
        sitesCEs[ siteName ] = siteCEs
        for ce in siteCEs:
          elements.append( { 'ElementName' : ce, 
                                                  'ElementType' : 'ComputingElement',
                                                  'VO' : vos } )
      else:
        sitesCEs[ siteName ] = [ siteName ]
        elements.append( { 'ElementName' : siteName,
                                                'ElementType' : 'CLOUD',
                                                'VO' : vos } )
        
    lastCheckTime = datetime.utcnow().replace(microsecond = 0)
    self.elementsStatus = {}

    threads = []
    for elementDict in elements:
      t = threading.Thread( target = self._execute, args = ( elementDict, ) )
      threads.append( t )
      t.start()
      
    for thread in threads:
      thread.join()

    for siteName in activeSites:
      seList = CSHelpers.getSiteStorageElements( siteName )
      se = ''
      if [] != seList:
        se = seList[ 0 ]
      try:
        seStatus = self.elementsStatus[ se ][ 'all' ]
      except KeyError:
        seStatus = None

      voStatus = { 'all' : [] }
      for ce in sitesCEs[ siteName ]:
        if not self.elementsStatus.has_key( ce ):
          continue
        for vo, status in self.elementsStatus[ ce ].items():
          if vo not in voStatus:
            voStatus[ vo ] = []
          voStatus[ vo ].append( status )
          
      for vo, ceStatusList in voStatus.items():
        if ceStatusList == [] and seStatus == None:
          continue
        res = self.statusEvaluator.evaluateSiteStatus( siteName, ceStatusList, seStatus, vo = vo, lastCheckTime = lastCheckTime)
        if not res[ 'OK' ]:
          gLogger.error( 'StatusEvaluator.evaluateSiteStatus: %s' % res[ 'Message' ] )
          break
        
    return S_OK()


  def _execute( self, elementDict ):
    elementName = elementDict[ 'ElementName' ]
    vos = elementDict.get( 'VO' ) or []
    utcNow = datetime.utcnow().replace( microsecond = 0 )

    testRes = self.testExecutor.execute( elementDict, lastCheckTime = utcNow )
    if not testRes[ 'OK' ]:
      gLogger.error( 'TestExecutor.execute: %s' % testRes[ 'Message' ] )
      return
    testsStatus = testRes[ 'Value' ]
    
    defaultTestsStatus = {}
    voTestsStatus = {}
    for vo in vos:
      voTestsStatus[ vo ] = {}
    for testType, status in testsStatus.items():
      vo = self.tests[ testType ][ 'match' ].get( 'VO' )
      if not vo:
        defaultTestsStatus[ testType ] = status
      else:
        voTestsStatus[ vo ][ testType ] = status
    
    elementStatus = {}
    self.elementsStatus[ elementName ] = elementStatus

    res = self.statusEvaluator.evaluateResourceStatus( elementDict, testsStatus, lastCheckTime = utcNow )
    if not res[ 'OK' ]:
      gLogger.error( 'StatusEvaluator.evaluateResourceStatus: %s' % res[ 'Message' ] )
      return
    elementStatus[ 'all' ] = res[ 'Value' ]

    for vo, statuses in voTestsStatus.items():
      statuses.update( defaultTestsStatus )
      res = self.statusEvaluator.evaluateResourceStatus( elementDict, statuses, vo = vo, lastCheckTime = utcNow )
      if not res[ 'OK' ]:
        gLogger.error( 'StatusEvaluator.evaluateResourceStatus: %s' % res[ 'Message' ] )
        return
      elementStatus[ vo ] = res[ 'Value' ]


  def __loadTestObj(self):
    _module_pre = 'DIRAC.ResourceStatusSystem.SAM.SAMTest.'

    for testType, testDict in self.tests.items():
      moduleName = testDict[ 'module' ]
      args = testDict.get( 'args', {} )
      args.update( testDict[ 'match' ] )
      args[ 'TestType' ] = testType
      try:
        testModule = Utils.voimport( _module_pre + moduleName )
      except ImportError, e:
        gLogger.error( "Unable to import %s, %s" % ( _module_pre + moduleName, e ) )
        continue
      testClass = getattr( testModule, moduleName )
      obj = testClass(args, self.apis)
      testDict[ 'object' ] = obj

