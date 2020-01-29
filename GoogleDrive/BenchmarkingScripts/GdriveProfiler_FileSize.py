import datetime, os, sys, subprocess,re, cProfile, pstats, csv, io
from io import BytesIO as StringIO


'''
Author : Sara Willis
Date   : September 20, 2019


This script is used to run benchmarking tests on transfers to/from Google Drive using Gdrive. 
The tests can be performed four ways:


1) Personal Computer --> Google Drive
2) Google Drive      --> Personal Computer
3) HPC               --> Google Drive
4) Google Drive      --> HPC


The output from these tests is saved as a csv file of the form "Gdrive_[source]_to_[destination].csv" and 
will be automatically formatted for the user.

Dependencies
------------

The user will need to have Gdrive set up on the machine where they are running these benchmarking tests. 
Download instructions are available on a shared overleaf document which summarizes the tests that 
have been run with this script as well as others in this repository: 

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

# Either 'Personal Computer' or 'HPC'
host_machine = 'Personal Computer'

# Below are the paths and names for the test files that will be transferred to/from
# google drive.

# The user must specify the filesize in the dummy file's filename! This is so labels
# can be created for users in the output. The file size must be specified in the format:
# [Prefix, i.e. B, M, G,...][size value], for example 10MB

local_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']

# When transferring files on HPC, it's recommended you store your test files in extra since
# your home directory has limited storage space and some of the larger files may cause
# errors if you exceed your quota.
hpc_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']


number_of_tests_per_filesize = 5


# File transfer direction:
# 'Upload'   : Local Machine --> Gdrive
# 'Download' : Gdrive        --> Local Machine 
Direction = 'Upload'

# If gdrive isn't in your PATH variable, add it with the BASH command:
#  export PATH=$PATH:/path/to/gdrive/executable
# If you decide not to add it, you will need to specify the full path
# to the gdrive executable below
gdrive_upload_command   = 'gdrive upload %s'
gdrive_download_command = 'gdrive download --force --path %s %s'
gdrive_delete_command   = 'gdrive delete %s'

# It can be useful following an upload to keep the last uploaded files in 
# google drive. Particularly if you are running an upload test followed by a download
# test. When set to False, the last copy of the dummy file is not deleted. If set
# to True, all copies will be deleted after the tests have been performed
delete_gdrive_file_after_test = False

# A temporary file where gdrive output will be extracted from. Previous versions of
# this script piped stdout to a variable using suprocess.run, however, this is not
# available for Python 2 and so had to be modified
gdrive_output_file = 'gdrive.out'



#####################################################################################
#                                   Submodules                                      #
#####################################################################################

'''
The file size should be included in the dummy filename so that it can be 
extracted and printed to the output file.

Really, if it were so desired, we could pull the file size from the file itself and
could convert it into a readable format, but I'm on the final iteration of this 
script and am more focused on the results at the moment. I may or may not come back
in the future to change this.
'''

def PullFileSizeFromFilename(filename):
    filename_upper = filename.upper()
    file_size = [i for i in re.findall(r"[0-9]+[MGKB]?",filename_upper) if i != ''][0]
    return file_size



#####################################################################################


'''
Frustratingly, the only way to get Gdrive's printed output running a profiler
that works using both python 2 and python 3 is to write a submodule that forces
the output to a file. 
'''
def RunTransferTest(gdrive_execution_command):
    os.system(gdrive_execution_command+ ' >'+gdrive_output_file)
    return



#####################################################################################




'''
This submodule executes the command to transfer the specified dummy file either
to or from Google Drive with a profilers that captures the amount of time
taken.
'''
def PerformProfileAnalysis(gdrive_execution_command,filename_with_path):
    
    if os.path.exists(gdrive_output_file) == True:
        os.remove(gdrive_output_file)
        
    # We use cProfile as our profiler
    cProfile.run('RunTransferTest(gdrive_execution_command)', 'restats')

    # We want to be able to pull the output from the cProfile run so we can store
    # it for later analysis. To do this, we redirect stdout in a way we can use.
    sysout = sys.stdout

    # The way we catch stdout and turn it into a human-readable format is dependent
    # on the version of Python we're using. If the incorrect version of Python is
    # specified, this program will exit with an error. 
    if python_version == '2':
        sys.stdout = StringIO()
    elif python_version == '3':
        sys.stdout = io.StringIO()
    
    # We use the pstats module to pull the times listed for each command execution 
    p = pstats.Stats('restats')
    p.strip_dirs().sort_stats(-1).print_stats('posix.system')
    stats_out = sys.stdout.getvalue()

    # We redirect the stdout back to the terminal
    sys.stdout = sysout

    # And dissect the stats output to get the details for the execution time. I'd
    # use a more elegant method, but I can't really think of one since the format
    # of the stats output is human-readable, not so much machine-readable.
    # The general idea is to whittle the output columns and their values into nested
    # sublists, to zip those lists together, and then pull the column we want.
    upload_stats =[[k for k in sublist if k!= ''] for sublist in [j.split(' ') for j in [i for i in stats_out.split('\n') if i != ''][-2:] if j != '']]

    # We then create a dictionary and pull the value we're after
    upload_time = float({j:k for j,k in zip(upload_stats[0],upload_stats[1])}['cumtime'])
    
    # To get the transfer speed, we pull the filesize to get the exact size rather than
    # relying on the value we used to generate the file which may or may not be binary.
    # The Linux command truncate can create dummy files with kilo, mega, and giga as
    # base-10 S.I. prefixes, which mkfile on Mac's create files with the prefixes referring
    # to their binary counterparts. Extracting the exact byte size will allow us to
    # standardize our results.
    exact_file_size = os.path.getsize(filename_with_path)

    # We then pull the transfer speed predicted by this profiler and divide by 10^6 to
    # convert to MB/s (S.I. prefixes, not binary)
    profile_time = exact_file_size/upload_time/float(1e6)

    # We then get the gdrive output to get it's estimate for the transfer speed.
    with open(gdrive_output_file,read_option) as f:
        reader = csv.reader(f)
        gdrive_output = ''
        for row in reader:
            gdrive_output += row[0]

    # We use a regular expression to pull the transfer speed
    gdrive_speed_prediction = re.findall(r"[0-9]*\.[0-9]*\s[MGK]?B/s",gdrive_output)[0]
    gdrive_prediction,Scale = gdrive_speed_prediction.split(' ')
    gdrive_prediction = float(gdrive_prediction)/(prefix_dictionary['M']/prefix_dictionary[Scale[0]])

    if delete_gdrive_file_after_test == True and direction == 'Upload':
        UploadID = output.split('\n')[1].split(' ')[1]
        os.system(gdrive_delete_command%UploadID)
        
    return profile_time,gdrive_prediction



#####################################################################################




'''
Google Drive, unlike other Google Drive transfer CLI programs, does not rely on
filenames to execute download/delete commands. Instead, it uses a unique File ID.
You can actually see this ID if you go to one of your google documents and check the
extension after the url: https://docs.google.com/document/d/<fileID>/...
Since it may be necessary to specify 
'''
def FindFileID(filename):

    # A temporary file where filenames are stored
    gdrive_contents = 'gdrive.contents'

    file_id = None

    # We determine if our file is already in google drive  by listing the
    # contents and checking our filename against what's listed. If it is,
    # we collect the file ID
    os.system('gdrive list | grep %s >%s' %(filename,gdrive_contents))
    with open(gdrive_contents,read_option) as f:
        reader = csv.reader(f)
        for row in reader:
            file_id = [i for i in row[0].split(' ') if i != ''][0]

    if os.path.exists(gdrive_contents) == True:
        os.remove(gdrive_contents)
        
    return file_id



#####################################################################################



'''
This function deletes a file with a given name from Google Drive.
gdrive is different from other transfer programs because it allows the user
to store more than one file with a given name because it uses a file id
system as an identifier. It's nice if the user wants to save files with a shared 
name, but is also problematic for this test. If the program does not delete files
as it goes, it will quickly overwhelm the tester's drive account with dummy files.
'''
def RemoveFileFromGdrive(filename):

    file_id = FindFileID(filename)

    if file_id != None:
        print('file found')
        os.system(gdrive_delete_command%file_id) 
            
    else:
        pass

        
    return





#####################################################################################
#                                 Program Executes                                  #
#####################################################################################

# Detects python version
python_version = str(sys.version_info[0])

# How an output CSV file is read is dependent on the python version. At least, if the
# correct read option is not specified, python will run but complain which clutters
# up output. 
global read_option
read_option = 'rU' if python_version == '2' else 'r'


if host_machine == 'Personal Computer':
    file_names = local_file_names
elif host_machine == 'HPC':
    file_names = hpc_file_names


base_output_filename = 'Gdrive_%s_to_%s.csv'
if Direction == 'Upload':
    output_filename = base_output_filename%(host_machine,'HPC')
elif Direction == 'Download':
    output_filename = base_output_filename%('HPC',host_machine)
else:
    print('\nSpecify a valid transfer directon to continue. Options:\n\n\t1) "Upload"\n\t2) "Download"\n')
    sys.exit(0)

# We start by writing the output file's headers to a fresh file and close it
# This will allow us to use the append function later to write our results to
# the output file as they are generated. This ensures that we will get results 
# even if 
output_file = open(output_filename,'w')
output_file.write('FileSize,ProfileSpeed,GdriveEstimate\n')
output_file.close()

# Our prefix dictionary will ensure our results are standardized and printed
# as MB/s. We also are using prefixes as SI units and not binary, which are
# supposed to be kibibytes, etc, but aren't necessarily written that way...
prefix_dictionary = {'B':1,'K':float(1e3), 'M':float(1e6),'G':float(1e9)}


for filename_with_path in file_names:

    filename = filename_with_path.split('/')[-1]

    # The file size should be specified in the filename
    file_size = PullFileSizeFromFilename(filename)
    
    for i in range(0,number_of_tests_per_filesize):

        if Direction == 'Upload':
            gdrive_execution_command = gdrive_upload_command%filename_with_path
            RemoveFileFromGdrive(filename)
        
        else:
            file_id = FindFileID(filename)
            file_path = filename_with_path.replace(filename_with_path.split('/')[-1],'')
            gdrive_execution_command = gdrive_download_command%(file_path,file_id)
  
        profile_speed,gdrive_speed = PerformProfileAnalysis(gdrive_execution_command,filename_with_path)
        
        output_file = open(output_filename,'a')
        output_file.write('%s,%s,%s\n'%(file_size,profile_speed,gdrive_speed))
        output_file.close()
        

if os.path.exists('restats'):
    os.remove('restats')
if os.path.exists(gdrive_output_file):
    os.remove(gdrive_output_file)
