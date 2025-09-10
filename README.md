# Traffic Prioritization with Ryu in Mininet

This project demonstrates a Software-Defined Networking (SDN) implementation to prioritize network traffic based on application type. Using the Ryu controller and the Mininet network emulator, the system differentiates between high-priority video traffic and low-priority file transfers, ensuring a better Quality of Service (QoS) for real-time video streams.

---

### Key Features

* **Traffic Classification**: The Ryu controller inspects TCP packet headers to identify traffic based on destination port numbers.
* **Prioritization**: OpenFlow rules are dynamically installed on the virtual switch (`s1`) to give a higher priority to video traffic (Port 5001) over file transfer traffic (Port 5002).
* **Emulated Environment**: The entire network is simulated within a single isolated **Docker container**, ensuring a consistent and reproducible environment for testing.

---

### Project Structure

* `Dockerfile`: Defines the Docker image, including all necessary dependencies like Ryu, Mininet, and Python libraries.
* `priority_ryu_controller.py`: The core of the project. This is the Ryu controller application that handles `PacketIn` events, learns host MAC addresses, and installs flow rules with different priorities.
* `ryu_topo.py`: The Mininet script that builds the network topology (`h1 -- s1 -- h2`) and starts the Open vSwitch (OVS) service.
* `start_project.sh`: A shell script to automate the entire process, including building the Docker image and starting the container.

---

### Getting Started

#### Prerequisites

* **Docker Desktop**: Make sure Docker is installed and running on your system. It is highly recommended to use a Linux environment or WSL2 on Windows.

#### Installation and Execution

1.  **Clone the Repository**:
    First, clone this repository to your local machine.

    ```bash
    git clone [https://github.com/vvianne/TrafficPriority.git](https://github.com/vvianne/TrafficPriority.git)
    cd TrafficPriority
    ```

2.  **Build and Run the Docker Container**:
    Use the provided script to automate the entire process. This command will build the Docker image, run the container with the necessary privileges, and start the Mininet CLI.

    ```bash
    chmod +x start_project.sh
    ./start_project.sh
    ```
    The build process may take a few minutes. Once complete, you will see the Mininet CLI prompt (`mininet>`).

---

### Usage and Verification

Once the network is up and running in the Mininet CLI, you can perform the following tests to verify that traffic prioritization is working correctly.

1.  **Verify Flow Rules**:
    Check the flow table on the switch (`s1`) to see the default rules installed by Ryu.
    ```bash
    mininet> sh ovs-ofctl dump-flows s1
    ```
    You will see a single default rule with `priority=0`. After running an `iperf` test, you can run the command again to see the new flow rules with `priority=10` and `priority=20`.

2.  **Run Priority-Based Traffic Tests**:
    Start `iperf` servers on `h1` for both types of traffic. Then, run clients on `h2` to generate the traffic.
    * **Start servers on `h1`**:
        ```bash
        mininet> h1 iperf -s -p 5001 &
        mininet> h1 iperf -s -p 5002 &
        ```
    * **Start a high-priority video client on `h2`**:
        ```bash
        mininet> h2 iperf -c 10.0.0.1 -p 5001 -t 30
        ```
    * **Start a low-priority file transfer client on `h2`**:
        ```bash
        mininet> h2 iperf -c 10.0.0.1 -p 5002 -t 30
        ```

3.  **Observe the Logs**:
    In the terminal where your Ryu controller is running, you will see log messages confirming that the controller has identified the traffic and installed the appropriate flow rules with `priority=20` for video and `priority=10` for file transfer.

---

### Further Exploration

This project can be extended to include more advanced features such as:

* **Quality of Service (QoS)**: Implement specific rate-limiting or queueing disciplines for different traffic types.
* **Network Resilience**: Add redundant links to the topology to test failover and dynamic routing capabilities.
* **Visual Monitoring**: Use Ryu's REST API to build a simple dashboard to monitor network statistics and traffic flows in real-time.