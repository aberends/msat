#!/usr/bin/python

#
# SCRIPT
#   msat_mk_user_role.py
# DESCRIPTION
#   Add a role to a user account via the command line. See the
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
#   Erik van Pienbroek (EVP), 2015-01-15 13:47
# HISTORY
#   2015-01-15 13:47, EVP: initial release.
# LICENSE
#   Copyright (C) 2015 Erik van Pienbroek
#
#   msat_mk_user.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_mk_user.py is distributed in the hope that it will be
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

usage = '''add a role to an user account'''

description = '''This script adds a specified role to an user account.'''

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
  "-l",
  "--login",
  action = "callback",
  callback = config.parse_string,
  dest = "user_login",
  type = "string",
  default = None,
  help = "login name of the user account to be updated"
)
parser.add_option(
  "--role",
  action = "callback",
  callback = config.parse_string,
  dest = "user_role",
  type = "string",
  default = None,
  help = "Role label to add. Can be any of: satellite_admin, org_admin, channel_admin, config_admin, system_group_admin, activation_key_admin, or monitoring_admin"
)
(options, args) = config.get_conf(parser)

if options.user_login is None:
  parser.error('Error: specify -l or --login')
if options.user_role is None:
  parser.error('Error: specify --role')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  rc = client.user.addRole(
    key,
    options.user_login,
    options.user_role,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options

client.auth.logout(key)
