#!/usr/bin/env python

import keyring, sys, time, verdict

# To store the password, run this from an interactive python session:
# import keyring; keyring.set_password(SSID, 'psk', 'mysecret')
SSID = 'RedFelineNetwork'
PASSWD = keyring.get_password(SSID, 'psk')
if not PASSWD:
	print 'No password for ' +  SSID
	sys.exit(1)

def run(args=[]):
	#console = verdict.netcat('hazel', 5002)
	console = verdict.serial('/dev/ttyUSB0')

	# Check we have a command prompt
	console.sendline('')
	console.expect('root.*# ')

	# Check we can see the router
	console.sendline('nmcli dev wifi list')
	console.expect(SSID)
	console.expect('root.*# ')

	# Change the hostname to avoid collisions with other 96Boards and
	# ensure NetworkManager is restarted and observes the change.
	console.sendline('sed -ie s/linaro-developer/hikey/ /etc/hostname')
	console.expect('root.*# ')
	console.sendline('hostname dragonboard')
	console.expect('root.*# ')
	console.sendline('exit')
	console.expect('root.*# ')
	console.sendline('systemctl restart NetworkManager\n')
	console.expect('root.*# ')

	# Wait for the SSID to detect the network
	for i in range(20):
		console.sendline('nmcli dev wifi list')
		m = console.expect([SSID, 'root.*# '])
		if m == 0:
			console.expect('root.*# ')
			break
		time.sleep(1)

	# Setup the connection (using network manager makes it durable
	# through reboot cycles).
	console.sendline('nmcli dev wifi con "{}" password "{}" name "Home"'.format(SSID, PASSWD))
	console.expect('Connection with UUID .* created and activated on device')
	console.expect('root.*# ')

	# The next set of commands are network based commands and might 
	# have unpredictable runtimes
	verdict.expect_slow_replies(console)

	console.sendline('apt-get update')
	console.expect('Reading package lists')
	console.expect('root.*# ')

	console.sendline('apt-get install -y mosh')
	console.expect('Reading package lists')
	console.expect('Unpacking mosh')
	console.expect('Setting up mosh')
	console.expect('root.*# ')
	
	verdict.good(cleanup=(console,))

if __name__ == '__main__':
        run(sys.argv[1:])
