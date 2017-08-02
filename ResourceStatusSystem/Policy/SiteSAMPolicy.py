from DIRAC                                              import S_OK
from DIRAC.ResourceStatusSystem.PolicySystem.PolicyBase import PolicyBase

__RCSID__ = '$Id:  $'

class SiteSAMPolicy( PolicyBase ):

  @staticmethod
  def _evaluate( commandResult ):
    result = {
              'Status' : None,
              'Reason' : None
              }

    if not commandResult[ 'OK' ]:
      result[ 'Status' ] = 'Error'
      result[ 'Reason' ] = commandResult[ 'Message' ]
      return S_OK( result )

    commandResult = commandResult[ 'Value' ]

    if not commandResult:
      result[ 'Status' ] = 'Unknown'
      result[ 'Reason' ] = 'No sam result to take a decision'
      return S_OK( result )

    status = {}
    for res in commandResult:
      status[ res[ 'VO' ] ] = { 'Status' : res[ 'Status' ], 'CEStatus' : res[ 'CEStatus' ], 'SEStatus' : res[ 'SEStatus' ] }

    if status[ 'all' ][ 'Status' ] == 'OK' or status[ 'all' ][ 'Status' ] == 'Busy':
      result[ 'Status' ] = 'Active'
      result[ 'Reason' ] = 'Site SAM status is %s' % status[ 'all' ][ 'Status' ]
    elif status[ 'all' ][ 'Status' ]  == 'Unknown':
      result[ 'Status' ] = 'Degraded'
      proVOs = []
      for vo, statusDict in status.items():
        if vo != 'all' and statusDict[ 'CEStatus' ] == 'Unknown':
          proVOs.append( vo )
      proVOs = ', '.join( proVOs )
      result[ 'Reason' ] = 'CEs could have some problems running the %s jobs' % proVOs
    else:
      if status[ 'all' ][ 'CEStatus' ] == 'Bad':
        fineVOsCount = 0
        proVOs = []
        for vo, statusDict in status.items():
          if vo != 'all':
            if statusDict[ 'CEStatus' ] == 'Bad':
              proVOs.append( vo )
            else:
              fineVOsCount += 1
        if fineVOsCount == 0:
          result[ 'Status' ] = 'Banned'
          result[ 'Reason' ] = 'CEs have some problems'
        else:
          result[ 'Status' ] = 'Degraded'
          result[ 'Reason' ] = 'CEs can not run the %s jobs properly' % proVOs
        proVOs = ', '.join( proVOs )
      else:
        result[ 'Status' ] = 'Degraded'
        result[ 'Reason' ] = 'SE has some problems'

    return S_OK( result )
