# python/td_startup.py

import sys
import socket
import subprocess
import re

def touchdesigner_operator(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print(f'From: {args[0].name}.')
            return result
        except Exception as e:
            print(f'Error: {e}')
    return wrapper

@touchdesigner_operator
def set_resolution(op, width, height):
    if hasattr(op, 'par'):
        op.par.w = width
        op.par.h = height
    else:
        raise AttributeError('Operator does not have resolution parameters.')


def get_current_interpreter_info():
    interpreter_path = sys.executable
    python_version = sys.version
    return interpreter_path, python_version


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip


def parse_arp_output(output):
    arp_entry_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f-]+)\s+(\w+)')    
    entries = arp_entry_pattern.findall(output)
    return entries


def get_arp_table():
    result = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    arp_table = parse_arp_output(output)
    return arp_table


def format_arp_table_to_string(arp_table):
    formatted_string = 'Internet Address, Physical Address, Type\n\n'
    for entry in arp_table:
        formatted_string += f"{entry[0]}, \t{entry[1]}, \t{entry[2]}\n"
    return formatted_string


class NetworkInterface:
    def __init__(self):
        self.devices = []

    def add_device(self, ip, hostname):
        self.devices[ip] = hostname

    def display_devices(self):
        for ip, hostname in self.devices.items():
            print(f'IP: {ip} - Hostname: {hostname}')
        return self.devices
    
    def get_own_details(self):
        ip = get_local_ip()
        hostname = socket.gethostname()
        return ip, hostname
    


# Executes on startup of ig20-iegeekcam.toe

def onStart():

    project_component = op('/project1')
    text_display_op = op('/project1/ig20_iegeekcam/ip_display/text_tex')

    set_resolution(project_component, 640, 720)

    text_display_op.par.text = '0.0.0.0'
    path, version = get_current_interpreter_info()

    print('Starting scanner and camera instance.')
    print(f'Python Interpreter Path: {path}')
    print(f'Python Version: {version}')

    return
