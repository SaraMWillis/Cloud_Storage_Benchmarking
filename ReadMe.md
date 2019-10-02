# Cloud Storage Benchmarking

## About

This repository contains all the scripts used to test upload/download speeds when transferring files to/from various cloud sites.

## Current Cloud Storage Options
 * Google Drive
 * AWS S3

## Google Drive
The tests all use various Google Drive CLI software packages to transfer dummy files. A transfer can either be completed as an upload or a download. It is designed so that the user can either complete these transfers from their personal computer or on University of Arizona's HPC filexfer node. As a result, these scripts can either be run using python 2 or python 3 (I have a personal preference for python3 and [python 2 is being sunsetted](https://www.python.org/doc/sunset-python-2/), and because the filexfer node has only python 2 installed). 

The transfer programs that have scripts currently available or are soon-to-be available are:
* rclone
* cyberduck
* gdrive

Additional information on this testing can be viewed on an available [Overleaf Document](https://www.overleaf.com/read/cnbzpsmbdbqp) which is currently a work-in-progress and so may contain unfinished thoughts and other unsightly notes. This document also contains notes on installing the relevant software on both your own personal computer as well as on HPC.

These scripts assume you can call the executables that you are testing. If you are running this script on the HPC filexfer node where you do not have root privileges, you have two options. 
  1) You can alter the execution commands to include the path to the executable
  2) You can add the location of the executable to your system's PATH variable.

If you choose to alter your PATH variable, note that doing so on the command line will only change it for the given session. If you would like to make this permanent, you'll need to edit your .bashrc file. Regardless of how you choose to change your PATH variable, the command is the same:
  ```
  export PATH=$PATH:/path/to/executable/directory
  ```
If you decide to make the change permanent:

  1. On HPC, open the file using ``` vi ~/.bashrc```
  2. Use the command ```shift A``` to edit 
  3. Add the command to edit PATH (see above) to a blank line
  4. Exit editing using ```shift :``` 
  5. Type ```wq``` and then press ```Enter``` to save and exit.


### Programs Used

* Gdrive : https://github.com/gdrive-org/gdrive
* Rclone : https://github.com/rclone/rclone
* Cyberduck CLI : https://duck.sh/
* Cyberduck GUI : https://cyberduck.io/
* Globus : https://www.globus.org/

## AWS S3
