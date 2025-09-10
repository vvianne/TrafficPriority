from mininet.net import Mininet
from mininet.cli import CLI
from mininet.cli import CLI
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel
import os  # Impor modul os

def create_topology():
    """
    Creates a simple Mininet topology with two hosts and one Open vSwitch.
    """
    # Running Open vSwitch service
    print("Starting Open vSwitch service...")
    os.system('service openvswitch-switch start')

    os.system('sleep 3')

    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink
    )

    print("Adding controller...")
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6653)

    print("Adding hosts and switch...")
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    s1 = net.addSwitch('s1')

    print("Creating links...")
    net.addLink(h1, s1)
    net.addLink(h2, s1)

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
