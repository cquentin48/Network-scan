from typing import Literal

import asyncio

from datetime import datetime

import xml.etree.ElementTree as ET

import ipaddress

import winreg as wr

import netifaces as ni

from ping3 import ping

from pyipp.exceptions import IPPConnectionError
from pyipp import IPP

import requests

import pychromecast

import zeroconf



async def detect_printer(ip_addr: str):
    """
    Check if the device is a printer

    :type ip_addr: str
    :param ip_addr: IP address of the device
    """
    async with IPP(f"ipp://{ip_addr}/ipp/print") as ipp:
        await ipp.printer()


def is_device_orange_tv_box(ip_addr: str) -> Literal['Décodeur TV', '']:
    """Check if the device is an orange TV Box

    :type ip_addr: str
    :param ip_addr: device IP address

    :rtype:
        Literal
    """

    with requests.get(f'http://{ip_addr}:8080/BasicDeviceDescription.xml', timeout=5) as response:
        if response.ok:
            xml_tree = ET.ElementTree(ET.fromstring(response.text))
            device_name = xml_tree.find(
                './/{urn:schemas-upnp-org:device-1-0}friendlyName')
            return 'Décodeur TV' if 'décodeur' in device_name.text.lower() else ''
        return ''


def get_device_type(ip_addr: str, router: str) ->\
    Literal['Routeur', 'Décodeur TV', 'Imprimante', 'Ordinateur']:
    """
    Return the device type associated with an ip address

    :type ip_addr: str
    :param ip_addr: device IP Address

    :type router: str
    :param router: router IP address
    """
    if str(ip_addr) == router:
        return 'Routeur'

    device_name = is_device_orange_tv_box(ip_addr)
    if device_name:
        return device_name

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(detect_printer(str(ip_addr)))
        return "Imprimante" if str(ip_addr) != router else "Routeur"

    except IPPConnectionError as _:
        return "Routeur" if router == str(ip_addr) else 'Ordinateur'


def get_connection_name_from_guid(iface_guids: list) -> dict:
    """
    Returns the networks connections from a windows device

    :type ifaceguids: list
    :param ifaceguids: Interfaces found with netiface
    """
    interfaces = ['(unknown)' for i in range(len(iface_guids))]
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(
        reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    for index, interface in enumerate(iface_guids):
        try:
            reg_subkey = wr.OpenKey(reg_key, interface + r'\Connection')
            interfaces[index] = {
                'reg_key': interface,
                'name': wr.QueryValueEx(reg_subkey, 'Name')[0]
            }
        except FileNotFoundError:
            pass
    if '(unknown)' in interfaces:
        index = interfaces.index('(unknown)')
        del interfaces[index]
    return interfaces


def get_network_ip() -> tuple[str, str]:
    """
    Generates the IP network address alongside every possible
    addresses of the network
    """

    network_interfaces = ni.interfaces()
    res = get_connection_name_from_guid(network_interfaces)
    wifi = [net for net in res if net['name'] == 'Wi-Fi'][0]
    
    interface_name = wifi['reg_key']

    addrs = ni.ifaddresses(interface_name)[ni.AF_INET][0]
    network_ip = ipaddress.IPv4Network(
        f'{addrs["addr"]}/{addrs["netmask"]}', strict=False)
    return (addrs, network_ip)


def detect_smart_tvs(valid_hosts: dict) -> dict:
    """Detect Smart TV in the network

    :type valid_hosts: dict
    :param valid_hosts: IP adress with devices linked

    :rtype:
        dict
    """
    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(
        pychromecast.SimpleCastListener(), zconf)
    browser.start_discovery()
    browser.stop_discovery()

    for tv_device in browser.devices:
        ip_addr = tv_device.host
        valid_host = [
            valid_host for valid_host in valid_hosts if valid_host['Addresse IP'] == ip_addr]
        if len(valid_host) > 0:
            valid_host = valid_host[0]
            valid_host['type'] = 'TV Connectée'
        else:
            valid_hosts[len(valid_hosts)+1] = {
                'Addresse IP': ip_addr,
                'type': 'TV connectée'
            }

    return valid_hosts


def get_valid_ip_addresses(
    network_ip_addresses: list,
    router: str,
    ip_address: str
):
    """
    List every IP address linked with a physical device

    :type network_ip_addresses: list
    :param network_ip_addresses:

    :type router: str
    :param router: router IP address

    :type ip_address: str
    :param ip_address: Current device IP address
    """
    valid_hosts = {}
    for host in network_ip_addresses:
        print(f"Ping host : {str(host)}")
        if ping(str(host), timeout=1):
            valid_hosts[len(valid_hosts)+1] = {
                'Addresse IP': str(host),
                'type': get_device_type(str(host), router)
            }
    valid_hosts[len(valid_hosts)+1] = {
        'Addresse IP': str(ip_address),
        'type': 'Ordinateur'
    }

    valid_hosts = detect_smart_tvs(valid_hosts)


def main():
    """
    Software main functions
    """
    (network, ip_addresses) = get_network_ip()

    hosts = list(network.hosts())
    router = ni.gateways()['default'][ni.AF_INET][0]

    before_op = datetime.now()

    valid_hosts = {}
    for host in hosts:
        print(f"Ping host : {str(host)}")
        if ping(str(host), timeout=1):
            valid_hosts[len(valid_hosts)+1] = {
                'Addresse IP': str(host),
                'type': get_device_type(str(host), router)
            }
    valid_hosts[len(valid_hosts)+1] = {
        'Addresse IP': str(ip_addresses['addr']),
        'type': 'Ordinateur'
    }

    valid_hosts = detect_smart_tvs(valid_hosts)

    after_op = datetime.now()
    duration = after_op-before_op
    print(str(duration))


if __name__ == 'main':
    main()
