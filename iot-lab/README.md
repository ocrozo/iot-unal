# Workshop IoT-Lab
*Thanks to Romain Pujol and Hervé Rivano from the Citi Laboratory*

## Preliminaries
The IoT-lab platform is a very large scale scientific infrastructure, it is designed for testing small wireless sensor devices and heterogeneous communicating objects. It is the evolution and extension of the SENSLAB testbed (2010-2013). It counts more than 2700 nodes over 7 facilities in France and 1 in Germany. For more details go on to https://www.iot-lab.info/what-is-iot-lab/.

### Consequences 
* It is a shared tool. In particular, when you book a resource (a set of sensors), other users can no longer use it. Remember to make sure you do not need to monopolize a resource.
* While experimenting with a few nodes, other users - even on the other side of the world - may use nearby nodes and interfere with yours. Think about it in analyzing your results.

## Setting up
The IoT-lab platform has two main characteristics:
- remote access via a web service and an ssh frontend: this involves creating an account and configuring access
- code running on systems built on an architecture ARM M3: to create your own firmware you need dedicated compilation tools

## 1. Account and access
> Temporal accounts are already created for all of UNAL students following this IoT-lab tutorial, ask your monitor to get your account. Nevertheless, this account is valid until *31/07/2018* so if you want to continue testing on the platform, feel free to create your own account.
To create a free account: 
- Go to the web portal: https://www.iot-lab.info/
- Create an account (register)
  * Put your true identity, use your mail unal
  * If you have already created a ssh key pair on your computer, copy and paste the public key, otherwise leave this field empty, we'll come back to it.
  * Motivation: "Tutorial IoT-lab UNAL Colombia - CITI Lab"
- The validation of your account involves a "human" phase, so it will take a while. Check your mailbox, you will receive emails from admin@iot-lab.info. Once your account is created you will be able to connect to the web portal https://www.iot-lab.info/testbed-beta/
- Create a pair of ssh keys. You will enter the public key on the web portal once your account is created. Instructions to follow are at https://www.iot-lab.info/tutorials/configure-your-ssh-access/
   * _Tip_: preferably use linux or macOS, it's much easier for ssh access, console use and cross-compilation of firmware. It is possible with Windows but less direct.
   * _Tip 2_: computers in UNAL are behind a proxy, so you need to create a config file to connect to ssh through the proxy.
     1. Install the `corkscrew` program with: 
        `sudo apt-get install corkscrew`
     2. Create a file `~/.ssh/config`
     3. Add the following line to that file:
        ```
        ProxyCommand /usr/bin/corkscrew 168.176.239.41 8080 %h %p 
        ```  
___
At this point, you should be able to connect to different ssh frontends. There is one by site whose address is `<site_name>.iot-lab.info`.
The frontend in Lyon is `lyon.iot-lab.info` 
> In a linux or macOS terminal, use the `ssh -X <your_user>@lyon.iot-lab.info` command
> The -X option indicates an "X11 forwarding", so the ability to launch a graphical application that runs on the server but appears on your screen (with performance dependent on the quality of your connection). It is not always necessary but will be useful to visualize the results of the experiments.
**Warning**: it happens (often?) That your connection is refused with
a message "permission denied (publickey)". The administration of IoT-lab is prevented. For now, check that your ssh key pair is correct and insist.

> Tip: To avoid having to log in to the frontend multiple times or lose all your work in case of connection break, use the `screen` command once connected (`man screen` or [here](https://www.tecmint.com/screen-command-examples-to-manage-linux-terminals/)). There is an alternative: `tmux`.
> It allows you to have several virtual terminals and, above all, to launch a task, disconnect and return later without interrupting. The consequence is that you have to be **careful to finish** your screen when the job is done to **avoid cluttering the server**.

## 2. First experiment
You will launch your first IoT-lab experiment using a precompiled and simple firmware for M3 nodes. You will then be able to connect to the sensors and interact with them. During all this tutorial, we will only use M3 nodes.
- Get the firmware "tutorial_m3.elf" online:
https://raw.githubusercontent.com/wiki/iot-lab/iot-lab/firmwares/tutorial_m3.elf
- Connect to the web portal
- Select the "New Experiment" tab and configure a
experimentation:
  * Find a representative name 
  * The duration must allow you to go to the end without monopolize the infrastructure too much
  * Start: As soon as possible
  * Choice of nodes by node properties: 
    - Architecture:  M3 (At86rf231) 
    - Site: wherever you like 
    - Quantity:  2
    - Mobile: Unchecked 
  * Click `Add to experiment`
  * Association of nodes:
    - You will see a list with the nodes that you have requested. 
    - Click on the `Add firmware` button, you will indicate which firmware will be launched on your nodes.
    - Browse and upload the tutorial firmware that you downloaded before
  * Click on "Submit experiment" to start the experiment. 
  * You will be redirected to the Dashboard and see the experiments spinning. Click on yours.
  * Locate the names of the nodes that are assigned to you, wait for "success" to appear in the Deployment column
  * Connect to the frontend of your site 
  * Interact with your M3 nodes
    - M3 nodes can read and write on their serial port. To access it, the IoT-lab platform opens a TCP socket on port 20000.
    - Connect to the nodes with the command "nc <node-id> 20000"
    - If your node is m3-14.lyon.iot-lab.info, node-id is m3-14.
    - A menu appears (type "h entry" if it is not the case)
    - Get the uid of each node
    - Get the temperature, brightness and pressure on each node. 
    - Send a packet with one of the nodes, what do you see?
    - Explain the messages you see appearing in your terminals.
  * You can connect directly from your PC with the command `ssh -L 20000:<node-id>:20000 <login>@<site>.iot-lab.info; nc localhost 20000`. Do you have two nodes? How to connect to both?
> Important: `nc` (=netcat) must be installed on your computer

## 3. Change the firmware
You must have noticed that all the nodes use the same frequency and get scrambled. The radio channel is configured in the firmware. It is therefore necessary to modify and recompile the firmware so that each one uses different frequencies.
- Connect to the ssh frontend of your selected site
- Get the source code on git: 
   `git clone https://github.com/iot-lab/iot-lab.git`
- Preparation of the environment
    * cd iot-lab
    * make
    * make setup-openlab
- Analysis and modification of the source code
    * cd parts/openlab
    * cd appli/iotlab_examples/tutorial
    * Analyze main.c source code and other files.
      - What do you understand about the different functions?
    * Save main.c in main.old and modify main.c to change the radio channel (and other things if you want). Each user on the same site must choose a different channel between 11 and 26.
- Compilation
    * cd ../../..
    * mkdir build.m3; cd build.m3
    * cmake .. -DPLATFORM=iotlab-m3
    * make tutorial_m3
    * The compiled firmware is bin/tutorial_m3.elf
    * Rename the file to keep an explicit name
- Download this file on your computer (with scp) and restart an experiment as in the previous part (*Attention*: the affected nodes may have changed). If you had conflicts with other users on the same site in the same channel, you should not have a conflict anymore.

> To go further: it is possible to install the ARM compilation environment on your computer. Details about the installed version are here: https://github.com/iot-lab/iot-lab/wiki/Versions-of-the-GNU-toolchain-for-ARM
> It is necessary to download the cross-compiler gcc-arm-embedded (attention to the version) then the toolchain arm-gcc being careful that it is a 32 bits version, so on 64 bits architectures it is necessary to install the libc and libncurses for 32 bits.
> It is simple and more comfortable to work with your favorite development tools. For the scope of this tutorial it is not necessary.

## 4. Measure the energy consumption of a node
- Connect to the web portal
- Go to the "Resources" tab 
- Create a new profile with an explicit name
- Choose the M3 architecture, and check Consumption. For the moment let "radio mode" to none.
- Select all Consumption options.  This indicates that you want the energy consumption recorded in a log.
- Keep the default values: Period: 8244 μs, Average = 4
- Read the box at the bottom of https://www.iot-lab.info/tutorials/monitor-consumption-m3-node/ to understand
the meaning of these values
- Save the profile
- Start a new experiment as before (2 nodes each) except that at the time of the association, you associate your profile with the nodes
- Connect to the frontend ssh (make sure you have the -X option
- Look at the log files ~ /.iot-lab/<experiment-id>/consumption/M3-<id>.oml
    * Identify saved values, their units, etc. 
    * Display the results as curves `plot_oml_consum -p -i ~/.iot-lab/<experiment-id>/consumption/m3-<id>.oml`
    * What produces the swing you see?
    * Deduce the energy consumption of an element of the nodes.
- Connect to the sensors (with nc) and send packets.
    * Try to estimate the energy consumption of a transmission and reception.
- How could you change the firmware to measure with more reliability and more precision?
    * Make averages
    * Evaluate the impact of packet size on the consumption 
    * Do it!
- Evaluate the impact of transmission power on consumption
    * The allowable transmission power values ​​are defined in the file ~/iot-lab/parts/openlab/net/phy.h
- **Bonus**: you can also download the oml files and analyze them a posteriori with a spreadsheet, gnuplot, etc. tool.

## 5. Measure the quality of reception
- Go to the "Resources" tab 
- Create a new profile with an explicit name
- - Choose the M3 architecture, and check "Radio". Let "Consumption" to none.
- Select radio mode rssi.
- Choose the channel to measure according to your firmware and a channel that no one uses (this one can be the same for all)
- Period = 1ms, number of measure per channel = 1
- Read the box at the bottom of https://www.iot-lab.info/tutorials/radio-monitoring-for-m3-nodes/ to understand the meaning of these values
- Save the profile
- Launch a new experiment as before with this profile
- Connect to the ssh frontend (make sure you have the -X option)
- Look at ~/.iot-lab/<experiment-id>/radio/m3-files<Id>.oml
- Identify values, their units, etc.
- Display the results as curves : `plot_oml_radio -a -i ~/.iot-lab/<experiment-id>/radio/m3-<id>.oml`
- Connect to the sensors (with nc) and send some packets. Estimate the quality of the channel. Is she the same with long packets and short packets?
- By comparing values ​​with other users, what can you deduce? Is there a channel more suitable than another?
- Evaluate the impact of the transmission power on the RSSI
  * The allowable transmission power values ​​are defined in the file ~/iot-lab/parts/openlab/net/phy.h

## 6. Bonus: to go further
- Watch the tutorials to use the CLI (command-line interface) tools
- Follow the tutorial "radio sniffer" https://www.iot-lab.info/tutorials/radio-sniffer/
- Follow the tutorial "ipv6-coap contiki" https://www.iot-lab.info/tutorials/public-ipv6-coap/