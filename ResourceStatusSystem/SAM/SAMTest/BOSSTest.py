""" BOSSTest

  A test class to test BOSS is ok or not.
  
"""

from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEBaseTest import CEBaseTest


__RCSID__ = '$Id: $'


class BOSSTest( CEBaseTest ):
  """
    BOSSTest is used to test whether BOSS is fine to run jobs.
  """
    
  def __init__( self, args = None, apis = None ):
    super( BOSSTest, self ).__init__( args, apis )

    
  @staticmethod
  def _judge( log ):
    """
      judge the BOSS test status.
    """
    
    dry = []
    lines = log.split( '\n' )
    for line in lines:
      line = line.split( ' ', 1 )
      if line[ 0 ] in [ 'DstHltMaker', 'ApplicationMgr' ]:
        line[ 1 ] = line[ 1 ].strip()
        dry.append( line )
                
    applicationMgrSuccess = 0
    dstHltMakerSuccess = 0
    expectedApplicationMng = 'INFO Application Manager Terminated successfully' 
    expectedDstHltMaker = 'SUCCESS 50 events are converted.'
    for i in dry:
      if i[ 0 ] == 'ApplicationMgr' and i[ 1 ] == expectedApplicationMng:
        applicationMgrSuccess += 1
      if i[ 0 ] == 'DstHltMaker' and i[ 1 ] == expectedDstHltMaker:
        dstHltMakerSuccess += 1
    if applicationMgrSuccess == 2 and dstHltMakerSuccess == 1:
      return 'OK' 
    return 'Bad'
