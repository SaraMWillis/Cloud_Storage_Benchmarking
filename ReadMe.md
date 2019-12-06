# Tiered Storage Benchmarking

**This repository was recently updated to contain benchmarking tests for non-cloud storage options.**


## About

This repository contains all the scripts, output CSV files, and figures used and generated from testing upload/download speeds  to/from various cloud storage repositories. A comprehensive summary of all results is included in the available PDF Tiered_Storage_Benchmarking.pdf _(coming soon)_. A second file will be included in the near future that documents setting up all the required software on HPC.

## Current Tested Tiered Storage Options
 * Google Drive
 * AWS S3
 * Cyverse

## Google Drive
The tests in this repository all use various Google Drive software packages to transfer dummy files where a transfer denotes either an upload or a download. All available output csv files, R plotting scripts, and figures are from a variety of programs which include both GUI and CLI programs. Scripts automating available CLI programs rclone, cyberduck, and gdrive are additionally available. Graphical programs were run manually. 

Note: a script has recently been written for the Globus CLI and has been tested with AWS S3. An option for transferring to/from Google Drive has been included. 

The available scripts are designed so that the user can either run them from their personal computer or on University of Arizona's HPC filexfer node. As a result, they have been designed so they can either be run using python 2 or python 3.


### Programs Used

| Program       | Source                               |
|---------------|--------------------------------------|
| Gdrive        | https://github.com/gdrive-org/gdrive |
| Rclone        | https://github.com/rclone/rclone     |
| Cyberduck CLI | https://duck.sh/                     |
| Cyberduck GUI | https://cyberduck.io/                |
| Globus        | https://www.globus.org/              |

## AWS S3

We had a limited trial for the service and so testing was not able to be carried out to completion. Globus's CLI was used in a script to automate transfers over a period of about a week. That script has been included in this repository along with the output csv files, R plotting script, and output plots. The available script has been updated to include a Google Drive connection (a fairly trivial change) and may be added to the Google Drive section in the future.

## CyVerse

Files were transferred between HPC and CyVerse using iRODS. As in the tests above, six individual dummy files were transferred five times. The means and standard errors were then found for the transfer speeds for each test and plotted in R. 
