---
layout: page
title: SAN and PresRAID Startup and Shutdown
parent: Technical Documentation
---

# SAN and PresRAID Startup and Shutdown

## SAN Startup

* Power up the SAN by pressing the power button on the front right-hand side of the server. Note, the SAN should be plugged into a UPS ideally.
* Wait about 15 minutes for things to start up
* Go to the SAN management GUI at: [https://192.168.253.61:8088](https://192.168.253.61:8088). Login credentials can be found on 1Password
* Once logged in, go to the VM (Virtual Machine) Tab on the right side of the browse window. If the tab doesn't appear, wait 5 to 10 minutes and refresh the page.
* Click the VM icon at the bottom of the screen (image attached) to enter the View and Management control panel
* ![VM Button]({{site.baseurl}}/assets/images/VM_Button.png)
* Here, you'll see statuses for both Metadata Controllers, MDC1 and MDC2. If you just started up the system, these should both have a Running Status of Powered Off.
* Click on the row labeled MDC1 and press the Power On button
* Once the Execution Result has succeeded you can close the popup window. Wait about 15 minutes, then to do the same for MDC2
* Once MDC2 is up and running you can closes the GUI and the SAN should be up and running
* To mount the SAN on the transfers stations you need to run the following command in terminal
  - `sudo xsanctl mount SymplyUltra`

## SAN Shutdown

* Make sure that the SAN is unmounted from all computers using this command
  - `sudo xsanctl unmount SymplyUltra`
* Login to the same web portal discussed above and stop services
* Shutdown



## PresRAID Startup

* Power up the PresRAID by pressing the power button on the front left-hand side of the server
  _Note: the PresRAID should be plugged into a UPS ideally_
* Wait about 15 minutes for things to start up

## PresRAID Shutdown

* Make sure that the PresRAID is ejected from all computers
* Open a terminal window
* Remotely log into the PresRAID as the user bavcadmin with the following command
  - `ssh bavcadmin@192.168.253.95`
* You'll be asked for a password, get it from 1password
* Shutdown the PresRAID with the following command
  - `sudo shutdown -h now`
* If you're prompted for a password it will be the same as before, available on 1password
* That's it. The PresRaid should be down in a few minutes
