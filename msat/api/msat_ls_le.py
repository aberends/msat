#!/usr/bin/python

#
# SCRIPT
#   msat_ls_le.py
# DESCRIPTION
# DEPENDENCIES
#   You need a Satellite server running to which this client
#   can connect.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB),  2013-02-24 13:07
# HISTORY
# LICENSE
#   Copyright (C) 2015 Gerben Welter
#
#   msat_ls_le.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_ls_le.py is distributed in the hope that it will be
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
import xmlrpclib

usage = '''list system and software channels entitlements'''

description = '''This script lists the used system and software channels entitlements on the Satellite server.'''

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
(options, args) = config.get_conf(parser)

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  entitlements = client.satellite.listEntitlements(
    key,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)

print ""
print "System Entitlements for Satellite organization '%s':" % ((options.satellite_login).split('_')[0])
print ""
print "%-40s\t%s\t%s\t%s" % ('Name','Total', 'Used', 'Free')
print "===================================================================="
for i in entitlements['system']:
  print "%-40s\t%s\t%s\t%s" % (i['name'], i['total_slots'], i['used_slots'], i['free_slots'])

print ""
print ""
print "Software Channel Entitlement for Satellite organization '%s':" % ((options.satellite_login).split('_')[0])
print ""
print "%-60s\t%s\t%s\t%s\t%s\t%s\t%s" % ('Name','Total', 'Used', 'Free', 'FlexTotal', 'FlexUsed', 'FlexFree')
print "================================================================================================================================"
for i in entitlements['channel']:
  print "%-60s\t%s\t%s\t%s\t%s\t\t%s\t\t%s" % (i['name'], i['total_slots'], i['used_slots'], i['free_slots'], i['total_flex'], i['used_flex'], i['free_flex'])



#print entitlements

client.auth.logout(key)
