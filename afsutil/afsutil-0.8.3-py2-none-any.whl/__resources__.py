# This is a generated file. Do not edit.

resources = {
    "openafs-client-linux.init":\
"""\
#! /bin/bash
# Copyright 2000, International Business Machines Corporation and others.
# All Rights Reserved.
#
# This software has been released under the terms of the IBM Public
# License.  For details, see the LICENSE file in the top-level source
# directory or online at http://www.openafs.org/dl/license10.html

# AFS	Start and stop AFS components
#
#
# chkconfig: 35 60 20
# description:  AFS is a distributed file system which provides location
#		transparency, caching and secure authentication.
#		Additional configuration can be done in the /etc/sysconfig/afs
#		file. Read the documentation in that file for more information.
#
# The following section is used at least by SuSE insserv(8)
### BEGIN INIT INFO
# Provides: afs
# Required-Start: $network
# Required-Stop: $network
# Default-Start: 3 5
# Default-Stop: 0 1 2 6
# Description:  AFS is a distributed file system which provides location
#              transparency, caching and secure authentication.
#              Additional configuration can be done in the /etc/sysconfig/afs
#              file. Read the documentation in that file for more information.
### END INIT INFO
#
# Note that AFS does not use a pid file in /var/run. It is turned off by
# unmounting /afs.


# check for special bootup functions
if [ -f /etc/rc.d/init.d/functions ] ; then
	. /etc/rc.d/init.d/functions
	afs_rh=1
else
	# special (RedHat) functions not available...
	# so I provide neccessary replacements (e.g. for SuSE)

	function echo_failure () { echo -n " - failed." ; }

	function echo_success () { echo -n " - successful." ; }

	# these are hopefully all functions I use...
fi

runcmd() {
   echo -n "$1 "
   shift
   if [ "$BOOTUP" = "color" ]; then
      $* && echo_success || echo_failure
   else
      $*
   fi
   echo
}

KERNEL_VERSION=`uname -r`

# Gather up options and post startup script name, if present
SYSCNF=/etc/sysconfig/openafs-client
CACHESIZE="AUTOMATIC"
AFSD_OPTIONS=""
CACHEINFO=/usr/vice/etc/cacheinfo
CACHE=/usr/vice/cache
AFS=/afs
AFSD=/usr/vice/etc/afsd
KILLAFS=/usr/vice/etc/killafs
if [ -f $SYSCNF ] ; then
	. $SYSCNF
fi

on_network() {
    if hash ip 2>/dev/null >/dev/null; then
        IP="ip -4 addr"
    elif hash ifconfg 2>/dev/null >/dev/null; then
        IP="ifconfig -a"
    else
        echo afs: Unable to check interfaces. 1>&2
        return 1
    fi
    ADDRS=`LANG=C ${IP} | grep 'inet ' | grep -v 127.0.0.1 | wc -l`
    if [ "$ADDRS" = "" ]; then
       echo afs: No interfaces with IP address 1>&2
       return 1
    elif [ $ADDRS = 0 ]; then
       echo afs: No interfaces with IP address 1>&2
       return 1
    fi
    return 0
}

# If choose_client can't correctly determine which client to use, set
# LIBAFS manually.
choose_client() {

	# Use the second field of the uname -v output instead of just
	# doing a match on the whole thing to protect against matching
	# a timezone named SMP -- I don't know of one, but let's be
	# paranoid.

	set X `uname -v`; shift
	case $2 in
	SMP) MP=.mp ;;	# MP system
	*)   MP= ;;	# SP system
	esac

	# For now, just use uname -r to get the module version.
	case $KERNEL_VERSION in
	  [1-2].[0-5].*)
		LIBAFS=libafs-$KERNEL_VERSION$MP.o
		;;
	  *)
		LIBAFS=libafs-$KERNEL_VERSION$MP.ko
		;;
	esac
}

#
# Find prefix symbol to use with insmod.  We find the unregister_filesystem
# string from /proc/ksyms since we know it's there.  If /proc/ksyms does not
# exist, we print that info to the console and use the uname -v output to
# decide on a prefix.
# unregister_filesystem_Rsmp_b240cad8 is a typcial SMP version string from
# a kernel built from ftp.kernel.org
#
case $KERNEL_VERSION in
  [1-2].[0-5].*)
	KSYMS_FILE=/proc/ksyms
	;;
  *)
	KSYMS_FILE=/proc/kallsyms
	;;
esac
SEARCH_STR="unregister_filesystem"
DEFAULT_SMP_PREFIX="smp_" # Redhat kernels need "smp" instead
PREFIX="" # none needed for UP with <= 1Gig memory

set_prefix()
{
	h='[0-9a-fA-F]'
	h8="$h$h$h$h$h$h$h$h"
	prefix_set=0

	set X `egrep "\<$SEARCH_STR" $KSYMS_FILE 2> /dev/null`; shift

	case $KERNEL_VERSION in
	  [1-2].[0-5].*)
		str=$2
		;;
	  *)
		str=$3
		;;
	esac
	case $str in
	${SEARCH_STR}_R$h8)
		# No prefix required
		;;
	$SEARCH_STR)
		# No versioning in kernel symbols
		;;
	${SEARCH_STR}_R*$h8)
		suffix=${str#${SEARCH_STR}_R}
		PREFIX=${suffix%$h8}
		;;
	*)
		case $str in
		'')
			echo afsd: Cannot find \"$SEARCH_STR\" in file $KSYMS_FILE
			;;
		*)
			echo afsd: Malformed kernel version symbol \"$str\"
			;;
		esac

		echo Guessing prefix from output of uname -v
		set X `uname -v`; shift
		case $2 in
		SMP)
			PREFIX=$DEFAULT_SMP_PREFIX
			;;
		esac
		;;
	esac
}

MODLOADDIR=${MODLOADDIR:-/usr/vice/etc/modload}
# load_client loads the AFS client module if it's not already loaded.
load_client() {

	# Load the packaging style kmod if present, otherwise fallback
	# to the legacy style.
	if [ -f /lib/modules/`uname -r`/extra/openafs/openafs.ko ] ; then
		modprobe openafs
		return
	fi

	# If LIBAFS is set, use it.
	if [ -z "$LIBAFS" ] ; then
		# Try to determine the right client.
		choose_client
	fi

	if [ ! -f "$MODLOADDIR/$LIBAFS" ] ; then
		echo AFS module $MODLOADDIR/$LIBAFS does not exist. Not starting AFS.
		exit 1
	fi

	# We need exportfs in order to access the cache files. Load it, but
	# ignore errors as on some machines it may be built in to the kernel.
	/sbin/modprobe exportfs >/dev/null 2>&1

	if [ -f $KSYMS_FILE ]; then
		# use the prefix command if required
		case $KERNEL_VERSION in
		  [1-2].[0-5].*)
			set_prefix
			/sbin/insmod ${PREFIX:+-P $PREFIX} -f -m $MODLOADDIR/$LIBAFS > $MODLOADDIR/libafs.map 2>&1
			;;
		  *)
			/sbin/insmod $MODLOADDIR/$LIBAFS > $MODLOADDIR/libafs.map 2>&1
			;;
		esac
	else
		/sbin/insmod $MODLOADDIR/$LIBAFS > $MODLOADDIR/libafs.map 2>&1
	fi
}

generate_cacheinfo() {
    if [ "$CACHESIZE" = "AUTOMATIC" ]; then
	LINE=`df -k $CACHE | tail -1`
	PART=`echo $LINE | awk '{ if ( ($NF != "/usr")  && ($NF != "/") ) print $NF; else print "NONE";}'`
	if [ "$PART" = "NONE" ]; then
	    echo "$CACHE or /usr/vice is not a separate partition"
	    echo "you have to change the cachesize in $SYSCNF by hand"
	    echo "AFS will be started with a VERY small cache of 8Mb."
	    CACHESIZE=8000
	else
	    # Check to see if df has pretty-printed for long dev (i.e. LVM)
            FCHAR=`echo $LINE | cut -c 1`
            if [ "$FCHAR" = "/" ]; then
                PARTSIZE=`echo $LINE | awk '{print $2}'`
            else
                PARTSIZE=`echo $LINE | awk '{print $1}'`
	    fi
	    CACHESIZE=`echo $PARTSIZE | awk '{printf "%d",int(($1*.8)/1000)*1000}'`
	fi
    fi
    if [ "x$CACHESIZE" != "x" ]; then
	echo $AFS:$CACHE:$CACHESIZE >$CACHEINFO
	chmod 0644 $CACHEINFO
    else
	CACHESIZE=`awk -F: '{print $3}' < $CACHEINFO`
    fi
}

generate_csdb() {
    if [ -f /usr/vice/etc/CellServDB.local -a -f /usr/vice/etc/CellServDB.dist ]; then
        if [ -h /usr/vice/etc/CellServDB ]; then
            rm -f /usr/vice/etc/CellServDB
        fi
        cat /usr/vice/etc/CellServDB.local /usr/vice/etc/CellServDB.dist >/usr/vice/etc/CellServDB
        chmod 644 /usr/vice/etc/CellServDB
    fi
}

case "$1" in
  start)
    if [ ! "$afs_rh" -o ! -f /var/lock/subsys/openafs-client ]; then
        if [ `echo "$AFSD_OPTIONS" | grep -c dynroot` = 0 ]; then
            on_network || exit 1
        fi
	# Load kernel extensions
	if  load_client  ; then :
	else
		echo Failed to load AFS client, not starting AFS services.
		exit 1
	fi

	echo "Starting AFS services..... "
	generate_cacheinfo
	generate_csdb
	${AFSD} ${AFSD_OPTIONS}
	test "$afs_rh" && touch /var/lock/subsys/openafs-client
	$AFS_POST_INIT
    fi
	;;

  stop)
    if [ ! "$afs_rh" -o -f /var/lock/subsys/openafs-client ]; then
	# Stop AFS
	echo "Stopping AFS services..... "

	if [ -x $KILLAFS ] ; then
		runcmd "Sending all processes using /afs the TERM signal ..." $KILLAFS TERM
		runcmd "Sending all processes using /afs the KILL signal ..." $KILLAFS KILL
	fi
	umount /afs

	# Unload the packaging style kmod if present, otherwise fallback
	# to the legacy style.
	if [ -f /lib/modules/`uname -r`/extra/openafs/openafs.ko ] ; then
		modprobe -r openafs
	else
		LIBAFS=`/sbin/lsmod | fgrep 'libafs'`
		if [ -n "$LIBAFS" ] ; then
			LIBAFS=`echo $LIBAFS | awk 'BEGIN { FS = " " } { print $1 }'`
			/sbin/rmmod $LIBAFS
		fi
	fi

	rm -f /var/lock/subsys/openafs-client
    fi
	;;

  restart)
	# Restart AFS
	$0 stop
	$0 start
	;;

  *)
	echo Usage: 'afs <start|stop|restart>'

esac

exit 0

action fool the Red Hat initscripts
""",


    "openafs-client-solaris-5.10.init":\
"""\
#!/bin/sh
#
# afs.rc: rc script for AFS on Solaris 10 platforms
#
# Install this script as /etc/init.d/afs.rc
# then make links like this:
# ln -s ../init.d/afs.rc /etc/rc0.d/K66afs
# ln -s ../init.d/afs.rc /etc/rc2.d/S70afs
#
CONFIG=/usr/vice/etc/config
AFSDOPT=$CONFIG/afsd.options
PACKAGE=$CONFIG/package.options

# EXTRAOPTS can be used to enable/disable AFSDB support (-afsdb)
# and Dynroot (dynamically-generated /afs) support (-dynroot).
EXTRAOPTS="-afsdb"

LARGE="-stat 2800 -dcache 2400 -daemons 5 -volumes 128"
MEDIUM="-stat 2000 -dcache 800 -daemons 3 -volumes 70"
SMALL="-stat 300 -dcache 100 -daemons 2 -volumes 50"

if [ -f $AFSDOPT ]; then
    OPTIONS=`cat $AFSDOPT`
else
    OPTIONS="$MEDIUM $EXTRAOPTS"
fi

# Need the commands ps, awk, kill, sleep
PATH=${PATH}${PATH:+:}/sbin:/bin:/usr/bin

killproc() {            # kill the named process(es)
      awkfield2='$2'
        pid=`ps -ef | awk "/$1/ && ! /awk/ {print $awkfield2}"`
        [ "$pid" != "" ] && kill -KILL $pid
}

generate_csdb() {
    if [ -f /usr/vice/etc/CellServDB.local -a -f /usr/vice/etc/CellServDB.dist ]; then
        if [ -h /usr/vice/etc/CellServDB ]; then
            rm -f /usr/vice/etc/CellServDB
        fi
        cat /usr/vice/etc/CellServDB.local /usr/vice/etc/CellServDB.dist >/usr/vice/etc/CellServDB
        chmod 644 /usr/vice/etc/CellServDB
    fi
}

case $1 in
'start')

#
# Make sure afs exists in /etc/name_to_sysnum
#
if grep -s "afs" /etc/name_to_sysnum > /dev/null; then
    echo "Entry for afs already exists in /etc/name_to_sysnum"
else
    echo "Creating entry for afs in /etc/name_to_sysnum"
    cp /etc/name_to_sysnum /etc/name_to_sysnum.orig
    sed '/nfs/i\
afs			65' /etc/name_to_sysnum > /tmp/name_to_sysnum
    mv /tmp/name_to_sysnum /etc/name_to_sysnum
    echo "Rebooting now for new /etc/name_to_sysnum to take effect"
    reboot
fi

## Check to see that /bin/isalist exists and is executable
if [ ! -x /bin/isalist ] ;then
      echo "/bin/isalist not executable"
      exit 1;
fi

## Determine if we are running the 64 bit OS
## If sparcv9 then the location of the afs and nfs extensions differ

case `/bin/isalist` in
    *amd64* )
              nfssrv=/kernel/misc/amd64/nfssrv
              afs=/kernel/fs/amd64/afs ;;
    *sparcv9* )
              nfssrv=/kernel/misc/sparcv9/nfssrv
              afs=/kernel/fs/sparcv9/afs ;;
          * )
              nfssrv=/kernel/misc/nfssrv
              afs=/kernel/fs/afs ;;
esac


#
# Load kernel extensions
#
# nfssrv has to be loaded first


if [ -f $nfssrv ]; then
      echo "Loading NFS server kernel extensions"
      modload $nfssrv
else
      echo "$nfssrv does not exist. Skipping AFS startup."
      exit 1
fi

## Load AFS kernel extensions

if [ -f $afs ]; then
      echo "Loading AFS kernel extensions"
      modload $afs
else
      echo "$afs does not exist. Skipping AFS startup."
      exit 1
fi

#
# Check that all of the client configuration files exist
#
generate_csdb
for file in /usr/vice/etc/afsd /usr/vice/etc/cacheinfo \
          /usr/vice/etc/ThisCell /usr/vice/etc/CellServDB
do
      if [ ! -f ${file} ]; then
              echo "${file} does not exist. Not starting AFS client."
              exit 1
      fi
done

#
# Check that the root directory for AFS (/afs)
# and the cache directory (/usr/vice/cache) both exist
#
for dir in `awk -F: '{print $1, $2}' /usr/vice/etc/cacheinfo`
do
      if [ ! -d ${dir} ]; then
              echo "${dir} does not exist. Not starting AFS client."
              exit 2
      fi
done

echo "Starting afsd"
/usr/vice/etc/afsd $OPTIONS

echo ;;

'stop')

afsroot=`awk -F: '{print $1}' /usr/vice/etc/cacheinfo` || exit 1
if /usr/sbin/mount | grep -q "$afsroot"; then
    echo "Unmounting $afsroot"
    /usr/sbin/umount $afsroot || exit 1

    echo "Stopping afsd"
    /usr/vice/etc/afsd -shutdown || exit 1

    afsid=`modinfo | awk '/afs filesystem/ {print $1}'` || exit 1
    echo "Unloading module id $afsid"
    modunload -i "$afsid"  || exit 1
fi
echo ;;

*)    echo "Invalid option supplied to $0"
      exit 1;;
esac
""",


    "openafs-client-solaris-5.11.init":\
"""\
#!/bin/sh
#
# afs.rc: rc script for AFS on Solaris 11 or OpenSolaris-based platforms
#
# Install this script as /etc/init.d/afs.rc
# then make links like this:
# ln -s ../init.d/afs.rc /etc/rc0.d/K66afs
# ln -s ../init.d/afs.rc /etc/rc2.d/S70afs
#
CONFIG=/usr/vice/etc/config
AFSDOPT=$CONFIG/afsd.options
PACKAGE=$CONFIG/package.options

# EXTRAOPTS can be used to enable/disable AFSDB support (-afsdb)
# and Dynroot (dynamically-generated /afs) support (-dynroot).
EXTRAOPTS="-afsdb"

LARGE="-stat 2800 -dcache 2400 -daemons 5 -volumes 128"
MEDIUM="-stat 2000 -dcache 800 -daemons 3 -volumes 70"
SMALL="-stat 300 -dcache 100 -daemons 2 -volumes 50"

if [ -f $AFSDOPT ]; then
    OPTIONS=`cat $AFSDOPT`
else
    OPTIONS="$MEDIUM $EXTRAOPTS"
fi

# Need the commands ps, awk, kill, sleep
PATH=${PATH}${PATH:+:}/sbin:/bin:/usr/bin

killproc() {            # kill the named process(es)
      awkfield2='$2'
        pid=`ps -ef | awk "/$1/ && ! /awk/ {print $awkfield2}"`
        [ "$pid" != "" ] && kill -KILL $pid
}

generate_csdb() {
    if [ -f /usr/vice/etc/CellServDB.local -a -f /usr/vice/etc/CellServDB.dist ]; then
        if [ -h /usr/vice/etc/CellServDB ]; then
            rm -f /usr/vice/etc/CellServDB
        fi
        cat /usr/vice/etc/CellServDB.local /usr/vice/etc/CellServDB.dist >/usr/vice/etc/CellServDB
        chmod 644 /usr/vice/etc/CellServDB
    fi
}


case $1 in
'start')

## Check to see that /bin/isalist exists and is executable
if [ ! -x /bin/isalist ] ;then
      echo "/bin/isalist not executable"
      exit 1;
fi

## Determine if we are running the 64 bit OS
## If sparcv9 then the location of the afs and nfs extensions differ

case `/bin/isalist` in
    *amd64* )
              nfssrv=/kernel/misc/amd64/nfssrv
              afs=/kernel/drv/amd64/afs ;;
    *sparcv9* )
              nfssrv=/kernel/misc/sparcv9/nfssrv
              afs=/kernel/drv/sparcv9/afs ;;
          * )
              nfssrv=/kernel/misc/nfssrv
              afs=/kernel/drv/afs ;;
esac


#
# Load kernel extensions
#
# nfssrv has to be loaded first


if [ -f $nfssrv ]; then
      echo "Loading NFS server kernel extensions"
      modload $nfssrv
else
      echo "$nfssrv does not exist. Skipping AFS startup."
      exit 1
fi

## Load AFS kernel extensions

if [ -f $afs ]; then
      if [ -f /kernel/drv/afs.conf ] ; then
          echo "Kernel afs.conf already exists"
      else
          echo "Creating kernel afs.conf"
          echo 'name="afs" parent="pseudo";' > /kernel/drv/afs.conf
      fi

      # load the module
      if grep '^afs ' /etc/name_to_major >/dev/null ; then
          echo "Loading AFS kernel extensions"
          modload $afs
	  # this can sometimes be necessary to get the /devices afs device to
	  # attach
	  update_drv afs
      else
          echo "Installing AFS driver and loading kernel extensions"
          add_drv -m '* 0666 root root' afs
      fi

      # Create the /dev/afs link
      if grep name=afs /etc/devlink.tab >/dev/null ; then
          echo "Entry for afs already exists in /etc/devlink.tab"
      else
          echo "Adding entry for afs in /etc/devlink.tab"
          echo "type=ddi_pseudo;name=afs;addr=0;minor=afs	\D" >> /etc/devlink.tab
	  devfsadm
      fi
else
      echo "$afs does not exist. Skipping AFS startup."
      exit 1
fi

#
# Check that all of the client configuration files exist
#
generate_csdb
for file in /usr/vice/etc/afsd /usr/vice/etc/cacheinfo \
          /usr/vice/etc/ThisCell /usr/vice/etc/CellServDB
do
      if [ ! -f ${file} ]; then
              echo "${file} does not exist. Not starting AFS client."
              exit 1
      fi
done

#
# Check that the root directory for AFS (/afs)
# and the cache directory (/usr/vice/cache) both exist
#

for dir in `awk -F: '{print $1, $2}' /usr/vice/etc/cacheinfo`
do
      if [ ! -d ${dir} ]; then
              echo "${dir} does not exist. Not starting AFS client."
              exit 2
      fi
done

echo "Starting afsd"
/usr/vice/etc/afsd $OPTIONS

echo ;;

'stop')

afsroot=`awk -F: '{print $1}' /usr/vice/etc/cacheinfo` || exit 1
if /usr/sbin/mount | grep -q "$afsroot"; then
    echo "Unmounting $afsroot"
    /usr/sbin/umount $afsroot || exit 1

    echo "Stopping afsd"
    /usr/vice/etc/afsd -shutdown || exit 1

    afsid=`modinfo | awk '/afs filesystem/ {print $1}'` || exit 1
    echo "Unloading module id $afsid"
    modunload -i "$afsid"  || exit 1
fi
echo ;;

*)    echo "Invalid option supplied to $0"
      exit 1;;
esac
""",


    "openafs-server.init":\
"""\
#!/bin/bash
#
# Copyright (c) 2014-2017, Sine Nomine Associates
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#----------------------------------------------------------------------
# Basic init script to start/stop the OpenAFS servers.
#----------------------------------------------------------------------
# chkconfig: 2345 49 51
#----------------------------------------------------------------------

if [ -f /etc/rc.d/init.d/functions ] ; then
    . /etc/rc.d/init.d/functions
    afs_rh=1
else
    # special (RedHat) functions not available...
    function echo_failure () { echo -n " - failed." ; }
    function echo_success () { echo -n " - successful." ; }
fi

is_on() {
    if  test "$1" = "on" ; then return 0
    else return 1
    fi
}

BOSSERVER_OPTIONS=""
SYSCNF=${SYSCNF:-/etc/sysconfig/openafs-server}
if [ -f $SYSCNF ] ; then
    . $SYSCNF
fi

BOS=${BOS:-/usr/afs/bin/bos}
BOSSERVER=${BOSSERVER:-/usr/afs/bin/bosserver}

start() {
    if [ ! "$afs_rh" -o ! -f /var/lock/subsys/openafs-server ]; then
        if test -x $BOSSERVER ; then
            echo "Starting AFS servers..... "
            $BOSSERVER $BOSSERVER_OPTIONS
            if [ $? -ne 0 ]; then
                echo "Failed to start bosserver!"
                exit 1
            fi
            test "$afs_rh" && touch /var/lock/subsys/openafs-server
            if is_on $WAIT_FOR_SALVAGE; then
                sleep 10
                while $BOS status localhost fs 2>&1 | grep 'Auxiliary.*salvaging'; do
                    echo "Waiting for salvager to finish..... "
                    sleep 10
                done
            fi
        fi
    fi
}

stop() {
    if [ ! "$afs_rh" -o -f /var/lock/subsys/openafs-server ]; then
        if  test -x $BOS ; then
            echo "Stopping AFS servers..... "
            $BOS shutdown localhost -localauth -wait
            pkill -HUP bosserver
        fi
        rm -f /var/lock/subsys/openafs-server
    fi
}

case "$1" in
  start)
      start
      ;;
  stop)
      stop
      ;;
  restart)
      $0 stop
      $0 start
      ;;
  *)
      echo $"Usage: $0 {start|stop|restart}"
      exit 1
esac
""",


}
