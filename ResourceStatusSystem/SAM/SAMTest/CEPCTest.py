""" JUNOTest

  A test class to test the software for the vo cepc.

"""

from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEBaseTest import CEBaseTest


__RCSID__ = '$Id: $'


class CEPCTest( CEBaseTest ):
  """
    JUNOTest is used to test whether the cepc's software is fine to run jobs.
  """

  def __init__( self, args = None, apis = None ):
    super( CEPCTest, self ).__init__( args, apis )


  @staticmethod
  def _judge( log ):
    idx = log.find( 'Job Done.' )
    if idx != -1:
      return 'OK'
    else:
      return 'Bad'
