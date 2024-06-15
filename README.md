# pv-hot-water

Control software for a custom photovoltaic solar hot water setup.  
The system consists of an array of solar panels providing two circuits.
There is an exterior GFCI panel, an interior panel, and a pair of electric
hot water heater tanks converted to DC.  
*This repository is solely for the software component of this system.*

Initially, the software consisted of a large Java program (written in 2020)
running on the Raspberry Pi in the interior panel with a corresponding
Android application that connected with a custom protocol over UDP.  
The old system, while having proven itself to be stable, has numerous
inefficiencies and slow performance.  
This software redesign has similar goals and priorities, being developed
for the same system. The specific improvements over the previous system will
not be documented further than they are above.

## Priorities and Considerations

1. Safety

   While the hardware provides numerous shutoffs and such, the software should also
   continuously monitor the state and conditions of the hardware and detect and
   appropriately respond to as many forseeably possible (though generally unlikely)
   unfavorable circumstances.

2. Stability

   Safety being a priority, as well as operability being important, the value of
   stability can be immediately derived. Due to the nature of the system, updates
   are extremely infrequent. Meanwhile, regardless of technical know-how of
   potential users, the system needs to "just work."  
   The system should be well isolated from potential cyber threats and designed
   to require as little maintenance as possible. Maintenance, such as
   monitoring database size, etc, should be extremely straightforward if required.

3. Ease of use

   As previously mentioned, the system needs to "just work."
   General usage, monitoring, statistics, etc. should be able to be understood
   and used by the layman and engineer alike (as much as possible).  
   There should be an easy user interface to immediately identify
   potential issues, as well as to see and understand handy or
   interesting statistics about the operation of the system.

4. Data collection

   Data should be collected by the physical sensors of the system to evaluate
   saved energy, performance of the solar panels, efficiency of the storage
   within the two tanks, etc.
   This should be easily accessible as previously mentioned and there should
   be a calibration mechanism for most measurements as well.

## Interior Control Panel

The primary control electronics are in the interior panel.

- **Raspberry Pi**, running the main control software
  
  This will act as a thermostat, monitor hardware conditions, provide basic
  information on the panel LCD screen, collect data to store in the database,
  host a Flask web app for a user interface, a Flask RESTful API for the
  web app to use and for an Android app to potentially use.

- **Arduino Nano**, used for its cheap a/d converters and as an i/o buffer

  This will be used as an intermidiary between the raspberry pi and some of the hardware.

- **ESP32**, maintaining a communication link to the exterior GFCI panel

  This will allow communication between the raspberry pi and the GFCI panel
  to allow for turning off the circuits externally and controlling/overseeing the
  ground fault detection.

## External GFCI Panel Hardware

The exterior panel with a circuit breaker and current sensors.

- **Arduino Nano**, running GFCI polling loop
  
  This monitors the current on both sides of each circuit in order to
  detect ground faults and turn off the circuits.

- **ESP32**, maintaining a communication link to the interior panel

  This will allow communication between the raspberry pi and the GFCI panel
  to allow for turning off the circuits externally and controlling/overseeing the
  ground fault detection.
