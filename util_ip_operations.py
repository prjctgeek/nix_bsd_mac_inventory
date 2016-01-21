import sys
import os
import netaddr
import socket


class IP_Operations():
    def __init__(self, targets, credentials):
        self.ipscope = None
        self.passwords = None
        self.targets = targets
        self.credentials = credentials

    def sort_ip(self):
        ip_addresses = []
        passwords = {}

        # Split targets
        if ',' in self.targets:
            self.ipscope = self.targets.split(',')
        else:
            self.ipscope = [self.targets]

        # Split entered in credentials
        if self.credentials:
            if ',' in self.credentials:
                self.credentials = self.credentials.split(',')
            else:
                self.credentials = [self.credentials]
            # Make credentials a dictionary
            creds = {}
            for rec in self.credentials:
                cred = rec.split(':')
                creds[cred[0].strip()] = cred[1].strip()
            self.credentials = creds

        for scope in self.ipscope:
            #cannot mix CIDR and iprange notation
            if '/'in scope  and '-' in scope:
                msg =  '[!] Malformed target IP %  - mixed CIDR and dash' % scope
                print msg
                sys.exit()

            scope = scope.strip()
            username = ''
            # Split out username and IP or hostname
            if scope.count('@') == 1:
                # split out username and IP address/hostname
                username,scope = scope.split('@')
                username = username+'@'
            elif scope.count('@') > 1:
                msg = '[!] Mailformed target % - multiple usernames ' % scope
                print msg
                sys.exit()

            # Find port if it's given in the target list
            # Otherwise assume 22
            port = ':22'
            if ':' in scope:
                scope, port = scope.split(':')
                port = ':'+port

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
                        ip_addresses.append(username+str(ip)+port)
                        # look for the username without the @ sign
                        if username.replace('@','') in self.credentials:
                            passwords[username+str(ip)+port] = self.credentials[username.replace('@','')]
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
                        ip_addresses.append(username+str(ip)+port)
                        # look for the username without the @ sign
                        if username.replace('@','') in self.credentials:
                            passwords[username+str(ip)+port] = self.credentials[username.replace('@','')]

            # SINGLE IP
            else:
                valid = self.check_valid_ip(scope)
                if not valid:
                    msg =  '[!] Malformed target IP %.' % scope
                    print msg
                    sys.exit()
                else:
                    ip_addresses.append(username+scope+port)
                    # look for the username without the @ sign
                    if username.replace('@','') in self.credentials:
                        passwords[username+str(scope)+port] = self.credentials[username.replace('@','')]

        return ip_addresses, passwords

    def check_valid_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return 1
        except:
            return 0
