import setuptools
from setuptools import find_packages

setuptools.setup(
    name="Analyse de réseau",
    packages=find_packages(),
    requires=[
        'asyncio',
        'ipaddress',
        'netifaces',
        'ping3',
        'psutil',
        'pyipp',
        'pychromecast',
        'winreg'
    ],
    author="Quentin CHAPEL",
    author_email="chapelquen@gmail.com"
)
