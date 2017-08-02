""" JUNOTest

  A test class to test the software for the vo juno.

"""

from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEBaseTest import CEBaseTest


__RCSID__ = '$Id: $'


class JUNOTest( CEBaseTest ):
  """
    JUNOTest is used to test whether the juno's software is fine to run jobs.
  """

  def __init__( self, args = None, apis = None ):
    super( JUNOTest, self ).__init__( args, apis )


  @staticmethod
  def _judge( log ):
    idx = log.find( '***  SNiPER Terminated Successfully!  ***' )
    if idx != -1:
      return 'OK'
    else:
      return 'Bad'
