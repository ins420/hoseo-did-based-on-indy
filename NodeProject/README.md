# NodeProject
## 1. System Specification
| OS             | CPU Architecture | Language     |
|:---------------|:-----------------|--------------|
| Ubuntu 16.04   | AMD64            | Python 3.5.2 |
***
## 2. Development Environment Configuration
## [Ubuntu 16.04]
```commandline
sudo apt-get update
sudo apt-get upgrade -y
```
```commandline
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
sudo add-apt-repository "deb https://repo.sovrin.org/deb xenial stable"
sudo apt-get update
sudo apt-get install -y indy-node
```
```commandline
sudo su indy
init_indy_node Test_Node1 127.0.0.1 9701 127.0.0.1 9702 aaaaseedbbbbseedccccseedddddseed
```
ex) init_indy_node {name} {ip} {node-node port} {ip} {node-client port} {seed}
```
sudo systemctl restart indy-node
sudo systemctl status indy-node
sudo systemctl enable indy-node
```
***