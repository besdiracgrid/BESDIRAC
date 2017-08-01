""" ResourceManagementDB

  ResourceManagementDB for BESDIRAC.
  
"""

from DIRAC import S_OK
from DIRAC.ResourceStatusSystem.DB.ResourceManagementDB import ResourceManagementDB as DIRACResourceManagementClient

__RCSID__ = '$Id: $'

class ResourceManagementDB( DIRACResourceManagementClient ):
  """
    ResourceManagementDB inherits from DIRAC's ResourceManagementDB.
  """

  _tablesDB = DIRACResourceManagementClient._tablesDB
  _tablesLike = DIRACResourceManagementClient._tablesLike
  _likeToTable = DIRACResourceManagementClient._likeToTable

  _tablesDB[ 'StorageCache' ] = { 'Fields' :
                                 {
                                  'SE'            : 'VARCHAR(64) NOT NULL',
                                  'Occupied'      : 'BIGINT UNSIGNED NOT NULL DEFAULT 0',
                                  'Free'          : 'BIGINT UNSIGNED NOT NULL DEFAULT 0',
                                  'Usage'         : 'DOUBLE NOT NULL DEFAULT 0.0',
                                  'LastCheckTime' : 'DATETIME NOT NULL'
                                  },
                                 'PrimaryKey' : [ 'SE' ]
                                 }

  _tablesDB[ 'JobCache' ] = { 'Fields' :
                      {
                       'Site'          : 'VARCHAR(64) NOT NULL',
                       'MaskStatus'    : 'VARCHAR(32) NOT NULL',
                       'Efficiency'    : 'DOUBLE NOT NULL DEFAULT 0',
                       'Running'       : 'INTEGER NOT NULL DEFAULT 0',
                       'Waiting'       : 'INTEGER NOT NULL DEFAULT 0',
                       'Done'          : 'INTEGER NOT NULL DEFAULT 0',
                       'Failed'        : 'INTEGER NOT NULL DEFAULT 0',
                       'Completed'     : 'INTEGER NOT NULL DEFAULT 0',
                       'Stalled'       : 'INTEGER NOT NULL DEFAULT 0 ',
                       'Status'        : 'VARCHAR(16) NOT NULL',
                       'LastCheckTime' : 'DATETIME NOT NULL'
                      },
                      'PrimaryKey' : [ 'Site' ]
                                }

  _tablesDB[ 'WorkNodeCache' ] = { 'Fields' :
                              {
                               'Host'          : 'VARCHAR(32) NOT NULL',
                               'Site'          : 'VARCHAR(32) NOT NULL',
                               'Done'          : 'INTEGER NOT NULL DEFAULT 0',
                               'Failed'        : 'INTEGER NOT NULL DEFAULT 0',
                               'Efficiency'    : 'DOUBLE NOT NULL DEFAULT 0.0',
                               'LastCheckTime' : 'DATETIME NOT NULL'
                               },
                              'PrimaryKey' : [ 'Host' ]
                              }

  _tablesDB[ 'SAMResult' ] = { 'Fields' :
                     {
                       'ElementName'     : 'VARCHAR(64) NOT NULL',
                       'TestType'        : 'VARCHAR(16) NOT NULL',
                       'ElementType'     : 'VARCHAR(16) NOT NULL',
                       'Status'          : 'VARCHAR(8) NOT NULL',
                       'Log'             : 'MEDIUMTEXT NOT NULL',
                       'JobID'           : 'INTEGER NOT NULL',
                       'SubmissionTime'  : 'DATETIME NOT NULL',
                       'CompletionTime'  : 'DATETIME NOT NULL DEFAULT "0000-0-0"',
                       'ApplicationTime' : 'DOUBLE NOT NULL DEFAULT 0',
                       'LastCheckTime'   : 'DATETIME NOT NULL'
                     },
                     'PrimaryKey' : [ 'ElementName' , 'TestType' ]
                                }

  _tablesDB[ 'ResourceSAMStatus' ] = { 'Fields' :
                     {
                       'VO'            : 'VARCHAR(8) NOT NULL', 
                       'ElementName'   : 'VARCHAR(64) NOT NULL',
                       'ElementType'   : 'VARCHAR(16) NOT NULL',
                       'Tests'         : 'VARCHAR(256) NOT NULL DEFAULT ""',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'VO', 'ElementName' ]
                                }

  _tablesDB[ 'SiteSAMStatus' ] = { 'Fields' :
                     {
                       'VO'            : 'VARCHAR(8) NOT NULL',
                       'Site'          : 'VARCHAR(32) NOT NULL',
                       'SiteType'      : 'VARCHAR(8) NOT NULL',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'CEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'SEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'VO', 'Site' ]
                                }

  _tablesLike[ 'SAMResultWithID' ] = { 'Fields' :
                     {
                       'ID'              : 'BIGINT UNSIGNED AUTO_INCREMENT NOT NULL',
                       'ElementName'     : 'VARCHAR(64) NOT NULL',
                       'TestType'        : 'VARCHAR(16) NOT NULL',
                       'ElementType'     : 'VARCHAR(16) NOT NULL',
                       'Status'          : 'VARCHAR(8) NOT NULL',
                       'Log'             : 'MEDIUMTEXT NOT NULL',
                       'JobID'           : 'INTEGER NOT NULL',
                       'SubmissionTime'  : 'DATETIME NOT NULL',
                       'CompletionTime'  : 'DATETIME NOT NULL DEFAULT "0000-0-0"',
                       'ApplicationTime' : 'DOUBLE NOT NULL DEFAULT 0',
                       'LastCheckTime'   : 'DATETIME NOT NULL'
                     },
                     'PrimaryKey' : [ 'ID' ]
                                }

  _tablesLike[ 'ResourceSAMStatusWithID' ] = { 'Fields' :
                     {
                       'ID'            : 'BIGINT UNSIGNED AUTO_INCREMENT NOT NULL',
                       'VO'            : 'VARCHAR(8) NOT NULL',
                       'ElementName'   : 'VARCHAR(64) NOT NULL',
                       'ElementType'   : 'VARCHAR(16) NOT NULL',
                       'Tests'         : 'VARCHAR(256) NOT NULL DEFAULT ""',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'ID' ]
                                }

  _tablesLike[ 'SiteSAMStatusWithID' ] = { 'Fields' :
                     {
                       'ID'            : 'BIGINT UNSIGNED AUTO_INCREMENT NOT NULL',
                       'VO'            : 'VARCHAR(8) NOT NULL',
                       'Site'          : 'VARCHAR(32) NOT NULL',
                       'SiteType'      : 'VARCHAR(8) NOT NULL',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'CEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'SEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'ID' ]
                                }

  _likeToTable.update( {
                   'SAMResultLog'             : 'SAMResultWithID',
                   'ResourceSAMStatusLog'     : 'ResourceSAMStatusWithID',
                   'SiteSAMStatusLog'         : 'SiteSAMStatusWithID',
                  } )
  
  
  def _logRecord( self, params, meta, isUpdate ):
    '''
      Method that records every change on a LogTable.
    '''
    
    tables = [ 'PolicyResult', 'SAMResult', 
                       'ResourceSAMStatus', 'SiteSAMStatus' ]
    if not ( 'table' in meta and meta[ 'table' ] in tables ):
      return S_OK()
        
    if isUpdate:
      
      updateRes = self.select( params, meta )
      if not updateRes[ 'OK' ]:
        return updateRes
                    
      params = dict( zip( updateRes[ 'Columns' ], updateRes[ 'Value' ][ 0 ] )) 

    meta[ 'table' ] += 'Log'

    logRes = self.insert( params, meta )
    
    return logRes

