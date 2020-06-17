# BT-LinkkeySync
Script to synchronize bluetooth link keys from macOS to windows.
It generates a registry file for windows on macOS, which can afterwards be imported with the tool regedit in windows.

## Instructions
1. Pair all your bluetooth devices to your Mac (e.g. keyboard, mouse, headphones)
2. Open the Terminal and navigate to the folder where you have downloaded the file`BT-Linkkeysync.py`
3. Run the script with `./BT-Linkkeysync.py`(you will be asked for your password)
4. Store the generated file `btkeys.reg` file to a location accessible by windows.
5. Import the file `btkeys.reg`
6. No need to reboot
7. Use your keyboard on macOS and Windows

## Information
Test Environment:

* MacBook Pro 11,5 (mid 2015)
* macOS Catalina 10.15.5
* Windows 10 Prof
* Python 3.8

Tested Devices:

* JBL Flip 3 SE
* Sony WH-1000XM3
* Apple Magic Mouse
* Hilti Radio Charger

## Limitations
BT 4.0 LE/Smart Devices (e.g. Logitech MX Master) do not work yet.
If you know how to get it working feel free to contribute :)

## TODO's
Try the other way round (Pair on Windows and import in macOS) maybe get Bluetooth 4.0 LE Working

## Credits
Related [Blog Post on InsanelyMac](http://www.insanelymac.com/forum/topic/268837-dual-boot-bluetooth-pairing-solved/) of camoguy

## Links
* [Dual Boot Bluetooth Pairing Solved](http://www.insanelymac.com/forum/topic/268837-dual-boot-bluetooth-pairing-solved/)
* [Dual pairing in OS X and Windows](https://discussions.apple.com/thread/3113227?start=0&tstart=0)
* [OS-X-Bluetooth-Pairing-Value-To-Windows-Value](https://github.com/Soorma07/OS-X-Bluetooth-Pairing-Value-To-Windows-Value)
