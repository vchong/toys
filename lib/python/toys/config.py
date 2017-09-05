'''
A not-actually-general-purpose-at-all configuration manager.
'''

import configparser
import getpass
import os
import sys

# Import keyring, suppressing any warnings from gi when we do so
try:
	import gi
	gi.require_version('GnomeKeyring', '1.0')
except:
	pass
import keyring

def get_config():
	'''Open (or create) a config file.'''
	filename = os.environ['HOME'] + os.sep + '.linaro_toys'

	cfg = configparser.ConfigParser()
	try:
		cfg.read(filename)
	except:
		pass

	if 'zendesk' not in cfg:
		cfg['zendesk'] = {}
	zendesk_orig = dict(cfg['zendesk'])
	if 'server' not in cfg['zendesk']:
		cfg['zendesk']['server'] = 'https://linaro.zendesk.com'
	if 'username' not in cfg['zendesk']:
		cfg['zendesk']['username'] = 'daniel.thompson@linaro.org'

	if 'jira' not in cfg:
		cfg['jira'] = {}
	jira_orig = dict(cfg['jira'])
	if 'server' not in cfg['jira']:
		cfg['jira']['server'] = 'https://projects.linaro.org'
	if 'username' not in cfg['jira']:
		cfg['jira']['username'] = 'daniel.thompson@linaro.org'

	if '96btool' not in cfg:
		cfg['96btool'] = {}
	l96btool_orig = dict(cfg['96btool'])
	if 'server' not in cfg['96btool']:
		cfg['96btool']['server'] = 'https://discuss.96boards.org'
	if 'username' not in cfg['96btool']:
		cfg['96btool']['username'] = 'danielt'

	if zendesk_orig != cfg['zendesk'] or \
	   jira_orig != cfg['jira'] or \
	   l96btool_orig != cfg['96btool']:
		with open(filename, 'w') as f:
			cfg.write(f)
		print('{} was updated. Please check and re-run.'.format(filename),
				file=sys.stderr)
		sys.exit(1)

	return cfg

def get_password(config, heading):
	c = config[heading]
	return keyring.get_password(c['server'], c['username'])

def set_password(config, heading):
	c = config[heading]
	keyring.set_password(c['server'], c['username'], getpass.getpass())

def connect_to_jira():
	'''Connect to the server using a password from the keyring.'''
	cfg = get_config()['jira']
	password = keyring.get_password(cfg['server'], cfg['username'])

	from jira.client import JIRA
	return JIRA(options={'server': cfg['server']},
		    basic_auth=(cfg['username'], password))
