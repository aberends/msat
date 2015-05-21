#!/usr/bin/python

#
# SCRIPT
#   msat_wr_cr.py
# DESCRIPTION
# OPTIONS
# ARGUMENTS
# RETURN
#   0: success.
# DEPENDENCIES
#   You need a Satellite server running to which this client
#   can connect.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB), 2013-02-24 13:07
# HISTORY
# LICENSE
#   Copyright (C) 2013 Allard Berends
#
#   msat_wr_cr.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_wr_cr.py is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the
#   implied warranty of MERCHANTABILITY or FITNESS FOR A
#   PARTICULAR PURPOSE. See the GNU General Public License
#   for more details.
#
#   You should have received a copy of the GNU General
#   Public License along with this program; if not, write to
#   the Free Software Foundation, Inc., 59 Temple Place -
#   Suite 330, Boston, MA 02111-1307, USA.
# DESIGN
#

import config
import optparse
import re
import sys
import time
import xmlrpclib

usage = '''writes specified cryptographic key to stdout'''

description = '''This script writes the creation script of the specified cryptographic key. The '1-' of the organisation must be provided.'''

parser = optparse.OptionParser(
  usage = usage,
  version = '1.6',
  description = description,
)
parser.add_option(
  "-x",
  "--xml-help",
  action = "callback",
  callback = config.print_xmlhelp,
  help = "Print help in XML format",
)

parser.add_option(
  "-f",
  "--params-file",
  action = "callback",
  callback = config.parse_path,
  dest = "params_file",
  type = "string",
  default = '.sat.conf',
  help = "path to the parameter file",
)

parser.add_option(
  "-u",
  "--satellite-url",
  action = "callback",
  callback = config.parse_url,
  dest = "satellite_url",
  type = "string",
  default = None,
  help = "Satellite RPC API URL to use",
)
parser.add_option(
  "-a",
  "--satellite-login",
  action = "callback",
  callback = config.parse_string,
  dest = "satellite_login",
  type = "string",
  default = None,
  help = "admin account to log in with on Satellite",
)
parser.add_option(
  "-p",
  "--satellite-password",
  action = "callback",
  callback = config.parse_string,
  dest = "satellite_password",
  type = "string",
  default = None,
  help = "password belonging to Satellite admin account",
)
parser.add_option(
  "-v",
  "--satellite-version",
  action = "callback",
  callback = config.parse_string,
  dest = "satellite_version",
  type = "string",
  default = "5.4",
  help = "version of the Satellite API",
)

parser.add_option(
  "-l",
  "--crypto-key",
  action = "callback",
  callback = config.parse_string,
  dest = "crypto_key",
  type = "string",
  default = None,
  help = "cryptographic key"
)
parser.add_option(
  "-e",
  "--activationkey-existence",
  action = "callback",
  callback = config.parse_boolean,
  dest = "activationkey_existence",
  type = "string",
  default = None,
  help = "test for activationkey existence in regeneration script"
)
parser.add_option(
  "--cryptokey-banner",
  action = "callback",
  callback = config.parse_boolean,
  dest = "cryptokey_banner",
  type = "string",
  default = 'yes',
  help = "output bash script banner, default is yes"
)
(options, args) = config.get_conf(parser)

if options.satellite_url is None:
  parser.error('Error: specify URL, -u or --satellite-url')
if options.satellite_login is None:
  parser.error('Error: specify login, -l or --login')
if options.satellite_password is None:
  parser.error('Error: specify password, -p or --password')
if options.crypto_key is None:
  parser.error('specify crypto key name, -l or --crypto-key. Use list_crypto_keys.py to find all crypto keys.')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  details = client.kickstart.keys.getDetails(
    key,
    options.crypto_key,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options
  sys.exit(1)

script = 'cr-' + re.sub('\d+-', '', options.crypto_key, 1) + '.sh'
t = time.strftime("%Y-%m-%d %H:%M", time.localtime())
y = time.strftime("%Y", time.localtime())
print '#!/bin/bash'

if options.cryptokey_banner:
  print '''#
# SCRIPT
#   ''' + script + '''
# DESCRIPTION
#   This script creates the ''' + re.sub('\d+-', '', options.crypto_key, 1) + '''
#   cryptographic key.
# ARGUMENTS
#   None.
# RETURN
#   0: success.
# DEPENDENCIES
#   This script depends on a functioning Satellite server to
#   connect to.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB), ''' + t + '''
# HISTORY
# LICENSE
#   Copyright (C) ''' + y + ''' Allard Berends
#
#   ''' + script + ''' is free software; you can
#   redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   ''' + script + ''' is distributed in the hope
#   that it will be useful, but WITHOUT ANY WARRANTY;
#   without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#   Public License for more details.
#
#   You should have received a copy of the GNU General
#   Public License along with this program; if not, write to
#   the Free Software Foundation, Inc., 59 Temple Place -
#   Suite 330, Boston, MA 02111-1307, USA.
# DESIGN
#'''
cr_label = re.sub('\d+-', '', options.crypto_key, 1)

print '''
msat_mk_cr.py \\'''

print "  --key-description %s \\" % (details['description'], )
print "  --key-type %s \\" % (details['type'], )
print "  --key-content - << 'EOF__BLAH__EOF'\n%sEOF__BLAH__EOF" % (details['content'], )

client.auth.logout(key)

