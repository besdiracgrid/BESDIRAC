BESDIRAC CHANGELOG
==================

v0r17 (2017-08-02)
---------------------

### New Feature
- Transfer accounting web page is added

### Change
- Use DIRAC v6r15
- Database of ResourceStatusIHEPDB for IHEP DIRAC monitoring is separated from
  the DIRAC ResourceStatusDB

v0r16 (2016-09-18)
---------------------

### New Feature
- ResourceStatus for IHEP DIRAC monitoring merged

v0r15 (2016-08-22)
---------------------

### Change
- Use DIRAC v6r15p13 to test UMN SE

v0r14 (2016-08-01)
---------------------

### Change
- Use DIRAC v6r15

v0r13 (2015-10-30)
---------------------

### New Feature
- `besdirac-wms-task-get-output` command for download and merge task files

### Change
- Task job access control method changed

v0r12 (2015-08-09)
---------------------

### New Feature
- `besdirac-wms-task-event-progress` command for getting event progress

### Change
- New version for new DIRAC version v6r13p11
- Change several places for new DIRAC API

### Bug
- Fix bug of empty jobID list when getJobs

v0r11 (2015-06-24)
---------------------

### New Feature
- Web portal for task management system
- A lot of improvement for task management system

### Change
- Put rsync url in CS

v0r10 (2015-05-05)
---------------------

### New Feature
- New task management system

### Bug
- Transfer system: The return of namedtuple._asdict changed from dict to Ordered Dict

v0r9 (2014-08-19)
---------------------
