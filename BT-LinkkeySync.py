#!/usr/bin/env python3

import plistlib
import os
import platform
import subprocess
import binascii
import json
#import winreg

# function which is used to do the byte swapping and insert commas
def convertToWinRep(s):
	return ",".join(map(str.__add__, s[0::2] ,s[1::2]))

def reverseEndian(key):
	return "".join(map(str.__add__, key[-2::-2] ,key[-1::-2]))

def writeRegFile():
	# open the file where we write the registry information
	f = open(filename, 'w')
	# registry file header
	f.write("Windows Registry Editor Version 5.00\r\n")
	for adapter in keydict:
		f.write('\r\n[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\'+adapter+']')
		for device in keydict[adapter]:
			if type (keydict[adapter][device]) is dict:
				pass
			else:
				f.write('\r\n"'+device+'"=hex:'+ convertToWinRep(keydict[adapter][device]))

	for adapter in keydict:
		for device in keydict[adapter]:
			if type (keydict[adapter][device]) is dict:
				f.write('\r\n\r\n[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\BTHPORT\\Parameters\\Keys\\'+adapter+'\\'+device+']')
				f.write('\r\n"LTK"=hex:'+ convertToWinRep(keydict[adapter][device]["LTK"]))
				f.write('\r\n"KeyLength"=dword:'+ keydict[adapter][device]["KeyLength"])
				f.write('\r\n"ERand"=hex(b):'+ convertToWinRep(keydict[adapter][device]["RAND"]))
				f.write('\r\n"EDIV"=dword:'+ keydict[adapter][device]["EDIV"])
				f.write('\r\n"IRK"=hex:'+ convertToWinRep(keydict[adapter][device]["IRK"]))
				f.write('\r\n"Address"=hex(b):'+ convertToWinRep(keydict[adapter][device]["DeviceAddress"]))
				f.write('\r\n"AddressType"=dword:'+ keydict[adapter][device]["AddressType"])
	f.close()

def writeKeyFile():
	f = open(keyfilename, 'w')
	f.write(json.dumps(keydict))
	f.close()

def readKeyFile():
	f = open(keyfilename)
	keydict =  json.loads(f)
	f.close()

# function to handle the macOS side of things
def darwin(mode):
	if mode == 'read':
		print("reading Bluetooth Link Keys from macOS, please enter your password")
		if darwinVersion <= 16:						# Darwin 16 is Sierra
			blued = subprocess.check_output("sudo defaults export blued -", shell=True)					# exporting in xml directly to stdin
		else:
			blued = subprocess.check_output("sudo defaults export com.apple.bluetoothd -", shell=True)	# exporting in xml directly to stdin

		print("parsing the plist")
		pl = plistlib.loads(blued)
		print("converting the Link Keys and storing them to " + keyfilename + "\r\n")

		# loop over all avialable Bluetooth 2.0 adapters
		if "LinkKeys" in pl:
			print("Bluetooth :\t"+str(len(pl["LinkKeys"].keys()))+ " adapter/s found")
			for adapter in pl["LinkKeys"].keys():
				if adapter.replace("-","") in keydict:
					pass
				else:
					keydict[adapter.replace("-","")] = {}
				# loop over all available devices of this adapter
				for device in pl["LinkKeys"][adapter].keys():
					keydict[adapter.replace("-","")][device.replace("-","")] = reverseEndian(binascii.hexlify(pl["LinkKeys"][adapter][device]).decode("ascii"))
		else:
			print("No Bluetooth 2.0 information available")


		# loop over all Bluetooth 4.0 LE adapters
		if "SMPDistributionKeys" in pl:
			print("Bluetooth LE:\t"+str(len(pl["SMPDistributionKeys"].keys()))+ " adapter/s found\r\n")
			for adapter in pl["SMPDistributionKeys"].keys():
				if adapter.replace("-","") in keydict:
					pass
				else:
					keydict[adapter.replace("-","")] = {}
				# loop over all available devices of this adapter
				for device in pl["SMPDistributionKeys"][adapter].keys():

					if device.replace("-","") in keydict[adapter.replace("-","")]:
						pass
					else:
						keydict[adapter.replace("-","")][device.replace("-","")] = {}
					# Lonk-Term Key (LTK)
					# 128-bit key used to generate the session key for an encrypted connection.
					keydict[adapter.replace("-","")][device.replace("-","")]["LTK"] = reverseEndian((binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["LTK"]).decode("ascii")))

					#dev += '\r"KeyLength"=dword:00000000' # Don't know why this is zero when i pair my BT LE Mouse with windows.
					keydict[adapter.replace("-","")][device.replace("-","")]["KeyLength"] = (binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["LTKLength"]).decode("ascii")).rjust(8,'0')

					# Random Number (RAND):
					# 64-bit stored value used to identify the LTK. A new RAND is generated each time a unique LTK is distributed.
					keydict[adapter.replace("-","")][device.replace("-","")]["RAND"] = reverseEndian(binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["RAND"]).decode("ascii"))

					# Encrypted Diversifier (EDIV)
					# 16-bit stored value used to identify the LTK. A new EDIV is generated each time a new LTK is distributed.
					keydict[adapter.replace("-","")][device.replace("-","")]["EDIV"] = (binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["EDIV"]).decode("ascii")).rjust(8,'0')

					# Identity Resolving Key (IRK)
					# 128-bit key used to generate and resolve random address.
					keydict[adapter.replace("-","")][device.replace("-","")]["IRK"] = reverseEndian(binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["IRK"]).decode("ascii"))

					# Device Address
					# 48-bit Address of the connected device
					keydict[adapter.replace("-","")][device.replace("-","")]["DeviceAddress"] = reverseEndian((binascii.hexlify(pl["SMPDistributionKeys"][adapter][device]["Address"]).decode("ascii")).rjust(16,'0'))

					# Don't know whats that, i'm using an Logitech MX Master, and this is written to the registry when i pair it to windows
					keydict[adapter.replace("-","")][device.replace("-","")]["AddressType"] = str(pl["SMPDistributionKeys"][adapter][device]["AddressType"]).rjust(8,'0')

					# Connection Signature Resolving Key (CSRK)
					# 128-bit key used to sign data and verify signatures on the receiving device.
					# Info: CSRK is not stored on the OSX side.
					# It seems to be a temporary key which is only needed during the first bundling of the devices. After that, only the LTK is used.
		else:
			print("No Bluetooth 4.0 information available")
		writeRegFile()
		writeKeyFile()
		print("Registry file generated and ready for import")
		return
	elif mode == 'write':
		print("TODO: do some key writing here")
		return
	else:
		print("no mode specified")
		return

def windows(mode):
	if mode == 'read':
		print("TODO: do some key reading here")
		return
	elif mode == 'write':
		print("TODO: do some key writing here")
		return
	else:
		print("no mode specified")
		return

def linux(mode):
	if mode == 'read':
		print("TODO: do some key reading here")
		return
	elif mode == 'write':
		print("TODO: do some key writing here")
		return
	else:
		print("no mode specified")
		return

# main execution body:

print("-------------------------------------------------")
print("  BT-Linkkeysync by DigitalBird & Broeckelmaier")
print("-------------------------------------------------")

# file where the registry info shall be stored
filename = 'btkeys.reg'
keyfilename = 'keys.json'
keydict = {}

#check if there is already a keyfile present and if so read the stored keys

if os.path.exists('keys.json'):
	print("there is already a keyfile.")
	mode = input("would you like to 'read' a new one, or 'write' the containing keys?\r\n")
else:
	mode = 'read'

if platform.system() == 'Darwin':			# check if we're running a Darwin kernel, otherwise exit
	darwinVersion=platform.release()		# get the system version
	darwinVersion=darwinVersion.split(".")	# split the string
	darwinVersion=int(darwinVersion[0])		# set the major versionnumber
	darwin(mode)
elif platform.system() == 'Windows':
	windows(mode)
elif platform.system() == 'Linux':
	linux(mode)
else:
	print("I'm sorry, but it seems you're running a operating system I'm not able to handle")
	sys.exit()
