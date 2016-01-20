import sys
import os
import netaddr
import socket


class IP_Operations():
    def __init__(self, targets):
        self.ipscope = None
        self.targets = targets

    def sort_ip(self):
        ip_addresses = []
        if ',' in self.targets:
            self.ipscope = self.targets.split(',')
        else:
            self.ipscope = [self.targets]
        for scope in self.ipscope:
            #cannot mix CIDR and iprange notation
            if '/'in scope  and '-' in scope:
                msg =  '[!] Malformed target IP %  - mixed CIDR and dash' % scope
                print msg
                sys.exit()

            username = ''
            # Split out username and IP or hostname
            if scope.count('@') == 1:
                # split out username and IP address/hostname
                parts = scope.split('@')
                username = parts[0].strip()
                scope = parts[1]
            elif scope.count('@') > 1:
                msg = '[!] Mailformed target % - multiple usernames ' % scope
                print msg
                sys.exit()
            # CIDR
            if '/' in scope:
                try:
                    mask = int(scope.split('/')[1])
                except:
                    msg =  '[!] Illegal CIDR mask - %.' % scope
                    print msg
                    sys.exit()
                if not  mask in range(1, 32):
                    msg =  '[!] Illegal CIDR mask - %.' % scope
                    print msg
                    sys.exit()
                valid = self.check_valid_ip(scope.split('/')[0])
                if valid:
                    for ip in netaddr.IPNetwork(scope).iter_hosts():
                        ip_addresses.append(username+'@'+str(ip))
                else:
                    msg =  '[!] Malformed target IP %.' % scope
                    print msg
                    sys.exit()

            # iprange
            elif '-' in scope:
                iprange = scope.split('-')
                if len(iprange) != 2:
                    msg =  '[!] Malformed target IP %.' % scope
                    print msg
                    sys.exit()
                else:
                    for ip in iprange:
                        valid = self.check_valid_ip(ip)
                        if not valid:
                            msg =  '[!] Malformed target IP %.' % ip
                            print msg
                            sys.exit()
                    start, end = iprange
                    ip_list = list(netaddr.iter_iprange(start, end))
                    for ip in ip_list:
                        ip_addresses.append(username+'@'+str(ip))

            # SINGLE IP
            else:
                valid = self.check_valid_ip(scope)
                if not valid:
                    msg =  '[!] Malformed target IP %.' % scope
                    print msg
                    sys.exit()
                else:
                    ip_addresses.append(username+'@'+scope)

        return ip_addresses

    def check_valid_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return 1
        except:
            return 0
