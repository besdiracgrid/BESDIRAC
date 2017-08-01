""" CVMFSTest

  A test class to test CVMFS is ok or not.
  
"""


from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEBaseTest import CEBaseTest


__RCSID__ = '$Id: $'


class CVMFSTest( CEBaseTest ):
  """
    CVMFSTest is used  to test whether CVMFS is fine to run jobs.
  """
    
  def __init__( self, args = None, apis = None ):
    super( CVMFSTest, self ).__init__( args, apis )

    
  @staticmethod
  def _judge( log ):
    """
      judge the CVMFS test status.
    """
    
    if log.find( 'Standard Error' ) != -1:
      return 'Bad'
    else:
      return 'OK'
