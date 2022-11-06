---
layout: page
title: Monthly Maintenance
parent: Admin
---


# Monthly Maintenance Tasks and BAVC

The following tasks should be performed on a monthly basis to keep our physical and digital spaces tidy. You don't need to do these all on the same day, but please make sure it all happens at least once a month

## Lab Cleanup

General cleanup of the lab is necessary for a tidy, safe, and efficient work environment. The following is non-inclusive list of tasks that should be completed during cleanup:
   * Vacuum all carpeted areas
   * Coil up and loose cables and return them to their proper storage drawer
   * Dust and clean off all surfaces and CRT screens
   * Rinse off the kitchen area
   * File or throw away and loose papers or records

## Monitor Calibration

Monitors should be calibrated using color bars once a month. Each station should have either a color bar generator or a DPS-575 with a test signal generator attached to it.

## SAN Maintenance

* Delete any files that have been loaded to the client drives. Make sure to mark them as loaded in this [list](https://bavc.lightning.force.com/lightning/o/Preservation_Object__c/list?filterName=00B500000086MiREAU).

* Delete any project folders in the ***TransferProjects*** folder if the drive has been loaded and the project has been marked complete

* Take a peek though the ***OtherProjects*** and ***Testing*** folders and delete any finished projects or files.

## PresRAID Maintenance

* Move any project folders that have been completed from ***InProgress*** to ***Delivered***

## Salesforce Maintenance

There's a number of reports in Salesforce that are used to track projects, sales, and objects. These needs to be kept up to to date in order to work properly. Monthly maintenance is a great time to clean up and check in on these reports.

### PresRAID Deletions

* [QC Passed Not Loaded To Drive](https://bavc.lightning.force.com/lightning/o/Preservation_Object__c/list?filterName=00B500000086MiREAU): This view makes it easy to mark items as *loaded* to a drive.

* [PresRAID Delete Now](https://bavc.lightning.force.com/lightning/r/Report/00O50000006AAaQEAW/view?queryScope=userFolders): This report contains every project that is past its PredRAID deletion deadline. We like to email collection holders and warn them before we delete their backups. However, once you've deleted the backups make sure to check off the box labeled *Deleted from PresRAID?*q in the Opportunity record. 

* [Preservation Quotes In Negotiation](https://bavc.lightning.force.com/lightning/r/Report/00O2J000006MsiZUAS/view?queryScope=userFolders): This report shows all inquiries that are currently in negotiation. If you haven't heard from someone in a while you can reach out to them again. If it's been too long and the project won't happen you can mark the opportunity as *Closed/Lost*


![Cleanup Shrimp]({{site.baseurl}}/assets/images/cleaningshrimp.gif)
