from datetime import datetime, timedelta
from DIRAC import S_OK, S_ERROR
from DIRAC.ResourceStatusSystem.Command.Command                 import Command
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient

__RCSID__ = '$Id:  $'

class SAMCommand( Command ):

  def __init__( self, args = None, clients = None ):

    super( SAMCommand, self ).__init__( args, clients )

    if 'ResourceManagementClient' in self.apis:
      self.rmClient = self.apis[ 'ResourceManagementClient' ]
    else:
      self.rmClient = ResourceManagementClient()


  def doCommand( self ):
    element = self.args[ 'element' ]
    elementName = self.args[ 'name' ]

    lastCheckTime = datetime.utcnow().replace(microsecond = 0) - timedelta(hours = 24)

    if element == 'Site':
      queryRes = self.rmClient.selectSiteSAMStatus( site = elementName,
                                                    meta = { 'newer' : [ 'LastCheckTime', lastCheckTime ] } )
    elif element == 'Resource':
      queryRes = self.rmClient.selectResourceSAMStatus( elementName = elementName,
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

