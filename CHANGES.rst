Version 0.6.0
-------------

:Date: TBC

* Moving ``get_pin`` function to be defined at the UOSDevice level.
  This is a client-facing function and low level devices aren't client-facing.
  Also set ``pin_index`` argument to be ``pin`` so this is more consistent
  with the other API functions.
* ``Device._pins`` un-protected as this was purely to promote use of get_pin.
* ``Device.get_pins`` removed as this is not required if pins is not protected.
* Moving ``get_compatible_pins`` function to be defined at the UOSDevice level.
  This is justified by the same reason as moving the ``get_pin``.
* ``UOSDevice.device`` set protected to avoid confusion and misuse.
  This is primarily for internal use and where it is required for clients
  getter methods such as ``get_pin`` should be provided.
* Removed checks to ``COMResult.exception`` length in internal code as it is
  sufficient to just check ``COMResult.status``.

Version 0.5.0
-------------

:Date: 7-January-2023

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
* Removed volatility from get_adc_input as this doesn't apply to that
  function.
* Removing the concept of separate analog and digital pins.
  If these are distinct then the analog should be aliased as virtual higher
  index pins.
* Fixed a bug where get compatible pins wasn't verifying requirements.
* Removed get gpio config as this functionality is no longer applicable in
  the new UOS design.
* Updated the get_gpio_input interface to allow for enabling pull-up.
* Updated interface execute_instruction prototype to take in a pre-built
  packet rather than all of these needing to build the packet internally.
* Shifted NPC based functionality into an explict class that bundles this.
  ``abstractions.NPCPacket``
* Including the TX packet in the RX response.
  This allows us more freedom to build higher level decoding functions.
* Adding functionality to include ADC and GPIO responses as objects stored
  in the device pins.
* Protected pins dict and instead exposed a ``get_pin`` function on device.
  This allows introspection on pin internals to making usage easier.
* Updated ``get_compatible_pins`` to return a set of pin indices rather
  than a dict of pins. This is to encourage the use of ``get_pin`` OOP.

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
