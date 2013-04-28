#!/usr/bin/python

#
# SCRIPT
#   msat_wr_cc.py
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
#   msat_wr_cc.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_wr_cc.py is distributed in the hope that it will be
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
import urlparse
import xmlrpclib

def escape_quote(s):
  # Remove nasty long dash u'u2013' with --
  s = re.sub(u'(?ms)[\u2013\u00ad]', '--', s)
  s = s.encode('ascii')
  # We use here documents, so no ' escaping
  #e = re.sub('(?ms)\'', '\'"\'"\'', s)
  #s = re.sub('(?ms)`', '\`', s)
  #s = re.sub('(?ms)\$', '\\$', s)
  return s

usage = '''writes recreation script of config channel and config files to stdout'''

description = '''This script writes the specified config channel and config file contents to stdout in the form of shell script to recreate the data elements.'''

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
  "--configchannel-label",
  action = "callback",
  callback = config.parse_string,
  dest = "configchannel_label",
  type = "string",
  default = None,
  help = "configchannel label"
)
parser.add_option(
  "-e",
  "--configchannel-existence",
  action = "callback",
  callback = config.parse_boolean,
  dest = "configchannel_existence",
  type = "string",
  default = None,
  help = "test for configchannel existence in regeneration script"
)
(options, args) = config.get_conf(parser)

if options.configchannel_label is None:
  parser.error('specify configchannel label, -l or --configchannel-label. Use list_config_channels.py to find all configchannel labels.')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

script = 'cc-' + options.configchannel_label + '.sh'
t = time.strftime("%Y-%m-%d %H:%M", time.localtime())
y = time.strftime("%Y", time.localtime())
print '''#!/bin/bash
#
# SCRIPT
#   ''' + script + '''
# DESCRIPTION
#   This script creates the ''' + options.configchannel_label + '''
#   config channel and contents.
# ARGUMENTS
#   None.
# RETURN
#   0: success.
# DEPENDENCIES
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
#

'''

if options.configchannel_existence:
  print  '''if [ -n "$(msat_ls_cc.py | /bin/grep %s)" ]; then
  /bin/echo "INFO: %s already exists! Bailing out."
  exit 0
fi
''' % (options.configchannel_label, options.configchannel_label)

print '''msat_mk_cc.py \\'''

# Set configchannel label.
print "  --configchannel-label %s \\" % (options.configchannel_label, )

# Get description: Configuration > Overview
# Get name: Configuration > Overview
try:
  details = client.configchannel.getDetails(
    key,
    options.configchannel_label,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options

print "  --configchannel-description '%s' \\" % (details['description'], )
print "  --configchannel-name '%s'" % (details['name'], )
print

# Get files: Configuration > List/Remove Files
try:
  files = client.configchannel.listFiles(
    key,
    options.configchannel_label,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options

filelist = [f['path'] for f in files]

try:
  files = client.configchannel.lookupFileInfo(
    key,
    options.configchannel_label,
    filelist
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options

for f in files:
  print "msat_mk_cc_cf.py \\"

  # Set configchannel label.
  print "  --configchannel-label %s \\" % (options.configchannel_label, )
  print "  --configpath-path %s \\" % (f['path'], )

  if f['type'] == 'file':
    print "  --configpath-dir false \\"
    print "  --configpath-content - \\"
  else:
    print "  --configpath-dir true \\"

  print "  --configpath-user %s \\" % (f['owner'], )
  print "  --configpath-group %s \\" % (f['group'], )
  if f['type'] == 'file':
    print "  --configpath-permissions %s \\" % (f['permissions_mode'], )
  else:
    print "  --configpath-permissions %s" % (f['permissions_mode'], )
  if f['type'] == 'file':
    print "  --configpath-startdelimiter '%s' \\" % (f['macro-start-delimiter'], )
  if f['type'] == 'file':
    print "  --configpath-enddelimiter '%s' << 'EOF__BLAH__EOF'" % (f['macro-end-delimiter'], )
    if f['binary']:
      print >> sys.stderr, "ERROR: %s: %s: binary config files not supported" % (options.configchannel_label, f['path'])
      content = xmlrpclib.Binary.decode(f['contents'])
      print content
      print
      print
      print
      print f['content']
    else:
      try:
        c = escape_quote(f['contents'])
      except UnicodeEncodeError, e:
        print >> sys.stderr, "ERROR: %s: %s: unicode characters not supported" % (options.configchannel_label, f['path'])
      else:
        print c
    print "EOF__BLAH__EOF"

  print

client.auth.logout(key)