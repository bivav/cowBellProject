# test BLE Scanning software
# jcs 6/8/2014

import blescan
import sys
import datetime
from datetime import timedelta
from tinydb import TinyDB, Query
from dateutil.parser import parse

import bluetooth._bluetooth as bluez

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)
db = TinyDB('scanData.json')
beaconQuery = Query()

while True:
	returnedList = blescan.parse_events(sock, 10)
	print "----------"
	beaconNumList = {}
	currentTime = datetime.datetime.now()
	lastTime = ""
	for i in returnedList:
		beaconId = i.split(",")[1]
		beaconPower = i.split(",")[5]
		if beaconId not in beaconNumList.keys():
			beaconNumList[beaconId] = [beaconPower]
		else:
			beaconNumList[beaconId].append(beaconPower)
	print "fullList : ", beaconNumList
	for i in beaconNumList.keys():
		if any(int(j) > -75 for j in beaconNumList[i]):
			print "after 75 : ", i
			temp = db.search(beaconQuery.beaconId == i)
			if temp:
				lastTime = parse(temp[-1]['date'])
				timeDiff = currentTime - lastTime
				if timeDiff > timedelta(seconds = 30):
					db.insert({'beaconId': i, 'date': str(currentTime), 'counter':temp[-1]['counter'] + 1})
				else:
					db.insert({'beaconId': i, 'date': str(currentTime), 'counter':temp[-1]['counter']})
			else:
				db.insert({'beaconId': i, 'date': str(currentTime), 'counter':1})
