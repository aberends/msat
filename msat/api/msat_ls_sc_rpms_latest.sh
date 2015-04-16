#! /bin/bash
#
# SCRIPT
#   msat_ls_sc_rpms_latest.sh
# DESCRIPTION
# DEPENDENCIES
#   The script depends on the python Satellite API scripts.
# FAILURE
# AUTHORS
#   Date strings made with 'date +"\%Y-\%m-\%d \%H:\%M"'.
#   Gerben Welter (GW),  2013-12-29 11:07
# HISTORY
# LICENSE
#   Copyright (C) 2013 Gerben Welter
#
#   msat_ls_sc_rpms_latest.sh is free software; you can redistribute it
#   and/or modify it under the terms of the GNU General
#   Public License as published by the Free Software
#   Foundation; either version 3 of the License, or (at your
#   option) any later version.
#
#   msat_ls_sc_rpms_latest.sh is distributed in the hope that it will be
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

#
# FUNCTION
#   usage
# DESCRIPTION
#   This function explains how this script should be called
#   on the command line.
# RETURN CODE
#   Nothing
#
usage() {
  echo "Usage: $PNAME"
  echo " -l <channel label>"
  echo " -c : To output in clone script format"
  echo " -h : this help message"
} # end usage

#
# FUNCTION
#   options
# DESCRIPTION
#   This function parses the command line options.
#   If an option requires a parameter and it is not
#   given, this function exits with error code 1, otherwise
#   it succeeds. Parameter checking is done later.
# EXIT CODE
#   1: error
#
while getopts ":l:ch" Option
do
  case $Option in
  l)  L_OPTION=$OPTARG ;;
  c)  C_OPTION="yes" ;;
  *)  usage
      exit 1 ;;
  esac
done

# Check if the supplied channel label exists.
CHECKCHANNEL=`msat_ls_sc.py | grep ^${L_OPTION}$ | wc -l`

if [ "$CHECKCHANNEL" == "0" ]; then
  echo "Supplied channel label not available!"
  echo "Use msat_ls_sc.py to list all available channels."
  exit 1
fi

# Make temp files to store various stages of the channel data.
ALL_RPMS=$(mktemp)
UNIQ_RPMS=$(mktemp)
LATEST_RPMS=$(mktemp)
LIST=$(mktemp)

# Save the channel package list to file and generate a list
# of unique package names in the channel.
msat_ls_sc_rpms.py -l $L_OPTION | tee $ALL_RPMS | awk 'BEGIN {FS=" "}; {print $1}' | sort -u > $UNIQ_RPMS

# Now we go in a loop to filter out the latest version per package.
# The extra space in the grep is needed to distinguish
# between e.g. 'hiera' and ' hiera-puppet'.
# Another grep for the package name and its latest version filters
# both the 32- and 64-bit format if applicable.
# This works on the premise that the different binary arch packages
# always are on the same patch level.

for package in $(cat $UNIQ_RPMS)
do
  LATEST=$(cat $ALL_RPMS | grep "^$package " | sort -V | tail -1 | awk 'BEGIN {FS=" "}; {print $2 " " $3}')
  cat $ALL_RPMS | grep "$package " | grep "$LATEST" >> $LATEST_RPMS
done

# Convert the list back to actual filenames.
sed -r 's/\ (noarch|x86_64|i686|i386)$/.\1/g' $LATEST_RPMS | tr ' ' '-' > $LIST

# Depending on the -c option show the list line by line
# or in the format used by the clone scripts.

if [ "$C_OPTION" == "yes" ]; then
  cat $LIST | tr '\n' ',' | sed 's/,$//'
  echo ""
else
 cat $LIST
fi

# Clean up the temp files
rm -f $ALL_RPMS $UNIQ_RPMS $LATEST_RPMS

