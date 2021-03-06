#!/usr/bin/python

#
# SCRIPT
#   msat_mk_cc_sl.py
# DESCRIPTION
#   Add a symbolic link path via the command line. See the
#   usage string for more help.
# OPTIONS
#   See the optparse code. parser.add_option statements.
# ARGUMENTS
#   None.
# RETURN
#   0: success.
# DEPENDENCIES
#   You need a Satellite server running to which this client
#   can connect.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB),  2013-02-24 13:07
#   Gerben Welter  (GW),  2013-04-28 22:04
# HISTORY
#   2013-04-28 22:04, GW added support for SELinux.
#   2013-09-15 23:04 GW: added support for symlinks.
# LICENSE
#   Copyright (C) 2013 Allard Berends
#
#   msat_mk_cc_sl.py is free software; you can
#   redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   msat_mk_cc_sl.py is distributed in the hope that
#   it will be useful, but WITHOUT ANY WARRANTY; without
#   even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU General Public
#   License for more details.
#
#   You should have received a copy of the GNU General
#   Public License along with this program; if not, write to
#   the Free Software Foundation, Inc., 59 Temple Place -
#   Suite 330, Boston, MA 02111-1307, USA.
# DESIGN
#

import base64
import config
import optparse
import sys
import xmlrpclib

usage = '''adds or updates a symbolic link to the specified config channel'''

description = '''This script adds or updates a symbolic link to the specified config channel.'''

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
  help = "config channel label"
)
parser.add_option(
  "--configpath-target",
  action = "callback",
  callback = config.parse_string,
  dest = "configpath_target",
  type = "string",
  default = None,
  help = "symbolic link path to file or dir"
)
parser.add_option(
  "--configpath-link",
  action = "callback",
  callback = config.parse_string,
  dest = "configpath_link",
  type = "string",
  default = None,
  help = "path of file or dir"
)
parser.add_option(
  "-z",
  "--configpath-context",
  action = "callback",
  callback = config.parse_string,
  dest = "configpath_context",
  type = "string",
  default = None,
  help = "SELinux context of a config file, [default: \'%default\']"
)
(options, args) = config.get_conf(parser)

if options.configchannel_label is None:
  parser.error('Error: specify label, -l or --configchannel-label')
if options.configpath_link is None:
  parser.error('Error: specify link, --configpath-link')
if options.configpath_target is None:
  parser.error('Error: specify target, --configpath-target')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

path_info = {}
path_info['target_path'] = options.configpath_target

if options.satellite_version in ['5.4', '5.5', '5.6']:
  if options.configpath_context:
    path_info['selinux_ctx'] = options.configpath_context

try:
  rc = client.configchannel.createOrUpdateSymlink(
    key,
    options.configchannel_label,
    options.configpath_link,
    path_info
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options
  sys.exit(1)

client.auth.logout(key)
