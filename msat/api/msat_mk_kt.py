#!/usr/bin/python

#
# SCRIPT
#   msat_mk_kt.py
# DESCRIPTION
#   Add a kickstartable tree via the command line. See the
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
#   If you put single quotes around value, but forget to
#   escape embedded single quotes, this script will fail.
#   Escaping works like this:
#   $ echo 'don'"'"'t'
#   don't
#   So ' -> '"'"'
#   Complicated huh?
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Allard Berends (AB),  2013-02-24 13:07
# HISTORY
#   2013-02-24 13:07, AB: added optionsiguration files option.
# LICENSE
#   Copyright (C) 2013 Allard Berends
# 
#   msat_mk_kt.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_mk_kt.py is distributed in the hope that it will be
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
import sys
import xmlrpclib

usage = '''adds the specified kickstartable tree'''

description = '''This script adds the specified kickstartable tree. If the kickstartable tree already exists, an error will be given and a dump of the used parameters. The kickstartable tree must be removed first before this script succeeds.'''

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
  help = "Path to the parameter file",
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
  help = "Admin account to log in with on Satellite",
)
parser.add_option(
  "-p",
  "--satellite-password",
  action = "callback",
  callback = config.parse_string,
  dest = "satellite_password",
  type = "string",
  default = None,
  help = "Password belonging to Satellite admin account",
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
  "--tree-label",
  action = "callback",
  callback = config.parse_string,
  dest = "tree_label",
  type = "string",
  default = None,
  help = "The new kickstart tree label"
)
parser.add_option(
  "--base-path",
  action = "callback",
  callback = config.parse_string,
  dest = "base_path",
  type = "string",
  default = None,
  help = "Path to the base or root of the kickstart tree"
)
parser.add_option(
  "--channel-label",
  action = "callback",
  callback = config.parse_string,
  dest = "channel_label",
  type = "string",
  default = None,
  help = "Label of channel to associate with the kickstart tree"
)
parser.add_option(
  "--install-type",
  action = "callback",
  callback = config.parse_string,
  dest = "install_type",
  type = "string",
  default = None,
  help = "Label for KickstartInstallType (rhel_2.1, rhel_3, rhel_4, rhel_5, fedora_9)"
)

(options, args) = config.get_conf(parser)

if options.satellite_url is None:
  parser.error('Error: specify URL, -u or --satellite-url')
if options.satellite_login is None:
  parser.error('Error: specify login, -l or --login')
if options.satellite_password is None:
  parser.error('Error: specify password, -p or --password')
if options.tree_label is None:
  parser.error('Error: specify --tree-label')
if options.base_path is None:
  parser.error('Error: specify --base-path')
if options.channel_label is None:
  parser.error('Error: specify --channel-label')
if options.install_type is None:
  parser.error('Error: specify --install-type')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

# create kickstartable tree
try:
  rc = client.kickstart.tree.create(
    key,
    options.tree_label,
    options.base_path,
    options.channel_label,
    options.install_type,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options
  sys.exit(1)

client.auth.logout(key)
