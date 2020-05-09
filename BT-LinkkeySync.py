#!/usr/bin/env python3

import plistlib
import os
import platform
import subprocess
import binascii


print("---------------------------------")
print("  BT-Linkkeysync by DigitalBird")
print("---------------------------------")

# file where the registry info shall be stored
filename = 'btkeys.reg'
if platform.system() == 'Darwin':		# check if we're running under Darwin, otherwise exit
	darwinVersion=platform.release()	# get the system version
	darwinVersion=darwinVersion.split(".")
	darwinVersion=int(darwinVersion[0])
else:
	sys.exit()

print("> get Bluetooth Link Keys from macOS")
if darwinVersion <= 16:
	blued = subprocess.check_output("sudo defaults export blued -", shell=True)
else:
	blued = subprocess.check_output("sudo defaults export com.apple.bluetoothd -", shell=True)

print("> parse the converted plist")
pl = plistlib.loads(blued)
# open the file where we write the registry information
f = open(filename, 'w')

# function which is used to do the byte swapping and insert commas
def convertToWinRep(s):
	return ",".join(map(str.__add__, s[-2::-2] ,s[-1::-2]))

print("> Convert the Link Keys and store them to btkeys.reg")
# header for the registry file
f.write("Windows Registry Editor Version 5.00")


# loop over all avialable Bluetooth 2.0 adapters
if "LinkKeys" in pl:
	print("  Bluetooth :\t"+str(len(pl["LinkKeys"].keys()))+ " adapter/s found")
	for adapter in pl["LinkKeys"].keys():
		f.write('\r\n\r\n[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\'+adapter.replace("-","")+"]")

		# loop over all available devices of this adapter
		for device in pl["LinkKeys"][adapter].keys():
			f.write('\r\n"'+device.replace("-","")+'"=hex:'+ convertToWinRep(binascii.hexlify(pl["LinkKeys"][adapter][device]).decode("ascii")))
else:
	print("No Bluetooth 2.0 information available")


# loop over all Bluetooth 4.0 LE adapters
if "SMPDistributionKeys" in pl:
	print("  Bluetooth LE:\t"+str(len(pl["SMPDistributionKeys"].keys()))+ " adapter/s found")
	for adapter in pl["SMPDistributionKeys"].keys():

		# loop over all available devices of this adapter
		for device in pl["SMPDistributionKeys"][adapter].keys():
			dev = '\r\n\r\n[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\'+adapter.replace("-","")+'\\'+device.replace("-","") +"]"

			# Lonk-Term Key (LTK)
			# 128-bit key used to generate the session key for an encrypted connection.
			dev += '\r\n"LTK"=hex:'+ convertToWinRep(binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["LTK"]).decode("ascii"))

			#dev += '\r"KeyLength"=dword:00000000' # Don't know why this is zero when i pair my BT LE Mouse with windows.
			dev += '\r\n"KeyLength"=dword:'+ (binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["LTKLength"]).decode("ascii")).rjust(8,'0')

			# Random Number (RAND):
			# 64-bit stored value used to identify the LTK. A new RAND is generated each time a unique LTK is distributed.
			dev += '\r\n"ERand"=hex(b):'+ convertToWinRep(binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["RAND"]).decode("ascii"))

			# Encrypted Diversifier (EDIV)
			# 16-bit stored value used to identify the LTK. A new EDIV is generated each time a new LTK is distributed.
			dev += '\r\n"EDIV"=dword:'+ (binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["EDIV"]).decode("ascii")).rjust(8,'0')

			# Identity Resolving Key (IRK)
			# 128-bit key used to generate and resolve random address.
			dev += '\r\n"IRK"=hex:'+ convertToWinRep(binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["IRK"]).decode("ascii"))

			# Device Address
			# 48-bit Address of the connected device
			dev += '\r\n"Address"=hex(b):'+ convertToWinRep((binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["Address"]).decode("ascii")).rjust(16,'0'))

			# Don't know whats that, i'm using an Logitech MX Master, and this is written to the registry when i pair it to windows
			dev += '\r\n"AddressType"=dword:00000001'

			# Connection Signature Resolving Key (CSRK)
			# 128-bit key used to sign data and verify signatures on the receiving device.
			# Info: CSRK is not stored on the OSX side.
			# It seems to be a temporary key which is only needed during the first bundling of the devices. After that, only the LTK is used.

			f.write(dev)
else:
	print("No Bluetooth 4.0 information available")

f.close()
print("> Registry file generated and ready for import")
