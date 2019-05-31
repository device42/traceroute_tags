[Device42](http://www.device42.com/) is a Continuous Discovery software for your IT Infrastructure. It helps you automatically maintain an up-to-date inventory of your physical, virtual, and cloud servers and containers, network components, software/services/applications, and their inter-relationships and inter-dependencies.


This repository contains a script that helps traceroute IPs in Device42 and mark tags for devices and IPs.

### Download and Installation
-----------------------------
To utilize the traceroute_tags script, Python 2.7, 3.5+ is required. The following Python Packages are required as well:

* xmljson==0.2.0
* requests==2.13.0
* pyparsing==2.1.10

These can all be installed by running `pip install -r requirements.txt`.

Once installed, the script itself is run by this command: `python traceroute_tags.py`.

### Configuration
-----------------------------
Prior to using the script, it must be configured to connect to your Device42 instance.
* Save a copy of configuration.xml.sample as configuration.xml. 
* Enter your URL, User, Password (lines 4-6).
* Update your DOQL according to your requirements (lines 7).
* Configure hop count and timeout(ms) (lines 9-10).
* Set tag information for devices and IPs (lines 11-12). You can remove any of the success, no-device, or failure attributes to not update tags for those conditions.



### Compatibility
-----------------------------
* Script runs on Linux as root privilege.

### Info
-----------------------------
* configuration.xml - file from where we get configuration information about Device42 and traceroute arguments.
* device42.py - file with integration Device42 instance.
* traceroute.py - file with python traceroute code using raw socket.
* traceroute_tags.py - start script file.

### Support
-----------------------------
We will support any issues you run into with the script and help answer any questions you have. Please reach out to us at support@device42.com.

### Version
-----------------------------
1.0.0