# MARMTOUCH SETUP


## 1. Network Manager Setup

Default network manager on raspberry pi will not work on Western networks. 

The following instructions must first be completed using a cellular network/different network to have internet access.

1. Set WiFi country to Canada  
   if this was not done in setup, do this in Raspberry Pi Configuration Menu (see next section)
2. Run the following terminal commands
```bash
sudo apt install network-manager network-manager-gnome
sudo systemctl disable --now dhcpcd
```
3. Restart the pi
4. Connect to the Western Wi-Fi

The rest of this set up can be done on western wifi/robarts network  

## 2. Setting up the proxy server

To access apt and pypi repositories on restricted networks, you may have to set up a proxy server.  
The proxy server address usually takes the form `http[s]://proxy.server:port` where port is usually 8080.

For apt, this can be done via the apt conf proxy file:

```bash
vi /etc/apt/apt.conf.d/02proxy
```

and paste the following:

```bash
Acquire:{
http::Proxy "http://proxy.server:port";
https::Proxy "https://proxy.server:port";
}
```

For PyPI, the proxy server can be set up at the system level.  
Define the lowercase and uppercase versions. Ensure that the https_proxy points to the http link or 
it will not work with PyPI.

``` bash
sudo vi /etc/environment
```

and paste the following

```bash
http_proxy=http://proxy.server:port
https_proxy=http://proxy.server:port
HTTP_PROXY=https://proxy.server:port
HTTPS_PROXY=http://proxy.server:port
```

Restart the pi before proceeding.


If this approach does not work with PyPI, export these as environment variables instead.

This can be achieved easily by adding the following to your `.bashrc` file

```bash
export http_proxy=http://proxy.server:port
export https_proxy=http://proxy.server:port
export HTTP_PROXY=https://proxy.server:port
export HTTPS_PROXY=http://proxy.server:port
```

## 3. Remote access configuration

Some things need to be configured to be able to access this Pi via SSH or VNC

You can access the Raspberry Pi Configuration menu by navigating to:  
> Raspberry Pi "Start Menu" (top left) --> Preferences --> `Raspberry Pi Configuration`  

OR  
```bash
sudo raspi-config
```

* Under System --> Change hostname to "pi" and password to "marmoset"
* Under Display --> Disable Screen blanking
* Under Interfaces --> Enable VNC and SSH

A VNC icon should immediately appear on the task bar.  
Click on this icon to see the RealVNC gui.  
An IP Address should be listed that can be used to access the Pi.  
Test to make sure it is working


## 4. Set up server access

### 4.1. Ensure required tools are available
```bash
sudo apt-get update
sudo apt-get install vim -y
sudo apt-get install cifs-utils -y
```

### 4.2. Update configuration info
Edit the fstab file using vim
```bash
sudo vim /etc/fstab
```
And add the following line to the bottom of the file
Replace {USER} and {PASS} with your serve access credentials
```
//everlingsrv.robarts.ca/Data /mnt/Data cifs user={USER},pass={PASS},file_mode=0777,dir_mode=0777,rw,_netdev 0 0
```

> VIM TIPS  
> In edit mode, hit escape to return to normal mode and in normal mode
> `i` allows you to enter edit mode
> In normal mode, the following shortcuts are useful
> * `G` goes to the end of the file
> * `o` adds a new line and enters edit mode below cursor
> * `ZZ` saves the file and exits
> 
Create the mount point and mount the server
```bash
sudo mkdir /mnt/Data
sudo mount -a
```

## 5. Setting up marmtouch

### 5.1. Install the python package
Use pip3 to install the package from the server
```bash
sudo pip3 install git+file:///mnt/Data/Touchscreen/marmtouch -U
```
Make sure to create the Touchscreen folder where data will be saved
```bash
mkdir ~/Touchscreen
```

### 5.2. Set up the shortcut
1. Navigate to the main menu editor:  
   Raspberry Pi Start Menu --> Preferences --> `Main Menu Editor`
2. Select `Other` and Click `New Item`
3. Input the following parameters and confirm 
   > Name: `marmtouch`  
   > Command: `sudo marmtouch launch`  
   > Launch in terminal: Set to `True`  
   > &nbsp;  
   > (OPTIONAL) add an icon
   > 1. The corresponding file, marm.png is in the setup folder can be found on the server. 
   > 2. Copy it to /home/pi/Pictures
   > 3. Click on the icon in this menu, and select the image file you copied over
4. Right click on the task bar and open `Panel Settings`
5. Navigate to the `Panel Applet` Tab
6. Select `Application Launch Bar` and click `Preferences`
7. Navigate to `Other > marmtouch`
8. Click `Add` to add it to the launch bar
9. Click `Up` until it is at the top of the list

You should see the marmtouch program on the launch bar beside the Raspberry Pi Start Menu icon.  
Clicking it should open the marmtouch launcher  

### 5.3. Import necessary files
Copy over the config and stimuli files
```bash
cp /mnt/Data/Touchscreen/configs/. ~/configs -r
cp /mnt/Data/Touchscreen/stimuli/. ~/stimuli -r
```

### 5.4. Set up system config
Copy marmtouch_system_config.yaml from setup folder
```bash
cp /mnt/Data/Touchscreen/setup/marmtouch_system_config.yaml ~/
```
update info to match the pi you are configuring  
critical fields are:
* the ttl port numbers (must atleast define `reward` and `sync`)
* the "has_camera" flag (boolean)

### 5.5. Confirm monitor resolution
The program currently uses hard-coded screen coordinates for stimulus presentation  
For this, the resolution is assumed to be **1280x800**  

When the actual touchscreen monitor is plugged in, navigate to the resolution configuration menu

This varies depending on the version of pi. It will either be in:

> Raspberry Pi Start Menu --> Preferences --> `Screen Configuration`   

OR  

> Raspberry Pi Start Menu --> Preferences --> `Raspberry Pi Configuration` --> Display
