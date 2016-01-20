#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 abrook <abrook@bsd.uchicago.edu>
#
# Distributed under terms of the MIT license.

"""
Rework device42 inventory script to use fabric for ssh connections
Parallel work will be done differently
"""

__version__ = "3.0"

from fabric.api import *

#import custom modules
import util_uploader as uploader
import util_ip_operations as ipop

def check_os():
    #global SUCCESS
    SUCCESS = False
    output = str(run("uname -a")).lower()
    if 'vmkernel' in output:
        print '[+] ESXi running @ %s ' % env.host_string
    elif 'linux' in output:
        print '[+] Linux running @ %s ' % env.host_string
        data = get_linux_data(ip, usr, pwd)
        return data
    elif 'solaris' in msg or 'sunos' in msg:
        print '[+] Solaris running @ %s ' % ip
    elif 'freebsd' in msg:
        print '[+] FreeBSD running @ %s ' % ip
    elif 'openbsd' in msg:
        print '[+] OpenBSD running @ %s ' % ip
    elif 'darwin' in msg:
        print '[+] Mac OS X running @ %s' % ip
    elif 'aix' in msg:
        print '[+] IBM AIX running @ %s' % ip
    else:
        print '[!] Connected to SSH @ %s, but the OS cannot be determined.' % ip
        print '\tInfo: %s\n\tSkipping... ' % str(msg)
    return

def main():
    if TARGETS:
        ipops = ipop.IP_Operations(TARGETS)
        ip_scope = ipops.sort_ip()

        if not ip_scope:
            msg =  '[!] Empty IP address scope! Please, check target IP address[es].'
            print msg
            sys.exit()
        else:
            with settings(
                hide('warnings', 'running', 'stdout', 'stderr'),
                warn_only=True,
                shell="/bin/sh -c"
            ):
                env.skip_bad_hosts=True
                execute(check_os,hosts=ip_scope)
            sys.exit(0)

if __name__ == '__main__':
    from module_shared import *
    main()
    sys.exit()
else:
    # you can use dict_output if called from external script (starter.py)
    from module_shared import *

