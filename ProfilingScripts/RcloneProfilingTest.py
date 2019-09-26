import datetime, os, sys, subprocess,re, cProfile, pstats, io, csv, json
from io import BytesIO as StringIO


'''
Author : Sara Willis
Date   : September 13, 2019

This script is used to run benchmarking tests on transfers to/from Google Drive using rclone. 

The tests can be performed four ways:

1) Personal Computer --> Google Drive
2) Google Drive      --> Personal Computer
3) HPC               --> Google Drive
4) Google Drive      --> HPC

The output from these tests is saved as a csv file of the form "Rclone_[source]_to_[destination].csv" and 
will be automatically formatted.

Dependencies
------------

The user will need to have rclone set up on the machine where they are running these benchmarking tests. 

Download instructions are available on a shared overleaf document which summarizes the
tests that have been run with this script as well as others in this repository: 

https://www.overleaf.com/read/cnbzpsmbdbqp

** When running this script on HPC, use the filexfer node and do not use the login nodes! **

You may access the filexfer node using the standard command: ssh NetID@filexfer.hpc.arizona.edu


'''

#####################################################################################
#                                   User Options                                    #
#####################################################################################

'''
This is the only section that needs to edited by the user to customize the program
for their use.

======================================================================================================
All User Options are specific to my machine and are included as examples. You will 
want to replace my commands with those specific to you.
======================================================================================================

'''

# The filexfer node only runs Python 2 which uses a few slightly different commands
# from python3 which is what I use on my personal computer. Specifying the version
# will ensure the correct commands are used. 
python_version = '3'

# Either 'Personal Computer' or 'HPC'
host_machine= 'Personal Computer'

# The user should already have dummy files set up on their personal computer of varying sizes.
# The filenames should be of the form: Temp_[N][XB].txt. Mine say Globus because those were
# initially what I created the tests for and never changed them.

# If the user does not have the dummy files uploaded to Google Drive yet, they will want to
# either transfer them there or run the upload tests first.

# The dummy files must have their paths specified
local_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']

# The dummy files on HPC should be stored in extra given the space restrictions in their
# home directory. The files need their path specified.
hpc_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']

# Each filesize will be uploaded multiple times to get a good sampling.
number_of_tests_per_filesize = 5

# File transfer direction:
# 'Upload'   : Local Machine --> Gdrive
# 'Download' : Gdrive        --> Local Machine 
Direction = 'Download'

# Below you need to use the profile name you gave to your Google Drive connector during
# the rclone setup process

# ** The options below are specific to my account and should be changed! **

# PC  : MyGoogleDrive 
# HPC : mygoogledrive
GoogleDriveRemote = 'MyGoogleDrive'

# Collects junk output and disposes of it
junk_file = 'temp.out'

# Rclone commands for uploading, downloading, and deleteing files
rclone_download_command = 'rclone copyto '+GoogleDriveRemote+':%s %s'
rclone_upload_command = 'rclone copyto %s '+GoogleDriveRemote+':%s'
rclone_delete_command = 'rclone deletefile '+GoogleDriveRemote+':%s >'+junk_file



#####################################################################################
#                                   Submodules                                      #
#####################################################################################

'''

This function transfers the specified file to/from Google Drive. It uses the profiler 
cProfile to extract the time taken to execute the transfer and returns to the user 
the estimated transfer speed

'''

def RunProfilingTest(local_file_path,transfer_filename):

    # The profiler requires that the transfer command is a global variable
    global specific_rclone_transfer_command

    # The specific transfer command is defined based on the file that's being moved
    # and whether the test is for uploading or downloading files
    if Direction == 'Upload':
        specific_rclone_transfer_command = rclone_upload_command%(local_file_path,transfer_filename)
    elif Direction == 'Download':
        specific_rclone_transfer_command = rclone_download_command%(transfer_filename,local_file_path)


    cProfile.run('os.system(specific_rclone_transfer_command)','restats')
    
    # Extracts the statistics from the profiler which otherwise would have been piped to
    # stdout
    sysout = sys.stdout
    if python_version == '2':
        sys.stdout = StringIO()
    elif python_version == '3':
        sys.stdout = io.StringIO()
    p = pstats.Stats('restats')
    p.print_stats()
    p.strip_dirs().sort_stats(-1).print_stats('posix.system')
    stats_out = sys.stdout.getvalue()
    sys.stdout = sysout

    # This ugly mess is how I decided to extract data from human-readable format. The original format
    # was a space-delimited table. Below uses list-comprehension to break apart the data points
    # and the headings into separate sublists.
    upload_stats =[[k for k in sublist if k!= ''] for sublist in [j.split(' ') for j in [i for i in stats_out.split('\n') if i != ''][-2:] if j != '']]

    # A dictionary is created from the zipped lists and the time taken to perform the transfer is pulled
    upload_time = float({j:k for j,k in zip(upload_stats[0],upload_stats[1])}['cumtime'])

    # The exact filesize is extracted in bytes, converted to megabytes, and used to generate the transfer speed
    exact_file_size = os.path.getsize(local_file_path)
    transfer_speed = (exact_file_size/float(1e6))/upload_time
    return transfer_speed


#####################################################################################


'''
Since unmodified Rclone doesn't overwrite files, we'll manually remove files from our destination prior
to performing the transfer.
'''

def Remove_file_from_dest(filename,local_filepath):
    if Direction == 'Upload':

        # Rather than go through a whole song and dance of checking whether the temporary file already
        # exists in Google Drive, we'll just try to remove it and not worry about it if rclone can't
        # find it. 
        try:
            os.system(rclone_delete_command%filename)
        except:
            pass
        
    # If we're downloading the file, we'll remove the file from our local machine before proceeding.
    else:
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
            
    # Any complaints rclone gave us about the file availability are junked
    if os.path.exists(junk_file):
        os.remove(junk_file)
    return
    
#####################################################################################
#                                 Program Executes                                  #
#####################################################################################

# Generates the output filename for the user
upload_naming_tuple = (host_machine.replace(' ',''),'GoogleDrive') if Direction == 'Upload' else ('GoogleDrive',host_machine.replace(' ',''))
output_file_name = 'RcloneSpeedTest_%s_to_%s.csv'%upload_naming_tuple

# Loads the paths and filenames to the dummy files being transferred
if host_machine == 'Personal Computer':
    file_names = local_file_names
elif host_machine == 'HPC':
    file_names = hpc_file_names
else:
    print('Please Specify Your Local Machine')
    sys.exit(0)

# Writes the header and closes the file.
# *CAUTION* Overwrites preexisting files, so make sure prior to rerunning this script that
# you're not erasing anything you don't want to.
OutputFile = open(output_file_name,'w')
OutputFile.write('FileSize,ProfiledSpeed\n')
OutputFile.close()

# Each file is transferred individually and information is collected about it
for local_file_path in file_names:
    transfer_filename = local_file_path.split('/')[-1]
    file_size = transfer_filename.split('_')[1]

    # The user-specified number of tests per filesize is used to transfer files a given
    # number of times
    for i in range(0,number_of_tests_per_filesize):

        # Files are removed from the destination prior to executing the transfer
        Remove_file_from_dest(transfer_filename,local_file_path)
        
        transfer_speed = RunProfilingTest(local_file_path,transfer_filename)

        # The output gets written to every iteration so if some error that shuts the program down,
        # progress is not lost
        OutputFile = open(output_file_name,'a')
        OutputFile.write('%s,%s\n'%(file_size,transfer_speed))
        OutputFile.close()
