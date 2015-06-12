OpenVSwitch Testing Outline/Summary
---------------------------

This documents a draft set of procedures for installation and configuring
OpenVSwitch for testing OpenVSwitch or software that depends on OpenVSwitch.

The source code instructions should may be useful as a starting point for
the setup of automatic builds to generate .deb, .rpm, and
other packages that can be installed by end users on 'supported distros'
who need a version of OVS that doesnt ship with their distribution.

[TOC]


Installing OpenVSwitch
----------------------

###### Step 1 - Basic Dependencies.

Just some basic tools.

- Ubuntu

```bash
apt-get install vim htop tmux moreutils daemontools glances git at beep ranger docker.io curl httpie
sudo apt-get build-dep python2.7 python3.2
curl https://raw.github.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
echo <<'EOF' > ~/.bash_profile
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
```

- Fedora

```bash
TODO
```

###### Step 2 - Install a version of OpenVSwitch.

Current versions of OpenVSwitch provided in both
the Ubuntu and Fedora package repositories are based on 2.3.x,
and lack some components due to ship in 2.4.
RSTP (Rapid Spanning Tree Protocol) support is due to ship with version 2.4.x.
In order to test anything to do with RSTP we need to build from source.

There are several options for installing OpenVSwitch dependng on requirements:

- On Ubuntu:

 1. Install the stable 2.3.x version.

```bash
apt-get install openvswitch-switch
```

 2. Build and Install from source.

```bash
apt-get install build-essential fakeroot openvswitch-datapath-dkms_
apt-get install --no-install-recommends -y  \
debhelper \
libssl-dev \
graphviz \
python-all \
python-qt4 \
python-zopeinterface \
python-twisted-conch \
python-twisted-web
git clone https://github.com/openvswitch/ovs.git
cd ovs
dpkg-checkbuilddeps
fakeroot debian/rules binary
# This will do a serial build that runs the unit tests.
# This will take approximately 8 to 10 minutes.
# If you prefer, you can run a faster parallel build, e.g.:
# DEB_BUILD_OPTIONS='parallel=8' fakeroot debian/rules binary
# If you are in a big hurry, you can even skip the unit tests:
# DEB_BUILD_OPTIONS='parallel=8 nocheck' fakeroot debian/rules binary
cd ..
dpkg -i \
openvswitch-datapath-dkms_*_all.deb \
openvswitch-common_*_amd64.deb \
openvswitch-switch_*_amd64.deb \
openvswitch-pki_*_all.deb \
openvswitch-testcontroller_*_amd64.deb \
python-openvswitch_*_all.deb \
openvswitch-test_*_all.deb \
```
The following extra packages are built but not normally needed.
Check the documentation before installing any of them.

```bash
# openvswitch-ipsec_*_amd64.deb \
# openvswitch-vtep_*_amd64.deb \
# openvswitch-datapath-source_*_all.deb \
# openvswitch-dbg_*_amd64.deb \
```

- On Fedora:

 1. Install the stable ??? version.

```bash
TODO
```

 2. Build and Install from source.

```bash
TODO
```

###### Step 3 - Check a few things to see if everything looks ok.

Some simple post install checks that everything looks right after installing.

- On Ubuntu

```bash
service --status-all | grep openvswitch
ps aux | grep ovsdb
ovs-vsctl -V
ovs-vsctl show
```

- On Fedora

```bash
TODO
```

If everything looks ok, we can move on and start doing
whatever it was that required us to install OpenVSwitch.
Typically testing either OVS or something that depends on it.

Test Network Setup and Configuration
------------------------------------

In order to test Layer 2 switch topology issues,
we need to setup a number of nodes,
with vswitch bridges on them, connect them together,
confirm they are connected to each other and working correctly,
then perform our test.

The following commands document testing STP and RSTP using 2 bridges on 3 servers,
watching layer 3 traffic between the servers on each of the bridges using ping,
and creating a routing loop so we can record the results.
Because we are specifically testing RSTP,
these servers need to have OpenVSwitch built and installed
from source code until after 2.4.x is released.

# This needs a teardown function for cleaner testing.


###### Build the docker container for testing.

These commands should be run on all three servers so that they have
the docker container with the right tools for the tests.

```bash
echo "Preparing the Docker container we'll use for testing."
docker run -d --name "build" -p 3000 -dt nathanleclaire/wetty && \
docker exec -i -t "build" apt-get update && \
docker exec -i -t "build" apt-get install -y iputils-ping && \
docker exec -i -t "build" apt-get install -y moreutils && \
docker commit build cygnus/wetty && \
docker stop "build" && \

docker run -d --name "pyenv" ubuntu
docker exec -i -t "pyenv" apt-get update && \
docker exec -i -t "pyenv" apt-get install curl git-core && \
docker exec -i -t "pyenv" apt-get build-dep python2.7 python3.2


docker images
```

##### Create the control tmux session on each server.

Create the tmux session we will use.

```bash

docker exec -i -t "pyenv" apt-get install curl git-core && \
docker exec -i -t "pyenv" apt-get build-dep python2.7 python3.2

tmux has  -t "_ovs__control" || tmux new -d -s "_ovs__control"
```


###### Test script for Server 1

Save this as server1-test.bash

```bash
#!/bin/bash -e

VM1_IP="10.135.243.153"
VM2_IP="10.135.243.154"
VM3_IP="10.135.243.155"

# Check that we are running the script from the correct place.
#echo "Are we in the right tmux session."
#if [ $(tmux display-message -p '#S') = "_ovs__control" ]
#then echo "This script should be run from inside the tmux session : _ovs__control"; exit 1
#fi
# Create the other tmux sessions we will for the backend test runs.
tmux has -t "ping__br1__vm1-to-vm1" || tmux new -d -s "ping__br1__vm1-to-vm1"
tmux has -t "ping__br1__vm1-to-vm2" || tmux new -d -s "ping__br1__vm1-to-vm2"
tmux has -t "ping__br1__vm1-to-vm3" || tmux new -d -s "ping__br1__vm1-to-vm3"
tmux has -t "ping__br2__vm1-to-vm1" || tmux new -d -s "ping__br2__vm1-to-vm1"
tmux has -t "ping__br2__vm1-to-vm2" || tmux new -d -s "ping__br2__vm1-to-vm2"
tmux has -t "ping__br2__vm1-to-vm3" || tmux new -d -s "ping__br2__vm1-to-vm3"


# Stop and remove any docker containers from previous test runs.
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
# Remove OVS bridges from previous test runs.
ovs-vsctl --\i\f-exists del-br br1
ovs-vsctl --\i\f-exists del-br br2
# Confirm everything is cleaned out.
docker ps
ovs-vsctl show

# Create our intial bridges.
ovs-vsctl add-br br1 -- set Bridge br1 stp_enable=true
ovs-vsctl add-br br2 -- set Bridge br2 rstp_enable=true

ovs-vsctl add-port br1 br1gre1 -- set Interface br1gre1 type=gre options:remote_ip=${VM2_IP} options:key=100
ovs-vsctl add-port br1 br1gre2 -- set Interface br1gre2 type=gre options:remote_ip=${VM3_IP} options:key=100
ovs-vsctl add-port br2 br2gre1 -- set Interface br2gre1 type=gre options:remote_ip=${VM2_IP} options:key=200
ovs-vsctl add-port br2 br2gre2 -- set Interface br2gre2 type=gre options:remote_ip=${VM3_IP} options:key=200


NUMBER=0
docker run -d --net=none --name "br1-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br1 -i eth0 "br1-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:11
docker run -d --net=none --name "br2-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br2 -i eth0 "br2-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:12
NUMBER=1
docker run -d --net=none --name "br1-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br1 -i eth0 "br1-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:13
docker run -d --net=none --name "br2-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br2 -i eth0 "br2-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:14


#sleep 1m
#printf '\a'
tmux send-keys -t ping__br1__vm1-to-vm1 'C-u' 'C-k' 'docker exec -i -t br1-t0 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm1-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br1__vm1-to-vm2 'C-u' 'C-k' 'docker exec -i -t br1-t1 ping -n -i 0.5 -w 300 10.0.0.12 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm1-to-vm2.tai64n.log' 'C-m'
tmux send-keys -t ping__br1__vm1-to-vm3 'C-u' 'C-k' 'docker exec -i -t br1-t1 ping -n -i 0.5 -w 300 10.0.0.13 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm1-to-vm3.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm1-to-vm1 'C-u' 'C-k' 'docker exec -i -t br2-t0 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm1-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm1-to-vm2 'C-u' 'C-k' 'docker exec -i -t br2-t1 ping -n -i 0.5 -w 300 10.0.0.12 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm1-to-vm2.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm1-to-vm3 'C-u' 'C-k' 'docker exec -i -t br2-t1 ping -n -i 0.5 -w 300 10.0.0.13 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm1-to-vm3.tai64n.log' 'C-m'

sleep 5m
printf '\a\a'
cat ping__br1__vm1-to-vm1.tai64n.log | tai64nlocal > ping__br1__vm1-to-vm1.iso8601.log
cat ping__br1__vm1-to-vm2.tai64n.log | tai64nlocal > ping__br1__vm1-to-vm2.iso8601.log
cat ping__br1__vm1-to-vm3.tai64n.log | tai64nlocal > ping__br1__vm1-to-vm3.iso8601.log
cat ping__br2__vm1-to-vm1.tai64n.log | tai64nlocal > ping__br2__vm1-to-vm1.iso8601.log
cat ping__br2__vm1-to-vm2.tai64n.log | tai64nlocal > ping__br2__vm1-to-vm2.iso8601.log
cat ping__br2__vm1-to-vm3.tai64n.log | tai64nlocal > ping__br2__vm1-to-vm3.iso8601.log
```

##### Test script for Server 2

Save this as server2-test.bash

```bash
#!/bin/bash -e

VM1_IP="10.135.243.153"
VM2_IP="10.135.243.154"
VM3_IP="10.135.243.155"

# Check that we are running the script from the correct place.
#echo "Are we in the right tmux session."
#if [ $(tmux display-message -p '#S') = "_ovs__control" ]
#then echo "This script should be run from inside the tmux session : _ovs__control"; exit 1
#fi
# Create the other tmux sessions we will for the backend test runs.
tmux has -t "ping__br1__vm2-to-vm1" || tmux new -d -s "ping__br1__vm2-to-vm1"
tmux has -t "ping__br1__vm2-to-vm3" || tmux new -d -s "ping__br1__vm2-to-vm3"
tmux has -t "ping__br2__vm2-to-vm1" || tmux new -d -s "ping__br2__vm2-to-vm1"
tmux has -t "ping__br2__vm2-to-vm3" || tmux new -d -s "ping__br2__vm2-to-vm3"


# Stop and remove any docker containers from previous test runs.
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
# Remove OVS bridges from previous test runs.
ovs-vsctl --\i\f-exists del-br br1
ovs-vsctl --\i\f-exists del-br br2

# Create the intial bridges.
ovs-vsctl add-br br1 -- set Bridge br1 stp_enable=true
ovs-vsctl add-br br2 -- set Bridge br2 rstp_enable=true
ovs-vsctl add-port br1 br1gre1 -- set Interface br1gre1 type=gre options:remote_ip=${VM1_IP} options:key=100
ovs-vsctl add-port br2 br2gre1 -- set Interface br2gre1 type=gre options:remote_ip=${VM1_IP} options:key=200


NUMBER=2
docker run -d --net=none --name "br1-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br1 -i eth0 "br1-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:15
docker run -d --net=none --name "br2-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br2 -i eth0 "br2-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:16


tmux send-keys -t ping__br1__vm2-to-vm1 'C-u' 'C-k' 'docker exec -i -t br1-t2 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm2-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br1__vm2-to-vm3 'C-u' 'C-k' 'docker exec -i -t br1-t2 ping -n -i 0.5 -w 300 10.0.0.13 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm2-to-vm3.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm2-to-vm1 'C-u' 'C-k' 'docker exec -i -t br2-t2 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm2-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm2-to-vm3 'C-u' 'C-k' 'docker exec -i -t br2-t2 ping -n -i 0.5 -w 300 10.0.0.13 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm2-to-vm3.tai64n.log' 'C-m'


sleep 2m
printf '\a'
ovs-vsctl add-port br1 br1gre2 -- set Interface br1gre2 type=gre options:remote_ip=${VM3_IP} options:key=100
ovs-vsctl add-port br2 br2gre2 -- set Interface br2gre2 type=gre options:remote_ip=${VM3_IP} options:key=200


sleep 3m
tmux send-keys -t ping__br1__vm2-to-vm1 'C-'
printf '\a\a'

cat ping__br1__vm2-to-vm1.tai64n.log | tai64nlocal > ping__br1__vm2-to-vm1.iso8601.log
cat ping__br1__vm2-to-vm3.tai64n.log | tai64nlocal > ping__br1__vm2-to-vm3.iso8601.log
cat ping__br2__vm2-to-vm1.tai64n.log | tai64nlocal > ping__br2__vm2-to-vm1.iso8601.log
cat ping__br2__vm2-to-vm3.tai64n.log | tai64nlocal > ping__br2__vm2-to-vm3.iso8601.log
```

##### Test script for Server 3

Save this as server3-test.bash

```bash
#!/bin/bash -e

# Setup necessary variables.
VM1_IP="10.135.243.153"
VM2_IP="10.135.243.154"
VM3_IP="10.135.243.155"


# Check that we are running the script from the correct place.
#echo "Are we in the right tmux session."
#if test $(tmux display-message -p '#S') = "_ovs__control"
#then echo "This script should be run from inside the tmux session : _ovs__control"; exit 1
#fi

# Create the other tmux sessions we will for the backend test runs.
tmux has -t "ping__br1__vm3-to-vm1" || tmux new -d -s "ping__br1__vm3-to-vm1"
tmux has -t "ping__br1__vm3-to-vm2" || tmux new -d -s "ping__br1__vm3-to-vm2"
tmux has -t "ping__br2__vm3-to-vm1" || tmux new -d -s "ping__br2__vm3-to-vm1"
tmux has -t "ping__br2__vm3-to-vm2" || tmux new -d -s "ping__br2__vm3-to-vm2"


# Stop and remove any docker containers from previous test runs.
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
# Remove OVS bridges from previous test runs.
ovs-vsctl --i\f-exists del-br br1
ovs-vsctl --i\f-exists del-br br2

# Create the intial bridges.
ovs-vsctl add-br br1 -- set Bridge br1 stp_enable=true
ovs-vsctl add-br br2 -- set Bridge br2 rstp_enable=true
ovs-vsctl add-port br1 br1gre1 -- set Interface br1gre1 type=gre options:remote_ip=${VM1_IP} options:key=100
ovs-vsctl add-port br2 br2gre1 -- set Interface br2gre1 type=gre options:remote_ip=${VM1_IP} options:key=200


NUMBER=3
docker run -d --net=none --name "br1-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br1 -i eth0 "br1-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:17
docker run -d --net=none --name "br2-t${NUMBER}" -p 3000 -dt cygnus/wetty
pipework/pipework br2 -i eth0 "br2-t${NUMBER}" "10.0.0.1${NUMBER}/24" 02:42:ac:11:00:18


tmux send-keys -t ping__br1__vm3-to-vm1 'C-u' 'C-k' 'docker exec -i -t br1-t3 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm3-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br1__vm3-to-vm2 'C-u' 'C-k' 'docker exec -i -t br1-t3 ping -n -i 0.5 -w 300 10.0.0.12 2>&1 | stdbuf -oL -eL tai64n | tee ping__br1__vm3-to-vm2.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm3-to-vm1 'C-u' 'C-k' 'docker exec -i -t br2-t3 ping -n -i 0.5 -w 300 10.0.0.11 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm3-to-vm1.tai64n.log' 'C-m'
tmux send-keys -t ping__br2__vm3-to-vm2 'C-u' 'C-k' 'docker exec -i -t br2-t3 ping -n -i 0.5 -w 300 10.0.0.12 2>&1 | stdbuf -oL -eL tai64n | tee ping__br2__vm3-to-vm2.tai64n.log' 'C-m'


sleep 2m
#printf '\a'
ovs-vsctl add-port br1 br1gre2 -- set Interface br1gre2 type=gre options:remote_ip=${VM2_IP} options:key=100
ovs-vsctl add-port br2 br2gre2 -- set Interface br2gre2 type=gre options:remote_ip=${VM2_IP} options:key=200


sleep 3m
#printf '\a\a'
cat ping__br1__vm3-to-vm1.tai64n.log | tai64nlocal > ping__br1__vm3-to-vm1.iso8601.log
cat ping__br1__vm3-to-vm2.tai64n.log | tai64nlocal > ping__br1__vm3-to-vm2.iso8601.log
cat ping__br2__vm3-to-vm1.tai64n.log | tai64nlocal > ping__br2__vm3-to-vm1.iso8601.log
cat ping__br2__vm3-to-vm2.tai64n.log | tai64nlocal > ping__br2__vm3-to-vm2.iso8601.log
```

### Notes

Recommended way to invoke invoke Docker and
```bash
# echo "/usr/bin/docker run -d --net=none --name ${tenant}-${name} -t ${image}"
# echo "/usr/bin/pipework ${bridge} -i eth0 ${tenant}-${name} ${ip}/${subnet} ${mac}"
```
