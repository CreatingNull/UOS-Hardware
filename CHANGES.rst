Version 0.5.0
-------------

:Date: TBC

* BREAKING! Remaps address for redesign of UOS protocol.
  Restructured GPIO packets to suit the redesign.
* PEP 484 implicit optional typing fixes.
* Redesigned the logging to be more suitable for a library.
  A global logger is configured at the top level and used throughout
  the project.
  The logger has a NullHandler so is suppressed unless the client enables.
  Removed configure_logs function as this was no longer functional.
* Updating reset_all_io to use persistence levels pertaining to where the
  reset details are obtained from.
* Enabling volatile instructions on arduino devices as this is now
  available at the firmware level.

Version 0.4.0
-------------

:Date: 30-October-2022

* Adding gpio_input case for testing lookup of compatible pins.
* Setting ``frozen=True`` for static abstraction dataclasses,
  this is for hash-ability. This change was required for 3.11
  support due to the
  `dataclass changes <https://github.com/python/cpython/issues/88840>`_.
* Device definitions are shifted into private modules within a
  devices packages. The intended API avoids having to be aware of this
  complexity.
* Correcting a mistake in the arduino_nano device definition.
  This had 9x pins defined where only 8x exist on this device.
* Redesigning the analog and digital pins to define aliases where
  they physically are the same pin.
* Removing interrupt and bus information from Pin definitions as
  this wasn't implemented and likely would need a redesign if it was
  added.
* Defining the arduino uno as a separate device to the nano.
  Functionally these are equivalent besides the fewer ADC inputs
  on the uno.

Version 0.3.0
-------------

:Date: 25-September-2022

* Allowing the UOSDevice interface to be used as a context manager.
* Adding an is_active function to UOSDevice as a method to indicate
  if a connection is held open with the device.
* Refactored devices lookup to use importable constant names rather
  than a dictionary.
* Removing use of success booleans in low level interface packages
  / abstractions in preference of more descriptive errors.
* Refactored loading type to be a defined keyword argument that
  uses a enum value rather than an ambiguous string. This removes
  the is_lazy function as this information should be directly taken
  from the ``UOSDevice.loading`` class variable.
* Fixed a bug where using LAZY loading without a context manager could
  cause connection lockups.
* Fixed a bug where pylint was incorrectly defined as a project dep
  rather than a dev dep.

Version 0.2.1
-------------

:Date: 18-September-2022

* Fixing a bug with the serial backend where DTR reset workaround on
  linux platforms. Opening the serial connection was defining encoding
  as binary rather than the mode.

Version 0.2.0
-------------

:Date: 18-September-2022

* Major refactoring to device handling and top-level UOS schema
  definitions. This is to improve OOP consistency across the project
  and reduce reliance on string name lookup.
* Drop support for python 3.9 in preference of clean typing.

Version 0.1.1
-------------

:Date: 7-August-2022

* Including additional documentation in published build.

Version 0.1.0
-------------

:Date: 7-August-2022

* Initial release of the redesigned API.
