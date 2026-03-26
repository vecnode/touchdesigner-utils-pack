# Scans the local network for IPs and physical addresses
# Needs arp -a, tested Windows 10, build 19045


def onOffToOn(channel, sampleIndex, val, prev):

	startup_op = op('/project1/startup')
	text_display_op = op('/project1/ig20_iegeekcam/ip_display/text_tex')

	storage = startup_op.module.NetworkInterface()
	storage.devices = startup_op.module.get_arp_table()
	
	this_ip, this_hostname = storage.get_own_details()

	print('This ip is: ', this_ip)
	print('This hostname is: ', this_hostname)

	print('These are scanned devices using arp -a : ', storage.devices)

	formatted_arp_table = startup_op.module.format_arp_table_to_string(storage.devices)

	print('Formatted arp table: ', formatted_arp_table)
	text_display_op.par.text = formatted_arp_table

	return



def whileOn(channel, sampleIndex, val, prev):
	return

def onOnToOff(channel, sampleIndex, val, prev):
	return

def whileOff(channel, sampleIndex, val, prev):
	return

def onValueChange(channel, sampleIndex, val, prev):
	return
	