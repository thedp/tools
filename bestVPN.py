#!/usr/bin/python3

"""
TODO LIST:
    - before testing with speedtest, verify vpn is actually connected.
"""

import os
import sys
import argparse
import subprocess
from random import choice
from time import sleep

COLOR_NORM = '\033[0m'
COLOR_SUCCESS = '\033[0;32m'
COLOR_FAILURE = '\033[0;31m'

VPN_TIMEOUT_SEC = 10
VPN_MIN_DL_SPEED_MBPS = 2
VPN_POOL = ['NL 1', 'CZ_1']
SPEED_UNIT_MAP = {'Gbit/s':0.001, 'Mbit/s':1, 'Kbit/s':1000, 'bit/s':1000000}

SPEEDTEST_CLI_PATH = '/home/thedp/speedtest-cli/speedtest_cli.py'

FNULL = open(os.devnull, 'w')


def exec_cmd_blocking(cmd):
    output = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=FNULL, shell=True).communicate()
    return output[0].decode('utf-8')

def exec_cmd_with_timeout(full_cmd, timeout_sec):
    p = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=FNULL, shell=True)
    try:
        p.wait(timeout=timeout_sec)
        return True
    except subprocess.TimeoutExpired:
        p.terminate()
        return False

def kill_vpn():
    exec_cmd_blocking('sudo killall openvpn')
    sleep(5)

def disconnect_vpn(vpn_id):
    exec_cmd_blocking('sudo nmcli con down id "'+ vpn_id +'"')
    sleep(4)

def connect_vpn(vpn_id, timeout_sec):
    print('>> Connecting to "'+ vpn_id +'"... ', end='', flush=True)
    cmd = 'sudo nmcli con up id "'+ vpn_id +'"'
    status = exec_cmd_with_timeout(cmd, timeout_sec)
    if not status:
        print(COLOR_FAILURE +'it\'s crap'+ COLOR_NORM)
    else:
        print(COLOR_SUCCESS +'ok'+ COLOR_NORM)
    sleep(3)
    return status

def select_vpn(vpn_server_index):
    if vpn_server_index > -1:
        return VPN_POOL[vpn_server_index]
    return choice(VPN_POOL)

def get_dl_speed_mbps(result):
    """ result example:
    Ping: 345.46 ms
    Download: 8.97 bit/s
    Upload: 7.31 Mbit/s"
    """
    dl_line_list = ((result.split('\n'))[1].split(' '))
    speed = float(dl_line_list[1])
    unit = float(SPEED_UNIT_MAP[dl_line_list[2]])
    return speed / unit

def test_vpn_connection(min_dl_speed_mbps):
    print('>> Testing with speedtest... ', end='', flush=True)
    result = exec_cmd_blocking(SPEEDTEST_CLI_PATH + ' --simple')
    dl_speed_mbps = get_dl_speed_mbps(result)
    status = (True, COLOR_SUCCESS) if min_dl_speed_mbps <= dl_speed_mbps else (False,
            COLOR_FAILURE)
    print(status[1] + str(dl_speed_mbps) +'Mbps'+ COLOR_NORM)
    return status[0]

def show_vpn_servers_list():
    print('Listing available VPN servers.')
    print('Used with "--server <vpn_server_index>" flag.')
    for i in range(0, len(VPN_POOL)):
        print(str(i) +': '+ VPN_POOL[i])

###########

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='bestVPN 0.1 - Finds the best VPN server.')

    parser.add_argument('--list', dest='list_vpn_servers',
            action='store_true', help='List VPN servers, and exit')

    parser.add_argument('--server', dest='vpn_server_index', default='-1',
            help='vpn server index')

    parser.add_argument('--mbps', dest='min_mbps',
            default=VPN_MIN_DL_SPEED_MBPS,
            help='Change min. Mbps. Default='+ str(VPN_MIN_DL_SPEED_MBPS))

    parser.add_argument('--timeout', dest='timeout_sec',
            default=VPN_TIMEOUT_SEC,
            help='Change timeout in seconds. Default='+ str(VPN_TIMEOUT_SEC))

    parser.add_argument('--quick', dest='no_test', action='store_true',
            help='Just connect, no testing with speedtest')

    parser.add_argument('--test', dest='do_test_connection',
            action='store_true', help='Only tests existing connection with speedtest')

    args = parser.parse_args()

    vpn_server_index = int(args.vpn_server_index)
    VPN_MIN_DL_SPEED_MBPS = int(args.min_mbps)
    VPN_TIMEOUT_SEC = int(args.timeout_sec)

    if args.list_vpn_servers:
        show_vpn_servers_list()
        sys.exit()

    if args.do_test_connection:
        test_vpn_connection(VPN_MIN_DL_SPEED_MBPS)
        sys.exit()

    while True:
        try:
            vpn_id = select_vpn(vpn_server_index)
            if connect_vpn(vpn_id, VPN_TIMEOUT_SEC):
                if not args.no_test:
                    if test_vpn_connection(VPN_MIN_DL_SPEED_MBPS):
                        break
                else:
                    break
            disconnect_vpn(vpn_id)
        except KeyboardInterrupt:
            print('\nOk.. Bye.')
            sys.exit()
        except:
            raise
