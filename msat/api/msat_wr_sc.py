#!/usr/bin/python

#
# SCRIPT
#   msat_wr_sc.py
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
#   Copyright (C) 2013 Allard Berends
#
#   msat_wr_sc.py is free software; you can
#   redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   msat_wr_sc.py is distributed in the hope that
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

import config
import hashlib
import optparse
import os.path
import pycurl
import shutil
import stat
import sys
import time
import xmlrpclib

usage = '''save specified software channel'''

description = '''This script saves the specified software channel to the specified location.'''

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
  "--satellite-rpmpath",
  action = "callback",
  callback = config.parse_string,
  dest = "satellite_rpmpath",
  type = "string",
  default = "/var/satellite",
  help = "Satellite rpm path",
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
  "-e",
  "--export-path",
  action = "callback",
  callback = config.parse_string,
  dest = "export_path",
  type = "string",
  default = None,
  help = "export directory"
)
parser.add_option(
  "-r",
  "--rpms-included",
  action = "callback",
  callback = config.parse_boolean,
  dest = "rpms_included",
  type = "string",
  default = False,
  help = "if set, RPM's are included"
)
parser.add_option(
  "--softwarechannel-banner",
  action = "callback",
  callback = config.parse_boolean,
  dest = "softwarechannel_banner",
  type = "string",
  default = 'yes',
  help = "output bash script banner, default is yes"
)
(options, args) = config.get_conf(parser)

if options.softwarechannel_label is None:
  parser.error('Error: specify label, -l or --softwarechannel-label')
if not options.export_path:
  export_path = os.path.join(os.getcwd(), options.softwarechannel_label)
else:
  export_path = os.path.join(options.export_path, options.softwarechannel_label)
if not os.path.exists(export_path):
  os.makedirs(export_path)

# Get session key via auth namespace.
client = xmlrpclib.ServerProxy(options.satellite_url, verbose=0)
key = client.auth.login(options.satellite_login, options.satellite_password)

try:
  details = client.channel.software.getDetails(
    key,
    options.softwarechannel_label,
  )
except xmlrpclib.Fault, e:
  print >> sys.stderr, str(e)
  print >> sys.stderr, options.softwarechannel_label
  sys.exit(1)

script = 'sc-' + options.softwarechannel_label + '.sh'
t = time.strftime("%Y-%m-%d %H:%M", time.localtime())
y = time.strftime("%Y", time.localtime())
script_path = os.path.join(export_path, script)
fd = open(script_path, 'w')
os.chmod(script_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
print >> fd, '''#!/bin/bash'''
if options.softwarechannel_banner:
  print >> fd, '''#
# SCRIPT
#   ''' + script + '''
# DESCRIPTION
#   This script creates the ''' + options.softwarechannel_label + '''
#   software channel.
# ARGUMENTS
#   None.
# RETURN
#   0: success.
# DEPENDENCIES
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

print >> fd, '''\nmsat_mk_sc.py \\'''

# Set software channel label, name and summary.
print >> fd, "  --softwarechannel-label \"%s\" \\" % (details['label'], )
print >> fd, "  --softwarechannel-name \"%s\" \\" % (details['name'], )
print >> fd, "  --softwarechannel-summary \"%s\" \\" % (details['summary'], )

# Set software channel arch.
print >> fd, "  --softwarechannel-arch \"channel-%s\" \\" % (details['arch_name'], )

# Set software channel parent.
print >> fd, "  --softwarechannel-parent \"%s\"" % (details['parent_channel_label'], )

if options.rpms_included:
  rpms = os.path.join(export_path, 'rpms')
  if not os.path.isdir(rpms):
    os.makedirs(rpms)
  try:
    list = client.channel.software.listAllPackages(
      key,
      options.softwarechannel_label,
    )
  except xmlrpclib.Fault, e:
    print >> sys.stderr, str(e)
    print >> sys.stderr, options.softwarechannel_label
    sys.exit(1)

  for pkg in list:
    try:
      pkg_url = client.packages.getPackageUrl(
        key,
        pkg['id'],
      )
    except xmlrpclib.Fault, e:
      print >> sys.stderr, str(e)
      print >> sys.stderr, id

    filename = pkg['name'] + '-' + pkg['version'] + '-' + pkg['release'] + '.' + pkg['arch_label'] + '.rpm'
    if not os.path.isfile(rpms + '/' + filename):
      c = pycurl.Curl()
      c.setopt(c.URL, pkg_url)
      with open(rpms + '/' + filename, 'wb') as f:
        c.setopt(c.WRITEFUNCTION, f.write)
        c.perform()
    else:
      chk = hashlib.md5(open(rpms + '/' + filename).read()).hexdigest()
      if pkg['checksum'] == chk:
        print "checksum of %s matches, not downloading again." % (filename)
      else:
        print "checksum mismatch, redownloading %s" % (filename)
        c = pycurl.Curl()
        c.setopt(c.URL, pkg_url)
        with open(rpms + '/' + filename, 'wb') as f:
          c.setopt(c.WRITEFUNCTION, f.write)
          c.perform()

  print >> fd, "P=$(/usr/bin/dirname $0)"
  print >> fd, "# To push the RPM's with rhnpush"
  print >> fd, "/usr/bin/rhnpush --username=$(msat_ls_sl.py) --password=$(msat_ls_sp.py) --dir=$P/rpms --channel=%s" % (options.softwarechannel_label, )

fd.close()
client.auth.logout(key)
