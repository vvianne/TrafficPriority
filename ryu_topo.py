from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
import os  # Import modul os

def create_topology():
    """
    Creates a simple Mininet topology with two hosts and one Open vSwitch.
    """
    # Running Open vSwitch service
    print("Starting Open vSwitch service...")
    os.system('service openvswitch-switch start')

    os.system('sleep 3')

    # Create the Mininet instance
    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink
    )

    # Add the controller
    print("Adding controller...")
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6653)

    print("Adding hosts and switches...")
    # Add the managed hosts and switch (use OpenFlow13 for compatibility with Ryu v1.3)
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    s1 = net.addSwitch('s1', protocols='OpenFlow13')

    # Add the unmanaged hosts and switch (use OpenFlow13)
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')

    # Create links between hosts and switches
    # print("Creating links...")
    # net.addLink(h1, s1)
    # net.addLink(h2, s1)
    print("Creating links...")
    # Managed network links
    net.addLink(h1, s1, cls=TCLink, bw=10, delay='1ms')
    net.addLink(h2, s1, cls=TCLink, bw=10, delay='1ms')

    # Unmanaged network links
    net.addLink(h3, s2, cls=TCLink, bw=10, delay='1ms')
    net.addLink(h4, s2, cls=TCLink, bw=10, delay='1ms')

    print("Starting network...")
    net.start()

    print("Testing network connectivity...")
    net.pingAll()

    print("Running CLI...")
    CLI(net)

    print("Stopping network...")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
