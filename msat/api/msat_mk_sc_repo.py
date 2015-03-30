#!/usr/bin/python

#
# SCRIPT
#   msat_mk_sc_repo.py
# DESCRIPTION
#   Add a software channel via the command line. See the
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
#   Allard Berends (AB), 2013-02-24 13:07
# HISTORY
# LICENSE
#   Copyright (C) 2013 Allard Berends
#
#   msat_mk_sc_repo.py is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_mk_sc_repo.py is distributed in the hope that it will be
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

usage = '''create software channel'''

description = '''This script creates the specified software channel.'''

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
  "--repo-label",
  action = "callback",
  callback = config.parse_string,
  dest = "repo_label",
  type = "string",
  default = None,
  help = "repository label"
)
parser.add_option(
  "-n",
  "--softwarechannel-name",
  action = "callback",
  callback = config.parse_string,
  dest = "softwarechannel_name",
  type = "string",
  default = None,
  help = "config channel name"
)
parser.add_option(
  "-s",
  "--source-url",
  action = "callback",
  callback = config.parse_string,
  dest = "source_url",
  type = "string",
  default = None,
  help = "source url"
)
parser.add_option(
  "-t",
  "--trigger-sync",
  action = "callback",
  callback = config.parse_boolean,
  dest = "trigger_repo",
  type = "string",
  default = None,
  help = "trigger repo sync"
)
(options, args) = config.get_conf(parser)

if options.repo_label is None:
  parser.error('Error: specify label, -l or --repo-label')
if options.source_url is None:
  parser.error('Error: specify source url, -s or --source-url')

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  repo = client.channel.software.getRepoDetails(
         key,
         options.repo_label,
         )
  print "Repository %s already exists, skipping creation." % (options.repo_label)
except xmlrpclib.Fault, e:
  try:
    rc = client.channel.software.createRepo(
      key,
      options.repo_label,
      'yum',
      options.source_url,
    )
  except:
    pass

if options.softwarechannel_name:
  try:
    channel = client.channel.software.getDetails(
              key,
              options.softwarechannel_name,
              )
  except xmlrpclib.Fault, e:
    print >> sys.stderr, "Channel %s does not exist!" % (options.softwarechannel_name)
    sys.exit(1)

  try:
    rc = client.channel.software.associateRepo(
         key,
         options.softwarechannel_name,
         options.repo_label,
         )
  except xmlrpclib.Fault, e:
    pass

  try:
    sync = client.channel.software.syncRepo(
        key,
        options.softwarechannel_name,
        # Default schedule: every sunday at midnight
        '0 0 0 ? * 1',
        )
  except:
    pass

  if options.trigger_repo:
    try:
      trigger = client.channel.software.syncRepo(
          key,
          options.softwarechannel_name,
          )
    except xmlrpclib.Fault, e:
      pass

client.auth.logout(key)
