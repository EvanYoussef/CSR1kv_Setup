#!/usr/bin/python3

## import required modules
from ncclient import manager
import xml.dom.minidom
import getpass
import re

# Allow the user to define credentials and verify they appear valid
def credential_valid():
      
    confirm = 'n'
    print("Provide host information and credentials, default values are []s, press enter to accept")
    while confirm == 'n':
        
        # Ask the human for the information required to connect to device
        global dev_addr
        dev_addr = input("Provide the name or IP address for the target device: ")
        global dev_port
        dev_port = input("Please provide the port [830]: ") or 830
        global dev_name
        dev_name = str(input("Please provide the username [cisco]: ") or 'cisco')
        global dev_pass
        dev_pass = str(getpass.getpass(prompt="Please provide the password [cisco123!]: ", stream=None) or 'cisco123!')
    
        # Ask the human if the values they provided are correct
        check = str(input(f"Please confirm you wish to connect to {dev_addr} on port {dev_port} as user {dev_name} (Y to confirm)? "))
        # If the human provides 'y' check the port number
        if check.lower()[0] == 'y':
            confirm = 'y'

            # verify the address provided is valid ip address or hostname
            if re.search("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$", dev_addr):
                #print(dev_addr,"appears to be a valid ipv4 address")
                confirm = 'y'
            elif re.search("^[a-fA-F0-9:]+$", dev_addr):
                #print(dev_addr,"appears to be a valid ipv6 address")
                confirm = 'y'
            elif re.search("^[a-zA-Z0-9][-a-zA-Z.0-9]+$", dev_addr):
                #print(dev_addr,"appears to be a valid hostname")
                confirm = 'y'
            else:
                print(dev_addr,"does not appear to be a valid hostname or IP address.")
                confirm ='n'

            # confirm dev_port is an integer
            try:
                dev_port = int(dev_port)
                # if dev_port is a number, verify it is a valid port number
                if dev_port <= 0 or dev_port >= 65536:
                    # if we get an invalid port number tell the human what we expect
                    print(f"Port {dev_port} is not valid, must be 1-65535")
                    confirm = 'n'
            except:
                # if we get a string, tell the human what we expect
                print(dev_port,"is not an integer or valid port number")
                confirm = 'n'
        # If the human provides anything other than 'y' recycle
        else:
            confirm ='n'
    # debugging, print all values
    #print(check, dev_addr, dev_port, dev_name, dev_pass, confirm)

    

# Ask user for credentials and connection information
credential_valid()
print("...Connecting to", dev_addr, "as", dev_name)
m = manager.connect(
host = dev_addr,
port = dev_port,
username = dev_name,
password = dev_pass,
hostkey_verify=False
)

# store the available running configuration in the netconf_config string
netconf_filter = """
<filter>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native" />
</filter>
"""
netconf_config = str(m.get_config(source="running", filter=netconf_filter))

# Pull the current hostname from the netconf_config and present it to the user
cur_hostname = re.search('(?<=<hostname>)(.*)(?=</hostname>)', netconf_config)
print("The current hostname is:",cur_hostname.group())

# Ask the user if they want to change it to the stored hostname
name_select = str(input("Do you want to change it to 'super.router'? "))
if name_select.lower()[0] == 'y':
    
    netconf_hostname = """
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<hostname>super.router</hostname>
</native></config>
"""
    netconf_reply = m.edit_config(target="running", config=netconf_hostname)
else:
    print("Leaving hostname",cur_hostname.group())


netconf_loopback = """
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<interface>
<Loopback>
<name>1</name>
<description>My NETCONF loopback</description>
<ip>
<address>
<primary>
<address>10.1.1.1</address>
<mask>255.255.255.0</mask>
</primary>
</address>
</ip>
</Loopback>
</interface>
</native>
</config>
"""
netconf_reply = m.edit_config(target="running", config=netconf_loopback)

netconf_loopback2 = """
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<interface>
<Loopback>
<name>2</name>
<description>My second NETCONF loopback</description>
<ip>
<address>
<primary>
<address>172.16.1.1</address>
<mask>255.255.255.0</mask>
</primary>
</address>
</ip>
</Loopback>
</interface>
</native>
</config>
"""
netconf_reply = m.edit_config(target="running", config=netconf_loopback2)

netconf_loopback3 = """
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
<interface>
<Loopback>
<name>3</name>
<description>My third NETCONF loopback</description>
<ip>
<address>
<primary>
<address>209.165.200.65</address>
<mask>255.255.255.252</mask>
</primary>
</address>
</ip>
</Loopback>
</interface>
</native>
</config>
"""
netconf_reply = m.edit_config(target="running", config=netconf_loopback3)
print(xml.dom.minidom.parseString(netconf_reply.xml).t
