#!/usr/bin/python3

import argparse
import getpass
import os
import sys

def dismount(mount_dest):
    print('Dismounting '+ mount_dest)
    os.system('veracrypt -d '+ mount_dest)

def mount(device, mount_dest):
    password = getpass.getpass('Password: ')
    print('Mounting '+ device +' to '+ mount_dest)
    os.system('veracrypt --mount '+ device +' -p '+ password +' '+ mount_dest)

def format_device_letter(letter):
    return '/dev/sd'+ letter +'1'

def format_mount_dest(vera_num):
    return '/media/veracrypt'+vera_num

try:
    parser = argparse.ArgumentParser(description='VeraCrypt wrapper. By default mounts a VeraCrypt drive.')
    parser.add_argument('-d', dest='dismount', action='store_true', help='Dismount vera drive')
    parser.add_argument('-l', dest='device_letter', default='b', help='Device letter. Default=b (as in /dev/sdb1)')
    parser.add_argument('-m', dest='mount_vera_number', default='2', help='Mount destination veracrypt number. Default=2 (as in /media/veracrypt2)')
    args = parser.parse_args()
    
    device = format_device_letter(args.device_letter)
    mount_dest = format_mount_dest(args.mount_vera_number)
    
    if args.dismount:
        dismount(mount_dest)
    else:
        mount(device, mount_dest)

except KeyboardInterrupt:
    print('\n\nNevermind...')
    sys.exit()
