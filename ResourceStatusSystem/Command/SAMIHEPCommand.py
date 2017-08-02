from datetime import datetime, timedelta
from DIRAC import S_OK, S_ERROR
from DIRAC.ResourceStatusSystem.Command.Command                 import Command
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient import ResourceManagementIHEPClient

__RCSID__ = '$Id:  $'

class SAMIHEPCommand( Command ):

  def __init__( self, args = None, clients = None ):

    super( SAMIHEPCommand, self ).__init__( args, clients )

    if 'ResourceManagementIHEPClient' in self.apis:
      self.rmIHEPClient = self.apis[ 'ResourceManagementIHEPClient' ]
    else:
      self.rmIHEPClient = ResourceManagementClient()


  def doCommand( self ):
    element = self.args[ 'element' ]
    elementName = self.args[ 'name' ]

    lastCheckTime = datetime.utcnow().replace(microsecond = 0) - timedelta(hours = 24)

    if element == 'Site':
      queryRes = self.rmIHEPClient.selectSiteSAMStatus( site = elementName,
                                                    meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] } )
    elif element == 'Resource':
      queryRes = self.rmIHEPClient.selectResourceSAMStatus( elementName = elementName,
                                                        meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] } )
    else:
      return self.returnERROR( S_ERROR('No SAM information for %s element' % element ) )

    if not queryRes[ 'OK' ]:
      return self.returnERROR( queryRes )
    records = queryRes[ 'Value' ]
    columns = queryRes[ 'Columns' ]

    results = []
    for record in records:
      results.append( dict( zip( columns, record ) ) )
    return S_OK( results )

