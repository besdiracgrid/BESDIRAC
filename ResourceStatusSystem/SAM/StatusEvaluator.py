""" StatusEvaluator

  StatusEvaluator is used to evaluate elements' SAM status depending on the
  SAM tests results. The SAM status includes resource SAM status and site SAM
  status. Firstly, integrate tests results and get resource SAM status. Then judge
  site SAM status depending on the status of resources which belong to the site.
"""

from datetime import datetime
from DIRAC                                                         import S_OK, S_ERROR
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient import ResourceManagementIHEPClient


__RCSID__ = '$Id:  $'


class StatusEvaluator(object):
  """ StatusEvaluator
  """

  def __init__(self, apis):
    """ Constructor

    examples:
      >>> sites = { 'CLUSTER' : [ 'CLUSTER.USTC.cn' ],
                              'GRID' : [ 'GRID.JINR.ru' ],
                              'CLOUD' : [ ''CLOUD.IHEP-OPENSTACK.cn' ] }
      >>> evaluator = StatusEvaluator( sites )

    :Parameters:
       **sites** - `dict`
         the sites to evaluate SAM status. The sites is grouped by domain.
    """

    if "ResourceManagementIHEPClient" in apis:
      self.rmClient = apis[ "ResourceManagementIHEPClient" ]
    else:
      self.rmClient = ResourceManagementIHEPClient()


  def __storeResourceStatus( self, resDict ):
    storeRes = self.rmClient.addOrModifyResourceSAMStatus(
                                                          resDict[ 'VO' ],
                                                          resDict[ 'ElementName' ],
                                                          resDict[ 'ElementType' ],
                                                          resDict[ 'Tests' ],
                                                          resDict[ 'Status' ],
                                                          resDict[ 'LastCheckTime' ]
                                                          )
    if not storeRes[ 'OK' ]:
      return storeRes
    return S_OK()


  def __storeSiteStatus( self, resDict ):
    storeRes = self.rmClient.addOrModifySiteSAMStatus(
                                                      resDict[ 'VO' ],
                                                      resDict[ 'Site' ],
                                                      resDict[ 'SiteType' ],
                                                      resDict[ 'Status' ],
                                                      resDict[ 'CEStatus' ],
                                                      resDict[ 'SEStatus' ],
                                                      resDict[ 'LastCheckTime' ]
                                                      )
    if not storeRes[ 'OK' ]:
      return storeRes
    return S_OK()


  def __resourceStatusRule( self, statusList ):
    if 'Bad' in statusList:
      return 'Bad'
    if 'Unknown' in statusList:
      return 'Unknown'
    if 'Busy' in statusList:
      return 'Busy'
    if 'OK' in statusList:
      return 'OK'
    return ''


  def __siteStatusRule( self, ceStatusList, seStatus ):
    if 'OK' in ceStatusList:
      ceStatus = 'OK'
    elif 'Busy' in ceStatusList:
      ceStatus = 'Busy'
    elif 'Bad' in ceStatusList:
      ceStatus = 'Bad'
    else:
      ceStatus = 'Unknown'

    if not seStatus:
      status = ceStatus
    else:
      if 'Bad' == seStatus:
        status = 'Bad'
      else:
        status = ceStatus

    return ( status, ceStatus, seStatus )


  def evaluateResourceStatus( self, elementDict, testResults, vo = None, lastCheckTime = None ):
    vo = vo or 'all'
    lastCheckTime = lastCheckTime or datetime.utcnow().replace( microsecond = 0 )
    elementName = elementDict[ 'ElementName' ]
    elementType = elementDict[ 'ElementType' ]
    tests = ','.join( testResults.keys() )
    status = self.__resourceStatusRule( testResults.values() )

    resDict = { 'ElementName' : elementName,
                        'VO' : vo,
                        'ElementType' : elementType,
                        'Tests' : tests,
                        'Status' : status,
                        'LastCheckTime' : lastCheckTime }

    storeRes = self.__storeResourceStatus( resDict )
    if not storeRes[ 'OK' ]:
      return S_ERROR( 'Failed to store resource SAM status.' )
    return S_OK( status )


  def evaluateSiteStatus( self, site, ceStatusList, seStatus = None, vo = None, lastCheckTime = None ):
    vo = vo or 'all'
    lastCheckTime = lastCheckTime or datetime.utcnow().replace( microsecond = 0 )
    siteType = site.split( '.' )[ 0 ]
    status, ceStatus, seStatus = self.__siteStatusRule( ceStatusList, seStatus )

    resDict = { 'Site' : site,
                         'VO' : vo,
                         'SiteType' : siteType,
                         'Status' : status,
                         'CEStatus' : ceStatus,
                         'SEStatus' : seStatus,
                         'LastCheckTime' : lastCheckTime }

    storeRes = self.__storeSiteStatus( resDict )
    if not storeRes[ 'OK' ]:
      S_ERROR( 'Failed to store site SAM status.' )
    return S_OK( status )
