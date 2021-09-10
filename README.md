# py-thermotec-aeroflow-flexismart
Python Library to communicate with the Thermotec AeroFlow® FlexiSmart Gateway

## Disclaimer:
This is completly a private / community project and is __NOT__ related to the Company [`Thermotec AG`](https://thermotec.ag) in any way!<br>
Use this Library / Client on your __own risk__. I am __NOT__ responsible for any __damage, data loss, error or malfunction!__

## Why this Project
When i got my Thermotec AeroFlow® heater i was quite pleased by the product, but i figured out that the `FlexiSmart Gateway` module was not quite "smart" (atleast not in the way i would think of "smart").

Why do i think it's not smart?
There are only 2 ways of communication with the Gateway:
- The APP for the SmartPhone (Android / iOS)
- Alexa Skill

There are some nice features already build into the Heater itself. Like automatic window open detection.

__BUT__ i have Door / Window sensors at every Door / Window, so i would like to directly control the heater and stop heating as long as the window(s) are open.

Or i want to go automatically in the anti freeze mode if i'm not in the area of my house.

There are many many many reasons why i want an API / Client / Direct way to communicate with the Gateway / Heater directly from my own network.

My Setup is based on [HASS (Home Assistant)](https://home-assistant.io), so i created this library / client project as a dependency for the hassio-integration.

## Features
- All* functions which are available in the APP
  - Holiday Mode and Programming is currently not implemented

- Temperature
  - Read Current Temperature
  - Read Target Temperature
  - Set Target Temperature
- Window Open Detection
  - Read current Status
  - Enable / Disable
- Anti-Freeze
  - Read current value
  - Set target Temperature
- Smart-Start
  - Read current status
  - Enable / Disable
- Temperature Offset
  - Read current value
  - Set value
- Boost
  - Read if Boost is active
  - Set Boost
- Restart
  - Reastart the Heater
- Register Heater
- Zone
  - List Zones
    - With Heater Count
  - Add Zone
  - Delete Zone (delete heaters in zone)
- Get Heater Firmware information
- Gateway Information
  - Read Network settings
  - Date / Time
    - Read
    - Update
  - Read Firmware
  - Read Installation Information
  - Read external Severer endpoints
- Ping
  - Custom implementation to see if the Gateway is available

Most Features are available for the whole Zone or for a specific Heater independently

### Special features (which are not available in the APP)
- Controll each Heater independently or the whole Zone
  - specific Heater works even if in a zone with multiple Heaters 
- Enable Boost


## How to use
You need the IP adress of your Gateway
- Use the APP (If you have the APP and you are in your local Network)
  - Open the APP -> Click on Configuration / Information
    - There you have your IP
- Use your Router / DHCP Server to find the IP

Require this Repository in your Project and use the Commands defined in the commands class

Provide the IP to the function
If your port is different then the default (6653), you can specify the port next to the ip in the function parameter


## How does it work / Restrictions
- Communication via UDP
- Direct communication in the Local Network
- Internet is not necessary
  - i personally have blocked the Gateway from accessing the Internet
- Complete Async approach
- Commands are build as functions to make it easy to use
- APP etc. still works
  - no side effects of using this project beside the official App
  - there might be more "sync" requests in the app, if you change zones

## ToDo
- add command to set Programing
- add command for holiday mode
- slow down the client to fix the: commands send to fast issue ( find pefect delay or set 0.1s )
- add some more DTOs for some objects
- add limits to some commands
  - eg. max temperature, etc. 


## Known issues
- Commands send to fast
  - if you issue the commands to fast, either the UDP-Client gets confused when reciving the responses or the Gateway has issues answering the requests correctly.
    - You might get the wrong response for your command. Sometimes the second command would have the same response as the first command.
  - How to solve this:
    - Maybe add a delay of 0.1 seconds
- FlexiSmart Gateway: Subnet is always 255.255.255.0
  - This is unrelated to this Project, but maybe interesting to know


## Note
Any Trademark, Name or Product is only referenced, but this project does not hold any of these.

- AeroFlow® is the Registered Trademark by [Thermotec AG](https://thermotec.ag)
- [Thermotec AG](https://thermotec.ag) is the Name of the Company behind the Heater and the Gateway
- FlexiSmart is the Product Type / Line of the Gateway / Heater
