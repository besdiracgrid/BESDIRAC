""" ResourceManagementIHEPDB

  ResourceManagementIHEPDB for BESDIRAC.

"""

from datetime                             import datetime

from DIRAC                                import S_OK, S_ERROR
from DIRAC.Core.Base.DB                   import DB
from BESDIRAC.ResourceStatusSystem.Utilities import MySQLWrapper

__RCSID__ = '$Id: $'

class ResourceManagementIHEPDB( object ):
  """
    Class that defines the tables for the ResourceManagementIHEPDB on a python dictionary.
  """

  # Written PrimaryKey as list on purpose !!
  _tablesDB = {}
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
#                       'CompletionTime'  : 'DATETIME NOT NULL DEFAULT "0000-00-00"',
                       'CompletionTime'  : 'DATETIME NOT NULL',
                       'ApplicationTime' : 'DOUBLE NOT NULL DEFAULT 0',
                       'LastCheckTime'   : 'DATETIME NOT NULL'
                     },
                     'PrimaryKey' : [ 'ElementName' , 'TestType' ]
                                }

  _tablesDB[ 'ResourceSAMStatus' ] = { 'Fields' :
                     {
                       'VO'            : 'VARCHAR(32) NOT NULL',
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
                       'VO'            : 'VARCHAR(32) NOT NULL',
                       'Site'          : 'VARCHAR(32) NOT NULL',
                       'SiteType'      : 'VARCHAR(8) NOT NULL',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'CEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'SEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'VO', 'Site' ]
                                }

  _tablesLike  = {}
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
#                       'CompletionTime'  : 'DATETIME NOT NULL DEFAULT "0000-00-00"',
                       'CompletionTime'  : 'DATETIME NOT NULL',
                       'ApplicationTime' : 'DOUBLE NOT NULL DEFAULT 0',
                       'LastCheckTime'   : 'DATETIME NOT NULL'
                     },
                     'PrimaryKey' : [ 'ID' ]
                                }

  _tablesLike[ 'ResourceSAMStatusWithID' ] = { 'Fields' :
                     {
                       'ID'            : 'BIGINT UNSIGNED AUTO_INCREMENT NOT NULL',
                       'VO'            : 'VARCHAR(32) NOT NULL',
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
                       'VO'            : 'VARCHAR(32) NOT NULL',
                       'Site'          : 'VARCHAR(32) NOT NULL',
                       'SiteType'      : 'VARCHAR(8) NOT NULL',
                       'Status'        : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'CEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'SEStatus'      : 'VARCHAR(8) NOT NULL DEFAULT ""',
                       'LastCheckTime' : 'DATETIME NOT NULL',
                     },
                     'PrimaryKey' : [ 'ID' ]
                                }

  _likeToTable = {
                   'SAMResultLog'             : 'SAMResultWithID',
                   'ResourceSAMStatusLog'     : 'ResourceSAMStatusWithID',
                   'SiteSAMStatusLog'         : 'SiteSAMStatusWithID',
                  }


  def __init__( self, mySQL = None ):
    '''
      Constructor, accepts any DB or mySQL connection, mostly used for testing
      purposes.
    '''
    self._tableDict = self.__generateTables()

    if mySQL is not None:
      self.database = mySQL
    else:
      self.database = DB( 'ResourceManagementIHEPDB',
                          'ResourceStatus/ResourceManagementIHEPDB' )

  ## SQL Methods ###############################################################

  def insert( self, params, meta ):
    '''
    Inserts args in the DB making use of kwargs where parameters such as
    the 'table' are specified ( filled automatically by the Client). Typically you
    will not pass kwargs to this function, unless you know what are you doing
    and you have a very special use case.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''

    utcnow = datetime.utcnow().replace( microsecond = 0 )

    # We force lastCheckTime to utcnow if it is not present on the params
    #if not( 'lastCheckTime' in params and not( params[ 'lastCheckTime' ] is None ) ):
    if 'lastCheckTime' in params and params[ 'lastCheckTime' ] is None:
      params[ 'lastCheckTime' ] = utcnow

    if 'dateEffective' in params and params[ 'dateEffective' ] is None:
      params[ 'dateEffective' ] = utcnow

    return MySQLWrapper.insert( self, params, meta )

  def update( self, params, meta ):
    '''
    Updates row with values given on args. The row selection is done using the
    default of MySQLMonkey ( column.primary or column.keyColumn ). It can be
    modified using kwargs. The 'table' keyword argument is mandatory, and
    filled automatically by the Client. Typically you will not pass kwargs to
    this function, unless you know what are you doing and you have a very
    special use case.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''

    # We force lastCheckTime to utcnow if it is not present on the params
    #if not( 'lastCheckTime' in params and not( params[ 'lastCheckTime' ] is None ) ):
    if 'lastCheckTime' in params and params[ 'lastCheckTime' ] is None:
      params[ 'lastCheckTime' ] = datetime.utcnow().replace( microsecond = 0 )

    return MySQLWrapper.update( self, params, meta )

  def select( self, params, meta ):
    '''
    Uses arguments to build conditional SQL statement ( WHERE ... ). If the
    sql statement desired is more complex, you can use kwargs to interact with
    the MySQL buildCondition parser and generate a more sophisticated query.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''
    return MySQLWrapper.select( self, params, meta )

  def delete( self, params, meta ):
    """
    Uses arguments to build conditional SQL statement ( WHERE ... ). If the
    sql statement desired is more complex, you can use kwargs to interact with
    the MySQL buildCondition parser and generate a more sophisticated query.
    There is only one forbidden query, with all parameters None ( this would
    mean a query of the type DELETE * from TableName ). The usage of kwargs
    is the same as in the get function.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    """
    return MySQLWrapper.delete( self, params, meta )

  ## Extended SQL methods ######################################################

  def addOrModify( self, params, meta ):
    '''
    Using the PrimaryKeys of the table, it looks for the record in the database.
    If it is there, it is updated, if not, it is inserted as a new entry.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''

    selectQuery = self.select( params, meta )
    if not selectQuery[ 'OK' ]:
      return selectQuery

    isUpdate = False

    if selectQuery[ 'Value' ]:

      # Pseudo - code
      # for all column not being PrimaryKey and not a time column:
      #   if one or more column different than params if not None:
      #     we update dateTime as well

      columns = selectQuery[ 'Columns' ]
      values  = selectQuery[ 'Value' ]

      if len( values ) != 1:
        return S_ERROR( 'More than one value returned on addOrModify, please report !!' )

      selectDict = dict( zip( columns, values[ 0 ] ) )

      newDateEffective = None

      for key, value in params.items():
        if key in ( 'lastCheckTime', 'dateEffective' ):
          continue

        if value is None:
          continue

        if value != selectDict[ key[0].upper() + key[1:] ]:
          newDateEffective = datetime.utcnow().replace( microsecond = 0 )
          break

      if 'dateEffective' in params:
        params[ 'dateEffective' ] = newDateEffective

      userQuery = self.update( params, meta )
      isUpdate  = True

    else:
      userQuery = self.insert( params, meta )

    # This part only applies to PolicyResult table
    logResult = self._logRecord( params, meta, isUpdate )
    if not logResult[ 'OK' ]:
      return logResult

    return userQuery

  # FIXME: this method looks unused. Maybe can be removed from the code.
  def addIfNotThere( self, params, meta ):
    '''
    Using the PrimaryKeys of the table, it looks for the record in the database.
    If it is not there, it is inserted as a new entry.

    :Parameters:
      **params** - `dict`
        arguments for the mysql query ( must match table columns ! ).

      **meta** - `dict`
        metadata for the mysql query. It must contain, at least, `table` key
        with the proper table name.

    :return: S_OK() || S_ERROR()
    '''

    selectQuery = self.select( params, meta )
    if not selectQuery[ 'OK' ]:
      return selectQuery

    if selectQuery[ 'Value' ]:
      return selectQuery

    return self.insert( params, meta )

  ## Auxiliar methods ##########################################################

  def getTable( self, tableName ):
    '''
      Returns a table dictionary description given its name
    '''
    if tableName in self._tableDict:
      return S_OK( self._tableDict[ tableName ] )

    return S_ERROR( '%s is not on the schema' % tableName )

  def getTablesList( self ):
    '''
      Returns a list of the table names in the schema.
    '''
    return S_OK( self._tableDict.keys() )

  ## Protected methods #########################################################

  def _checkTable( self ):
    '''
      Method used by database tools to write the schema
    '''
    return self.__createTables()

  def _logRecord( self, params, meta, isUpdate ):
    '''
      Method that records every change on a LogTable.
    '''

    tables = [ 'SAMResult', 'ResourceSAMStatus', 'SiteSAMStatus' ]
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


  ## Private methods ###########################################################

  def __createTables( self, tableName = None ):
    '''
      Writes the schema in the database. If no tableName is given, all tables
      are written in the database. If a table is already in the schema, it is
      skipped to avoid problems trying to create a table that already exists.
    '''

    # Horrible SQL here !!
    tablesCreatedRes = self.database._query( "show tables" )
    if not tablesCreatedRes[ 'OK' ]:
      return tablesCreatedRes
    tablesCreated = [ tableCreated[0] for tableCreated in tablesCreatedRes[ 'Value' ] ]

    tables = {}
    if tableName is None:
      tables.update( self._tableDict )

    elif tableName in self._tableDict:
      tables = { tableName : self._tableDict[ tableName ] }

    else:
      return S_ERROR( '"%s" is not a known table' % tableName )

    for tableName in tablesCreated:
      if tableName in tables:
        del tables[ tableName ]

    res = self.database._createTables( tables )
    if not res[ 'OK' ]:
      return res

    # Human readable S_OK message
    if res[ 'Value' ] == 0:
      res[ 'Value' ] = 'No tables created'
    else:
      res[ 'Value' ] = 'Tables created: %s' % ( ','.join( tables.keys() ) )
    return res

  def __generateTables( self ):
    '''
      Method used to transform the class variables into instance variables,
      for safety reasons.
    '''

    # Avoids copying object.
    tables = {}
    tables.update( self._tablesDB )

    for tableName, tableLike in self._likeToTable.items():

      tables[ tableName ] = self._tablesLike[ tableLike ]

    return tables

################################################################################
#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF
