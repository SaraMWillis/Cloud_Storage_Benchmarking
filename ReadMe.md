# Cloud Storage Benchmarking

## About

This repository contains all the scripts, output CSV files, and figures used and generated from testing upload/download speeds  to/from various cloud storage repositories. A comprehensive summary of all results is included in the available PDF Cloud_Storage_Benchmarking.pdf. The document is still under construction and will be periodically updated. The live version is available for viewing as an [Overleaf Document](https://www.overleaf.com/read/cnbzpsmbdbqp) with the caveat that the compilation times are getting longer and longer due to the number of included image files. 

Some tests below rely on CLI programs installed on a remote machine where user's don't have root permissions. There are instructions for installing these programs in the supplied PDF. To add the installed programs to your PATH variable, edit your .bashrc file to include the following:

```
export PATH=$PATH:</path/to/executable/directory>
```

## Current Tested Cloud Storage Options
 * Google Drive
 * AWS S3

## Google Drive
The tests in this repository all use various Google Drive software packages to transfer dummy files where a transfer denotes either an upload or a download. All available output csv files, R plotting scripts, and figures are from a variety of programs which include both GUI and CLI programs. Scripts automating available CLI programs rclone, cyberduck, and gdrive are additionally available. Graphical programs were run manually. 

Note: a script has recently been written for the Globus CLI and has been tested with AWS S3. An option for transferring to/from Google Drive has been included. Once testing takes place, I will include it in the Google Drive repository. Until then, it will remain solely in the AWS repository. 

The available scripts are designed so that the user can either run them from their personal computer or on University of Arizona's HPC filexfer node. As a result, they have been designed so they can either be run using python 2 or python 3 (I have a personal preference for python3 and [python 2 is being sunsetted](https://www.python.org/doc/sunset-python-2/), and because the filexfer node has only python 2 installed). 


### Programs Used

| Gdrive        | https://github.com/gdrive-org/gdrive |
|---------------|--------------------------------------|
| Rclone        | https://github.com/rclone/rclone     |
| Cyberduck CLI | https://duck.sh/                     |
| Cyberduck GUI | https://cyberduck.io/                |
| Globus        | https://www.globus.org/              |

## AWS S3

The most recent cloud storage platform to be tested is Amazon's AWS S3. We have a limited trial for the service and so testing was limited. Specifically, Globus's CLI was used in a script to automate transfers over a period of about a week. The script that automates the transfers has been included in this repository along with the output csv files and their plots. The script has been updated to include a Google Drive connection (a fairly trivial change).
