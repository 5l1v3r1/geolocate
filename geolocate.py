import threading
import requests
import optparse
import time
import json
import sys

parser = optparse.OptionParser('%prog -f file [-o country] [-i city] [-r region]')
parser.add_option('-f', dest='file_name', type='string', help='File to load IPs from')
parser.add_option('-i', dest='city_search', type='string', help='City to search for')
parser.add_option('-o', dest='country_search', type='string', help='Country to search for')
parser.add_option('-r', dest='region_search', type='string', help='Region to search for')
parser.add_option('-l', dest='logging', action='store_true', default=False, help='Log results to file')
(options, args) = parser.parse_args()

global active_threads
global file_name
file_name = ''
active_threads = 0

def logging(ip):
	global file_name
	file_name = 'geolocate'
		
	if options.country_search != None:
		file_name = file_name + '_' + str(options.country_search)
	if options.region_search != None:
		file_name = file_name + '_' + str(options.region_search)
	if options.city_search != None:
		file_name = file_name + '_' + str(options.city_search)

	file_name = file_name + '.txt'

	the_file = open(file_name, 'a')
	the_file.write(ip + '\n')
	the_file.close()

def get_location(full_ip):
	global active_threads
	active_threads = active_threads + 1
	try:
		ip_string, junk = full_ip.split(':')
	except:
		ip_string = full_ip
	send_url = 'https://freegeoip.net/json/' + str(ip_string)
	try:
		r = requests.get(send_url)
		j = json.loads(r.text)
	except:
		print('***************************')
		print('[!] Could not get info -> ' + str(ip_string))		
		active_threads = active_threads - 1
		return

	ip = j['ip']
	city = j['city']
	region = j['region_name']
	country = j['country_name']

	try:
		output = '****************************\n'
		output = output + 'IP      -> ' + str(ip) + '\n'
		output = output + 'Country -> ' + str(country) + '\n'
		output = output + 'Region  -> ' + str(region) + '\n'
		output = output + 'City    -> ' + str(city)


		if (options.city_search != None) or (options.country_search != None) or (options.region_search != None):
			if ((options.city_search == str(city)) and (options.city_search != None)) or ((options.country_search == str(country)) and (options.country_search != None)) or ((options.region_search == str(region)) and (options.region_search != None)):
				print(output)
				if options.logging == True:
					logging(full_ip)
		else:
			print(output)
			if options.logging == True:
				logging(full_ip)
	except:
		active_threads = active_threads - 1
		return

	active_threads = active_threads - 1


def waiter():
	global active_threads
	while active_threads > 0:
		time.sleep(0.1)

try:
	if options.logging == True:
		print('[!] Logging: True')
	if options.file_name != None:
		with open(str(options.file_name)) as f:
			lines = f.readlines()
	
		for line in lines:
			entry = line
#			get_location(entry.replace('\n', ''))
			t = threading.Thread(target = get_location, args=(entry.replace('\n', ''),))
			t.daemon = True
			t.start()
			time.sleep(0.1)

		waiter()

		print('[!] Complete')
		if options.logging == True:
			print('[!] Results saved to ' + str(file_name))
	else:
		print('[!] Check usage')
except KeyboardInterrupt:
	print('\n\n[!] Exiting...\n')
	if options.logging == True:
		print('[!] Results saved to ' + str(file_name))
	sys.exit()
