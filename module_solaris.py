# Import Fabric API
from fabric.api import *

class GetSolarisData():
    def __init__(self, GET_SERIAL_INFO, GET_HARDWARE_INFO, GET_OS_DETAILS, \
                    GET_CPU_INFO, GET_MEMORY_INFO, IGNORE_DOMAIN, UPLOAD_IPV6, DEBUG):
        self.GET_SERIAL_INFO    = GET_SERIAL_INFO
        self.GET_HARDWARE_INFO  = GET_HARDWARE_INFO
        self.GET_OS_DETAILS     = GET_OS_DETAILS
        self.GET_CPU_INFO       = GET_CPU_INFO
        self.GET_MEMORY_INFO    = GET_MEMORY_INFO
        self.IGNORE_DOMAIN      = IGNORE_DOMAIN
        self.UPLOAD_IPV6        = UPLOAD_IPV6
        self.DEBUG              = DEBUG
        self.sysData    = {}
        self.allData    = []

    def main(self):
        self.get_sys()
        self.get_CPU()
        self.get_RAM()
        self.allData.append(self.sysData)
        self.get_IP()
        return self.allData

    def execute(self, cmd):
        # Since there seems to be no sudo commands for this module
        output = run(cmd)
        data_err = output.stderr
        data_out = output.stdout
        return data_out.splitlines(),data_err.splitlines()

    def get_CPU(self):
        if self.GET_CPU_INFO:
            data_out, data_err = self.execute("/usr/bin/kstat cpu_info")
            if not data_err:
                cpu_ids = []
                core_ids = []
                for rec in data_out:
                    if 'clock_MHz' in rec:
                        cpupower = rec.split()[1].strip()
                    if 'chip_id' in rec:
                        cpu_ids.append(rec.split()[1].strip())
                    if 'core_id'in rec:
                        core_ids.append(rec.split()[1].strip())
                cpucount = len(set(cpu_ids))
                cpucores  = len(set(core_ids))
                self.sysData.update({'cpupower':cpupower})
                self.sysData.update({'cpucount':cpucount})
                self.sysData.update({'cpucore':cpucores})
            else:
                print data_err

    def get_RAM(self):
        if self.GET_MEMORY_INFO:
            data_out, data_err = self.execute("/usr/sbin/prtconf")
            if not data_err:
                for rec in data_out:
                    if 'Memory ' in rec:
                        memory = (rec.split(':')[1]).split()[0]
                        self.sysData.update({'memory':memory})
            else:
                print 'Error: ', data_err

    def get_name(self):
        data_out, data_err = execute("/usr/bin/hostname")
        if not data_err:
            return data_out[0].strip()
        else:
            print 'Error: ', data_err

    def get_macs(self):
        macs = {}
        data_out, data_err = self.execute("/usr/sbin/dladm show-phys -m")
        if not data_err:
            for rec in data_out[1:]:
                nic, slot, address, in_use, client = rec.split()
                # dladm returns MACs in wrong format
                if address:
                    raw = address.split(':')
                    address = ':'.join([x if len(x)==2 else ('0'+x) for x in raw])
                macs.update({nic:address})
            return macs
        else:
            data_out, data_err = self.execute("/usr/sbin/arp -a")
            if not data_err:
                for rec in data_out[1:]:
                        nic = rec.split()[0]
                        mac = rec.split()[-1]
                        macs.update({nic:mac})
                return macs
            else:
                print 'Error: ', data_err

    def get_IP(self):
        macs = self.get_macs()
        data_out, data_err = self.execute("/usr/sbin/ifconfig -a")
        if not data_err:
            name = self.get_name()
            n = 0
            for x in range(len(data_out)):
                raw = data_out[n:n+2]
                if raw:
                    try:
                        a, i = raw
                    except:
                        pass
                    else:
                        nic = a.split()[0].strip(':')
                        ip = i.split()[1]
                        if ip not in ('', ' ') and nic not in ('lo0'):
                            mac = macs[nic]
                            nicData = {}
                            macData = {}
                            if not mac:
                                mac = ''
                            if '/' in ip: # ipv6
                                ip = ip.split('/')[0]
                            nicData.update({'ipaddress':ip})
                            nicData.update({'macaddress':mac})
                            nicData.update({'device':name})
                            nicData.update({'tag':nic})
                            self.allData.append(nicData)
                            if mac != '':
                                macData.update({'macaddress':mac})
                                macData.update({'port_name':nic})
                                macData.update({'device':name})
                                self.allData.append(macData)
                n += 2
        else:
            print 'Error: ', data_err

    def get_sys(self):
        data_out, data_err = self.execute("uname -X")
        if not data_err:
            for rec in data_out:
                if 'System ' in rec:
                    if self.GET_OS_DETAILS:
                        os = rec.split('=')[1].strip()
                        self.sysData.update({'os':os})
                if 'KernelID ' in rec:
                    if self.GET_OS_DETAILS:
                        version = rec.split('=')[1].strip()
                        self.sysData.update({'osverno':version})
                if 'Release ' in rec:
                    if self.GET_OS_DETAILS:
                        version = rec.split('=')[1].strip()
                        self.sysData.update({'osver':version})
                if 'Node ' in rec:
                    name = rec.split('=')[1].strip()
                    self.sysData.update({'name':name})
        else:
            print 'Error: ', data_err
        data_out, data_err = self.execute("/usr/sbin/smbios -t SMB_TYPE_SYSTEM")
        if not data_err:
            for rec in data_out:
                if 'Manufacturer:' in rec:
                    manufacturer = rec.split(':')[1].strip()
                    for mftr in ['VMware, Inc.', 'Bochs', 'KVM', 'QEMU', 'Microsoft Corporation', 'Xen', 'innotek',  'innotek GmbH']:
                        if mftr.lower() == manufacturer.lower():
                            manufacturer = 'virtual'
                            self.sysData.update({'manufacturer':'virtual'})
                            break
                        if manufacturer != 'virtual':
                            self.sysData.update({'manufacturer':manufacturer})
                if 'Product:' in rec:
                    if self.GET_HARDWARE_INFO:
                        hardware = rec.split(':')[1].strip()
                        self.sysData.update({'hardware':hardware})
                if 'Serial ' in rec:
                    if self.GET_SERIAL_INFO:
                        serial = rec.split(':')[1].strip()
                        self.sysData.update({'serial_no':serial})
                if 'UUID' in rec:
                    uuid = rec.split(':')[1].strip()
                    self.sysData.update({'uuid':uuid})
        else:
            print 'Error: ', data_err
