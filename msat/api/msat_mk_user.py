#!/usr/bin/python

#
# SCRIPT
#   msat_mk_user.py
# DESCRIPTION
#   Add a user account via the command line. See the
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
#   Erik van Pienbroek (EVP), 2015-01-15 13:10
# HISTORY
#   2015-01-15 13:30, EVP: initial release.
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

usage = '''create a user account'''

description = '''This script creates the specified user account.'''

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
  "--desired-login",
  action = "callback",
  callback = config.parse_string,
  dest = "desired_login",
  type = "string",
  default = None,
  help = "desired login name"
)
parser.add_option(
  "--desired-password",
  action = "callback",
  callback = config.parse_string,
  dest = "desired_password",
  type = "string",
  default = None,
  help = "desired password"
)
parser.add_option(
  "--first-name",
  action = "callback",
  callback = config.parse_string,
  dest = "first_name",
  type = "string",
  default = None,
  help = "first name of the user"
)
parser.add_option(
  "--last-name",
  action = "callback",
  callback = config.parse_string,
  dest = "last_name",
  type = "string",
  default = None,
  help = "last name of the user"
)
parser.add_option(
  "--email",
  action = "callback",
  callback = config.parse_string,
  dest = "user_email",
  type = "string",
  default = None,
  help = "e-mail address of the user"
)
(options, args) = config.get_conf(parser)

if options.desired_login is None:
  parser.error('Error: specify -l or --desired-login')
if options.desired_password is None:
  parser.error('Error: specify --desired-password')
if options.first_name is None:
  parser.error('Error: specify --first-name')
if options.last_name is None:
  parser.error('Error: specify --last-name')
if options.user_email is None:
  parser.error('Error: specify --email')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  rc = client.user.create(
    key,
    options.desired_login,
    options.desired_password,
    options.first_name,
    options.last_name,
    options.user_email,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options

client.auth.logout(key)
