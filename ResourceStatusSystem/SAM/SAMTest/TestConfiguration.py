
TESTS = {

  'Access-Test' :
  {
    'module' : 'AccessTest',
    'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD', 'StorageElement' ) },
    'args' : { 'timeout' : 5 }
  },

  'WMS-Test' :
  {
    'module' : 'WMSTest',
    'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD' ) },
    'args' : { 'executable' : 'wms_test.py', 'timeout' : 2400 }
  },

  'CVMFS-Test' :
  {
    'module' : 'CVMFSTest',
    'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD' ), 'VO' : 'bes' },
    'args' : { 'executable' : 'cvmfs_test.py', 'timeout' : 2400 }
  },

  'BOSS-Test' :
  {
    'module' : 'BOSSTest',
    'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD' ), 'VO' : 'bes' },
    'args' : { 'executable' : 'boss_test.py', 'timeout' : 2400 }
  },

  'CEPC-Test' :
  {
    'module' : 'CEPCTest',
    'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD' ), 'VO' : 'cepc' },
    'args' : { 'executable' : 'cepc_test.py', 'timeout' : 2400 }
  },

  'JUNO-Test':
  {
   'module' : 'JUNOTest',
   'match' : { 'ElementType' : ( 'ComputingElement', 'CLOUD' ), 'VO' : 'juno' },
   'args' : { 'executable' : 'juno_test.py', 'timeout' : 2400 }
  },

  'SE-Test' :
  {
    'module' : 'SETest',
    'match' : { 'ElementType' : ( 'StorageElement', ) }
  },

}
