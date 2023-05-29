# TrusteeProject
***
## 1. System Specification
| OS             | CPU Architecture | IDE                       | Language     |
|:---------------|:-----------------|---------------------------|--------------|
| Ubuntu 16.04   | AMD64            | Visual Studio Code 1.78.2 | Python 3.5.2 |
***
## 2. Development Environment Configuration
### [Ubuntu 16.04]
```commandline
sudo apt-get update
sudo apt-get upgrade -y
```
```commandline
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88
sudo add-apt-repository "deb https://repo.sovrin.org/deb xential stable"
sudo apt-get update
sudo apt-get install -y indy-node
```
### [Python3]
```commandline
sudo apt-get install python3-pip python-pip curl
curl -O https://bootstrap.pypa.io/pip/3.5/get-pip.py
python3 get-pip.py
```
```
pip3 install pip==9.0.1
pip3 install wheel==0.29.0
pip3 install setuptools==57.5.0
pip3 install flask
```
### [WebDAV]
```commandline
sudo apt-get update
sudo apt-get install -y apache2 \
                        apache2-utils

sudo a2enmod dav dav_fs autoindex
sudo service apache2 restart

sudo mkdir /var/www/html/trustee
sudo chown www-data:www-data /var/www/html/trustee
sudo chmod 777 /var/www/html/trustee
```
```commandline
sudo vim /etc/apache2/sites-available/000-default.conf
```
```text
Alias /trustee /var/www/html/trustee
<Directory /var/www/html/trustee>
    DAV on
</Directory>
```
***