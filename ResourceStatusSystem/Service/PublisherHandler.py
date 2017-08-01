# $HeadURL $
""" PublisherHandler

  PublisherHandler for BESDIRAC

"""

import  math
from datetime import datetime, timedelta
from types    import NoneType

# DIRAC
from DIRAC                                                      import gLogger, S_OK, gConfig, S_ERROR
from DIRAC.ResourceStatusSystem.Utilities                       import CSHelpers
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.ResourceStatusSystem.Client.ResourceStatusClient import ResourceStatusClient
from DIRAC.ResourceStatusSystem.Service.PublisherHandler import PublisherHandler as DIRACPublisherHandler
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient
from BESDIRAC.ResourceStatusSystem.Utilities import BESUtils

__RCSID__ = '$Id: $'

# RSS Clients
rsClient = None
rmClient = None

def initializePublisherHandler(_serviceInfo):
  """
  Handler initialization in the usual horrible way.
  """

  from DIRAC.ResourceStatusSystem.Service import PublisherHandler
  PublisherHandler.initializePublisherHandler(_serviceInfo)
  global rsClient
  rsClient = ResourceStatusClient() 
  global rmClient 
  rmClient = ResourceManagementClient()
  
  return S_OK()
  
class PublisherHandler(DIRACPublisherHandler):
  """
  PublisherHandler inherits from DIRAC's PublisherHandler.
  """  

  def __init__(self, *args, **kwargs):
    """
    Constructor
    """
    super(PublisherHandler, self).__init__(*args, **kwargs)
  
  # My Methods ...................................................
  
  types_getVOs = []
  def export_getVOs(self):
    """
    Returns the list of all VOs.
    """
    
    gLogger.info('getVOs')
    
    return Registry.getVOs()

  types_getVOByGroup = [ str ]
  def export_getVOByGroup(self, group):
    """
    Returns the vo which the group belongs to.
    """
  
    gLogger.info('getVOByGroup')
    
    return S_OK(Registry.getVOMSVOForGroup(group))

  types_getDomains = []
  def export_getDomains(self):
    """
    Returns the list of all site domains.
    """
    
    gLogger.info('getDomains')
    
    return gConfig.getSections('Resources/Sites')

  types_getDomainSites = [ str ]
  def export_getDomainSites(self, domain):
    """
    Returns the list of sites under the specified domain. 
    """
  
    gLogger.info('getDomainSites')
  
    return gConfig.getSections('Resources/Sites/' + domain)
  
  types_getComputingElements = []
  def export_getComputingElements(self):
    """
    Returns the list of all CEs.
    """
    
    gLogger.info('getComputingElements')
    
    return CSHelpers.getComputingElements()

  types_getStorageElements = []
  def export_getStorageElements(self):
    """
    Returns the list of all SEs.
    """
    
    gLogger.info('getStorageElements')
    
    return CSHelpers.getStorageElements()
  
  types_getSiteVO = [ str ]
  def export_getSiteVO(self, siteName):
    """
    Returns the VO for the given site.
    """

    gLogger.info('getSiteVO')

    vos = BESUtils.getSiteVO( siteName )
    return S_OK( vos )
  
  types_getSiteResource = [ str ]
  def export_getSiteResource(self, siteName):
    """
    Returns the dictionary with CEs and SEs for the given site.
    
    :return: S_OK( { 'ComputingElement' : celist, 'StorageElement' : selist } ) | S_ERROR
    """
    
    gLogger.info('getSiteResource')
    
    siteType = siteName.split('.')[ 0 ]
      
    if siteType == 'CLOUD':
      ces = []
    else:
      ces = CSHelpers.getSiteComputingElements(siteName)
          
    ses = CSHelpers.getSiteStorageElements(siteName)
      
    return S_OK({ 'ComputingElement' : ces, 'StorageElement' : ses })
  
  types_getSitesSAMSummary = [  (str, NoneType, list), (str, NoneType, list) ]
  def export_getSitesSAMSummary(self, sitesName, vo = None):
    """
    Return the dictionary with SAM summary information for the given sites.
    
    :return: S_OK( { site : { 'CEStatus' : 'OK'
                                                   'SEStatus' : 'Bad'
                                                   } } ) | S_ERROR
    """
    
    gLogger.info('getSitesSAMSummary')
    
    sitesSAMSummary = {}

    vo = vo or 'all'
    queryRes = rmClient.selectSiteSAMStatus(site = sitesName, vO = vo,
                                            meta = { 'newer' : [ 'LastCheckTime', 
                                                                datetime.utcnow().replace(microsecond = 0) - timedelta(hours = 24) ] })
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]
    
    for record in records:
      recordDict = dict(zip(columns, record))
      siteName = recordDict[ 'Site' ]
      sitesSAMSummary[ siteName ] = { 'CEStatus' : recordDict[ 'CEStatus' ], 'SEStatus' : recordDict[ 'SEStatus' ] }
      
    return S_OK(sitesSAMSummary)
      
  types_getSitesStorageSummary = [ (str, NoneType, list) ]
  def export_getSitesStorageSummary(self, sitesName):
    """
    Return the dictionary with storage summary information for the given sites.
    
    :return: S_OK( { site : { 'MaxStorage' :  1000.00
                                                   'FreeStorage' :  200.00
                                                   'StorageUsage' : 80.0
                                                   } } ) | S_ERROR
    """
    
    gLogger.info('getSitesStorageSummary')
    
    sitesStorageSummary = {}
    
    ses = set()
    for siteName in sitesName:
      se = CSHelpers.getSiteStorageElements(siteName)
      if se:
        sitesStorageSummary[ siteName ] = se[ 0 ]
        ses.add(se[ 0 ])

    if len(ses) == 0:
      return S_OK(sitesStorageSummary)
   
    queryRes = rmClient.selectStorageCache(sE = list(ses))
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]
    
    seInfo = {}
    for record in records:
      recordDict = dict(zip(columns, record))
      seName = recordDict.pop('SE')
      seDict = {}
      seDict[ 'MaxStorage' ] = math.floor(float(recordDict[ 'Occupied' ] + recordDict[ 'Free' ]) / 1024 / 1024 / 1024 * 100) / 100
      seDict[ 'FreeStorage' ] = math.floor(float(recordDict[ 'Free' ]) / 1024 / 1024 / 1024 * 100) / 100
      seDict[ 'StorageUsage' ] = recordDict[ 'Usage' ]
      seInfo[ seName ] = seDict
      
    for siteName, seName in sitesStorageSummary.items():
      sitesStorageSummary[ siteName ] = seInfo[ seName ]
      
    return S_OK(sitesStorageSummary)
      
  types_getSitesJobSummary = [ (str, NoneType, list) ]
  def export_getSitesJobSummary(self, sitesName):
    """
    Return the dictionary with job summary information for the given sites.
    
    :return: S_OK( { site : { 'Running' :  222
                                                   'Waiting' :  222
                                                   'Done' : 222
                                                   'Failed' : 222
                                                   'Efficiency' : 50.0
                                                   'MaxJobs' : 666
                                                   'JobUsage' : 33.3
                                                   } } ) | S_ERROR
    """
    
    gLogger.info('getSitesJobSummary')
    
    sitesJobSummary = {}
    
    queryRes = rmClient.selectJobCache(site = sitesName)
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]
    
    for record in records:
      recordDict = dict(zip(columns, record))
      siteName = recordDict[ 'Site' ]
      jobDict = {}
      jobDict[ 'Running' ] = recordDict[ 'Running' ]
      jobDict[ 'Waiting' ] = recordDict[ 'Waiting' ]
      jobDict[ 'Done' ] = recordDict[ 'Done' ]
      jobDict[ 'Failed' ] = recordDict[ 'Failed' ]
      jobDict[ 'Efficiency' ] = recordDict[ 'Efficiency' ]
      sitesJobSummary[ siteName ] = jobDict
      
    siteMaxJobs = self.__getSitesMaxJobs(sitesName)
    if not siteMaxJobs[ 'OK' ]:
      return siteMaxJobs
    siteMaxJobs = siteMaxJobs[ 'Value' ]
    
    for siteName, jobDict in sitesJobSummary.items():
      maxJobs =  siteMaxJobs.get(siteName)
      if maxJobs:
        jobDict[ 'MaxJobs' ] = maxJobs
        jobDict[ 'JobUsage' ] = math.floor(float(jobDict[ 'Running' ]) / maxJobs * 1000) / 10
      else:
        jobDict[ 'MaxJobs' ] = ''
        jobDict[ 'JobUsage' ] = ''
      
    return S_OK(sitesJobSummary)
      
  types_getSitesWNSummary = [ (str, NoneType, list) ]
  def export_getSitesWNSummary(self, sitesName):
    """
    Return the dictionary with work node summary information for the given sites.
    
    :return: S_OK( { site : { 'WNStatus' :  'OK'
                                                   } } ) | S_ERROR
    """
    
    gLogger.info('getSitesWNSummary')
    
    sitesWNSummary = {}
    
    queryRes = rmClient.selectWorkNodeCache(site = sitesName)
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]
    
    wnsEfficiency = {}
    for record in records:
      recordDict = dict( zip( columns, record ) )
      site = recordDict[ 'Site' ]
      if site not in wnsEfficiency:
        wnsEfficiency[ site ] = []
      wnsEfficiency[site ].append( recordDict[ 'Efficiency' ] )
      
    for site, efficiencyList in wnsEfficiency.items():
      if len(efficiencyList) != 0:
        rate = float( efficiencyList.count( 0 ) ) / len( efficiencyList )
        if rate == 0:
          status = 'OK'
        elif rate > 0.5:
          status = 'Bad'
        else:
          status = 'Warn'
        sitesWNSummary[ site ] = { 'WNStatus' : status }
        
    return S_OK( sitesWNSummary )
  
  types_getSiteWNsInfo = [ str ]
  def export_getSiteWNsInfo(self, siteName):
    """
    Retruns the jobs statistics for hosts of the given site. 
    
    :return: S_OK( [ { 'Host' : 'aaa.bb.ccc'
                                        'Running' : 1
                                        'Done' : 22
                                        'Failed' : 22
                                        'Efficiency' : 50.0
                                        } ] ) / S_ERROR
    """
    
    gLogger.info('getSiteWNsInfo')
      
    queryRes = rmClient.selectWorkNodeCache(site = siteName, 
                                       meta = { 'columns' : [ 'Host', 'Done', 'Failed', 'Efficiency' ] })
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]
    
    results = []
    for record in records:
      results.append(dict(zip( columns, record )))
    
    return S_OK(results)
     
  types_getSAMDetail = [ str, str ]
  def export_getSAMDetail(self, elementName, testType):
    """
    Returns the dictionary with SAM test detail information for the given test.
    """
    
    gLogger.info('getSAMDetail')
    
    queryRes = rmClient.selectSAMResult(elementName=elementName, testType=testType)
    if not queryRes[ 'OK' ]:
      return queryRes
    record = queryRes[ 'Value' ][ 0 ]
    columns = queryRes[ 'Columns' ]
      
    detail = dict(zip(columns, record))
    detail.pop('LastCheckTime')
    return S_OK(detail)
      
  types_getSAMSummary = [ str, str ]
  def export_getSAMSummary(self, siteName, vo):
    """
    Returns SAM tests status for the elements of the given site.
    
    :return: S_OK( { element : { 'ElementType' :
                                                            'WMSTest' : 
                                                            'CVMFSTest' : 
                                                            'BOSSTest' :
                                                            'SETest' : } } ) / S_ERROR
    
    """
    
    gLogger.info('getSAMSummary')

    siteType = siteName.split('.')[ 0 ]
    if 'CLOUD' == siteType:
      ces = [ siteName ]
    else:
      ces = CSHelpers.getSiteComputingElements(siteName)
    ses = CSHelpers.getSiteStorageElements(siteName)

    samSummary = {}
    for ce in ces:
      samSummary[ ce ] = { 'ElementType' : 'ComputingElement' }
    for se in ses:
      samSummary[ se ] = { 'ElementType' : 'StorageElement' }

    lastCheckTime = datetime.utcnow().replace(microsecond = 0) - timedelta(hours = 24)

    queryRes = rmClient.selectResourceSAMStatus(elementName = ces, vO = vo,
                                                meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] })
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]

    if ses != []:
      queryRes = rmClient.selectResourceSAMStatus(elementName = ses,
                                                  meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] })
      if not queryRes[ 'OK' ]:
        return queryRes
      records += queryRes[ 'Value' ]

    for record in records:
      samDict = dict(zip(columns, record))
      elementName = samDict[ 'ElementName' ]
      samSummary[ elementName ][ 'Status' ] = samDict[ 'Status' ]
      tests = [ test.strip() for test in samDict[ 'Tests' ].split(',') ]
      queryRes = rmClient.selectSAMResult(elementName = elementName, testType = tests,
                                          meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] })
      if not queryRes[ 'OK' ]:
        return queryRes
      testRecords = queryRes[ 'Value' ]
      testColumns = queryRes[ 'Columns' ]
      for testRecord in testRecords:
        testDict = dict(zip(testColumns, testRecord))
        samSummary[ elementName ][ testDict[ 'TestType' ] ] = testDict[ 'Status' ]

    return S_OK(samSummary)
  
  def __getSitesMaxJobs(self, sites):
    sitesMaxJobs = {}
    
    for site in sites:
      domain = site.split('.')[ 0 ]
      
      if domain == 'CLOUD':
        _basePath = 'Resources/VirtualMachines/CloudEndpoints'
        endpoints = gConfig.getSections(_basePath)
        if not endpoints[ 'OK' ]:
          return endpoints
        endpoints = endpoints[ 'Value' ]
        for endpoint in endpoints:
          siteName = gConfig.getValue('%s/%s/siteName' % ( _basePath, endpoint ))
          if site == siteName:
            maxJobs = gConfig.getValue('%s/%s/maxEndpointInstances' % ( _basePath, endpoint ), 0)
            sitesMaxJobs[ site ] = maxJobs
            break
    
      else:
        maxJobs = 0
        _basePath = 'Resources/Sites'
        ces = gConfig.getSections('%s/%s/%s/CEs' % (_basePath, domain, site))
        if not ces[ 'OK' ]:
          return ces
        ces = ces[ 'Value' ]
        for ce in ces:
          queues = gConfig.getSections('%s/%s/%s/CEs/%s/Queues' % (_basePath, domain, site, ce))
          if not queues[ 'OK' ]:
            return queues
          queues = queues[ 'Value' ]
          for queue in queues:
            maxJobs += gConfig.getValue('%s/%s/%s/CEs/%s/Queues/%s/MaxTotalJobs' % (_basePath, domain, site, ce, queue), 0)
        sitesMaxJobs[ site ] = maxJobs
      
    return S_OK(sitesMaxJobs)
      
  types_getTestHistory = [ str, str, datetime, datetime]
  def export_getTestHistory(self, elementType, element, fromDate, toDate):
    gLogger.info('getTestHistory')
    
    if fromDate > toDate:
      return S_ERROR('from date can not be after the to date.')
  
    selectElements = []
    if elementType == 'Site':  
      if element.split('.')[ 0 ] == 'CLOUD':
        selectElements.append( element )
      else:
        selectElements += CSHelpers.getSiteComputingElements(element)
      selectElements += CSHelpers.getSiteStorageElements(element)
    else:
      selectElements = [ element ]
        
    queryRes = rmClient.selectSAMResultLog(
                                           elementName = selectElements,
                                           meta = { 'newer' : ['LastCheckTime', fromDate ],
                                                   'older' : [ 'LastCheckTime', toDate ],
                                                   'columns' : [ 'ElementName', 'TestType', 'Status', 'LastCheckTime' ] }
                                           )
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    
    testHistory = {}
    for record in records:
      key = record[ 0 ] + '-' + record[ 1 ]
      if key not in testHistory:
        testHistory[ key ] = []
      testHistory[ key ].append(( record[ 3 ], record[ 2 ] ))
    
    return S_OK(testHistory)

  types_getResourceStatusHistory = [ (str, NoneType, list), str, datetime, datetime ]
  def export_getResourceStatusHistory(self, resources, vo, fromDate, toDate):
    gLogger.info('getResourceStatusHistory')
    
    if fromDate > toDate:
      return S_ERROR('from date can not be after the to date.')
  
    queryRes = rmClient.selectResourceSAMStatusLog(
                                                   elementName = resources, vO = vo,
                                                   meta = { 'newer' : ['LastCheckTime', fromDate ],
                                                           'older' : [ 'LastCheckTime', toDate ],
                                                           'columns' : [ 'ElementName', 'Status', 'LastCheckTime' ] }
                                                   )
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    
    statusHistory = {}
    for record in records:
      res = record[ 0 ]
      if res not in statusHistory:
        statusHistory[ res ] = []
      statusHistory[ res ].append(( record[ 2 ], record[ 1 ] ))
      
    return S_OK(statusHistory)
    
  types_getSiteStatusHistory = [ (str, NoneType, list), str, datetime, datetime ]
  def export_getSiteStatusHistory(self, sites, vo, fromDate, toDate):
    gLogger.info('getSiteStatusHistory')
    
    if fromDate > toDate:
      return S_ERROR('from date can not be after the to date.')
  
    queryRes = rmClient.selectSiteSAMStatusLog(
                                               site = sites, vO = vo,
                                               meta = { 'newer' : ['LastCheckTime', fromDate ],
                                                       'older' : [ 'LastCheckTime', toDate ],
                                                       'columns' : [ 'Site', 'Status', 'LastCheckTime' ] }
                                                   )
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]
    
    statusHistory = {}
    for record in records:
      site = record[ 0 ]
      if site not in statusHistory:
        statusHistory[ site ] = []
      statusHistory[ site ].append(( record[ 2 ], record[ 1 ] ))
      
    return S_OK(statusHistory)
    
# ...............................................................................
# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF

