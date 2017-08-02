""" TestBase

  Base class for all tests.

"""

import threading
from abc   import ABCMeta,abstractmethod


__RCSID__ = '$Id:  $'

LOCK = threading.Lock()


class TestBase( object ):
  """
    TestBase is a simple base class for all tests. Real test classes should
    implement its doTest and getTestResult method.
  """

  __metaclass__ = ABCMeta

  def __init__( self, args = None, apis = None ):
    self.apis = apis or {}
    self.args = args or {}


  @abstractmethod
  def doTest( self, elementDict ):
    """
      to be extended by real tests.
    """

    return None
