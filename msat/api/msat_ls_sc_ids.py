#!/usr/bin/python

#
# SCRIPT
#   msat_ls_sc_ids.py
# DESCRIPTION
#   Lists the RPM ID's of the specified RPM names in the
#   specified software channel label.
# DEPENDENCIES
#   You need a Satellite server running to which this client
#   can connect.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB), 2013-05-20 19:24
#   Gerben Welter (GW), 2013-09-15 22:49
# HISTORY
#   2013-09-15 22:47 (AB): added suggestion of Gerben Welter
#                          to e:n-v-r.a output
# LICENSE
#   Copyright (C) 2013 Allard Berends
#
#   msat_ls_sc_ids.py is free software; you can
#   redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   msat_ls_sc_ids.py is distributed in the hope that it
#   will be useful, but WITHOUT ANY WARRANTY; without even
#   the implied warranty of MERCHANTABILITY or FITNESS FOR A
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
import sys
import xmlrpclib

usage = '''list RPM ID's of specified RPM's in software channel'''

description = '''This script lists the RPM ID's of the specified RPM's in the specified software channel.'''

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
  "--softwarechannel-label",
  action = "callback",
  callback = config.parse_string,
  dest = "softwarechannel_label",
  type = "string",
  default = None,
  help = "softwarechannel label"
)
parser.add_option(
  "-n",
  "--rpm-names",
  action = "callback",
  callback = config.parse_string,
  dest = "rpm_names",
  type = "string",
  default = None,
  help = "comma separated list of RPM's"
)
(options, args) = config.get_conf(parser)

if options.softwarechannel_label is None:
  parser.error('Error: specify label, -l or --softwarechannel-label')
if options.rpm_names is None:
  parser.error('Error: specify RPM names, -n or --rpm-names')

names = options.rpm_names.split(',')

d = {}
for n in names:
  d[n] = None

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  rpms = client.channel.software.listAllPackages(
    key,
    options.softwarechannel_label,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, kickstart

for i in rpms:
  if not i['epoch']:
    rpm = "%s-%s-%s.%s" % (i['name'], i['version'], i['release'], i['arch_label'])
  else:
    rpm = "%s-%s-%s:%s.%s" % (i['name'], i['version'], i['release'], i['epoch'], i['arch_label'])
  try:
    d[rpm]
    d[rpm] = i['id']
  except KeyError, e:
    pass

ids = d.values()
ids.sort()
ids = [str(i) for i in ids]
print ','.join(ids)

client.auth.logout(key)
