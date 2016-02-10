import sys
import os
import ast
import ConfigParser
import util_locator as ul

APP_DIR = ul.module_path()
CONFIGFILE = os.path.join(APP_DIR, 'inventory.cfg')


def get_settings():
    cc = ConfigParser.RawConfigParser()
    if os.path.isfile(CONFIGFILE):
        cc.readfp(open(CONFIGFILE,"r"))
    else:
        print '\n[!] Cannot find config file. Exiting...'
        sys.exit()

    # modules
    mod_linux      = cc.getboolean('modules', 'linux')
    mod_solaris    = cc.getboolean('modules', 'solaris')
    mod_mac        = cc.getboolean('modules', 'mac')
    mod_bsd        = cc.getboolean('modules', 'bsd')
    mod_aix        = cc.getboolean('modules', 'aix')
    # settings ------------------------------------------------------------------------
    base_url       = cc.get('settings', 'base_url')
    username       = cc.get('settings', 'username')
    if username in ('None',' ',''):
        username = raw_input('Device42 username: ')
    secret         = cc.get('settings', 'secret')
    if secret in ('None',' ',''):
        import getpass
        secret=getpass.getpass('Device42 password for '+username+': ')
    #targets  ------------------------------------------------------------------------
    targets        = cc.get('targets', 'targets')
    # credentials  --------------------------------------------------------------------
    use_key_file   = cc.getboolean('credentials', 'use_key_file')
    key_file       = cc.get('credentials', 'key_file')
    credentials    = cc.get('credentials', 'credentials')
    #ssh settings   ------------------------------------------------------------------
    timeout        = cc.get('ssh_settings', 'timeout')
    #options   ------------------------------------------------------------------------
    get_serial_info             = cc.getboolean('options', 'get_serial_info')
    get_hardware_info           = cc.getboolean('options', 'get_hardware_info')
    get_os_details              = cc.getboolean('options', 'get_os_details')
    get_cpu_info                = cc.getboolean('options', 'get_cpu_info')
    get_memory_info             = cc.getboolean('options', 'get_memory_info')
    ignore_domain               = cc.getboolean('options', 'ignore_domain')
    upload_ipv6                 = cc.getboolean('options', 'upload_ipv6')
    duplicate_serials           = cc.getboolean('options', 'duplicate_serials')
    add_hdd_as_device_properties= cc.getboolean('options', 'add_hdd_as_device_properties')
    add_hdd_as_parts            = cc.getboolean('options', 'add_hdd_as_parts')
    give_hostname_precedence    = cc.getboolean('options', 'give_hostname_precedence')
    debug                       = cc.getboolean('options', 'debug')
    threads                     = cc.get('options', 'threads')
    dict_output                 = cc.getboolean('options', 'dict_output')
    run_parallel                = cc.getboolean('options', 'run_parallel')

    return   mod_linux, mod_solaris,  mod_mac, mod_bsd, mod_aix, base_url, username, secret, targets, \
                use_key_file, key_file, credentials,  timeout, get_serial_info, duplicate_serials,\
                add_hdd_as_device_properties, add_hdd_as_parts, get_hardware_info, get_os_details, get_cpu_info, \
                get_memory_info,ignore_domain, upload_ipv6, debug, threads,  dict_output, give_hostname_precedence, run_parallel

caller = os.path.basename(sys._getframe().f_back.f_code.co_filename)

if caller == 'main.py':
    MOD_LINUX, MOD_SOLARIS, MOD_MAC, MOD_BSD, MOD_AIX, BASE_URL, \
    USERNAME, SECRET, TARGETS, USE_KEY_FILE, KEY_FILE, \
    CREDENTIALS, TIMEOUT, GET_SERIAL_INFO, DUPLICATE_SERIALS, ADD_HDD_AS_DEVICE_PROPERTIES, \
    ADD_HDD_AS_PARTS, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, IGNORE_DOMAIN, \
    UPLOAD_IPV6, DEBUG, THREADS, DICT_OUTPUT, GIVE_HOSTNAME_PRECEDENCE, RUN_PARALLEL = get_settings()
    TIMEOUT         = int(TIMEOUT)

else:
    if len(sys.argv) == 5:
        MOD_LINUX, MOD_SOLARIS, MOD_MAC, MOD_BSD, MOD_AIX,  BASE_URL, \
        USERNAME, SECRET, xTARGETS, xUSE_KEY_FILE, xKEY_FILE, \
        xCREDENTIALS, TIMEOUT, GET_SERIAL_INFO, DUPLICATE_SERIALS, ADD_HDD_AS_DEVICE_PROPERTIES, \
        ADD_HDD_AS_PARTS, GET_HARDWARE_INFO, GET_OS_DETAILS, GET_CPU_INFO, GET_MEMORY_INFO, IGNORE_DOMAIN, \
        UPLOAD_IPV6, DEBUG, THREADS, DICT_OUTPUT, GIVE_HOSTNAME_PRECEDENCE, RUN_PARALLEL = get_settings()
        TIMEOUT         = int(TIMEOUT)
        TARGETS         = sys.argv[1].strip()
        USE_KEY_FILE    = ast.literal_eval(sys.argv[2].strip().capitalize())
        KF              = sys.argv[3].strip()
        if KF.lower() in ('none', 'false', 'true'):
            KEY_FILE        = ast.literal_eval(KF.capitalize())
        else:
            KEY_FILE    = KF
            if not os.path.exists(KEY_FILE):
                print '[!] Cannot find key file: "%s"' % KEY_FILE
                print '[!] Exiting...'
                sys.exit()
        CR              = sys.argv[4].strip()
        if CR.lower() in ('none', 'false', 'true'):
            CREDENTIALS = ast.literal_eval(CR)
        else:
            env.password = CR

    else:
        print '\n[!] Wrong number of args. '
        print ' '.join(sys.argv[1:])
        print '[-] main.py USERNAME@TARGET USE_KEY_FILE KEY_FILE CREDENTIALS'
        sys.exit()
