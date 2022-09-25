Version 0.3.0
-------------

:Date: TBC

* Allowing the UOSDevice interface to be used as a context manager.
* Adding an is_active function to UOSDevice as a method to indicate if a connection is held open with the device.
* Refactored devices lookup to use importable constant names rather than a dictionary.
* Removing use of success booleans in low level interface packages / abstractions in preference of more descriptive errors.
* Refactored loading type to be a defined keyword argument that uses a enum value rather than an ambiguous string.
  This removes the is_lazy function as this information should be directly taken from the `UOSDevice.loading` class variable.
* Fixed a bug where using LAZY loading without a context manager could cause connection lockups.
* Fixed a bug where pylint was incorrectly defined as a project dep rather than a dev dep.

Version 0.2.1
-------------

:Date: 18-September-2022

* Fixing a bug with the serial backend where DTR reset workaround on linux platforms.
  Opening the serial connection was defining encoding as binary rather than the mode.

Version 0.2.0
-------------

:Date: 18-September-2022

* Major refactoring to device handling and top-level UOS schema definitions.
  This is to improve OOP consistency across the project and reduce reliance on string name lookup.
* Drop support for python 3.9 in preference of clean typing.

Version 0.1.1
-------------

:Date: 7-August-2022

* Including additional documentation in published build.

Version 0.1.0
-------------

:Date: 7-August-2022

* Initial release of the redesigned API.
