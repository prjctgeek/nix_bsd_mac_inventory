#!/usr/bin/env python

"""
Rework device42 inventory script to use fabric for ssh connections
Parallel work will be done differently
"""

__version__ = "3.0"

# Import Fabric API
from fabric.api import *

#import custom modules
import util_uploader as uploader
import util_ip_operations as ipop
import module_linux as ml
import module_solaris as ms
import module_mac as mc
import module_freebsd as freebsd
import module_openbsd as openbsd
import module_aix as aix

def upload(data):
    name = None
    rest = uploader.Rest(BASE_URL, USERNAME, SECRET, DEBUG)

    # get hdd parts if any
    hdd_parts = {}
    for rec in data:
        if 'hdd_parts' in rec:
            hdd_parts.update(rec['hdd_parts'])
            data.remove(rec)

    # Upload device first and get name back
    for rec in data:
        if not 'macaddress' in rec:
            devindex = data.index(rec)
    rec = data[devindex]
    if DUPLICATE_SERIALS:
        result = rest.post_multinodes(rec)
    else:
        result = rest.post_device(rec)
    try:
        name = result['msg'][2]
    except:
        pass

    # upload IPs and MACs
    for rec in data:
        if not 'macaddress' in rec:
            pass
        elif 'ipaddress'in rec:
            if name and 'device' in rec:
                rec['device'] = name
            rest.post_ip(rec)
        elif 'port_name' in rec:
            if name and 'device' in rec:
                rec['device'] = name
            rest.post_mac(rec)
    # upload hdd_parts if any
    if hdd_parts:
        rest.post_parts(hdd_parts)
def get_linux_data():
    print '[+] Collecting data from: %s' % env.host_string
    linux = ml.GetLinuxData(GET_SERIAL_INFO, ADD_HDD_AS_DEVICE_PROPERTIES, ADD_HDD_AS_PARTS, \
                            GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = linux.main()
    if DEBUG:
        print 'Linux data: ', data
    return data

def get_solaris_data():
    solaris = ms.GetSolarisData(GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = solaris.main()
    if DEBUG:
        print 'Solaris data: ', data
    return data


def get_aix_data():
    aix = ms.GetAixData(GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = aix.main()
    if DEBUG:
        print 'Aix data: ', data
    return data

def get_openbsd_data():
    openbsd = ms.GetOpenbsdData(GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = openbsd.main()
    if DEBUG:
        print 'Openbsd data: ', data
    return data

def get_freebsd_data():
    freebsd = ms.GetFreebsdData(GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = freebsd.main()
    if DEBUG:
        print 'Freebsd data: ', data
    return data

def get_mac_data():
    mac = ms.GetMacData(GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, \
                            IGNORE_DOMAIN, UPLOAD_IPV6, GIVE_HOSTNAME_PRECEDENCE, DEBUG)
    data = mac.main()
    if DEBUG:
        print 'Mac data: ', data
    return data

def check_os():
    #global SUCCESS
    SUCCESS = False
    output = str(run("uname -a")).lower()
    if 'linux' in output:
        print '[+] Linux running @ %s ' % env.host_string
        data = get_linux_data()
    elif 'solaris' in msg or 'sunos' in msg:
        print '[+] Solaris running @ %s ' % ip
        data = get_solaris_data()
    elif 'freebsd' in msg:
        print '[+] FreeBSD running @ %s ' % ip
        data = get_freebsd_data()
    elif 'openbsd' in msg:
        print '[+] OpenBSD running @ %s ' % ip
        data = get_openbsd_data()
    elif 'darwin' in msg:
        print '[+] Mac OS X running @ %s' % ip
        data = get_mac_data()
    elif 'aix' in msg:
        print '[+] IBM AIX running @ %s' % ip
        data = get_aix_data()
    else:
        print '[!] Connected to SSH @ %s, but the OS cannot be determined.' % ip
        print '\tInfo: %s\n\tSkipping... ' % str(msg)
    if DICT_OUTPUT:
        return data
    #else:
    #    upload(data)

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
