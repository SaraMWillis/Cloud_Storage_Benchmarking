import datetime, os, sys, subprocess,re, cProfile, pstats, csv, io
from io import BytesIO as StringIO


'''
Author : Sara Willis
Date   : November 25, 2019

This script is used to run benchmarking tests on transfers to/from Cyverse using irods. 
The tests can be performed two ways:

3) HPC               --> Cyverse
4) Cyverse           --> HPC

The output from these tests is saved as a csv file of the form "irods_[source]_to_[destination].csv" and 
will be automatically formatted for the user.



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

# Below are the paths and names for the test files that will be transferred to/from
# google drive.

# The user must specify the filesize in the dummy file's filename! This is so labels
# can be created for users in the output. The file size must be specified in the format:
# [Prefix, i.e. B, M, G,...][size value], for example 10MB

file_location = '/extra/sarawillis/'

file_names = ['Temp_1M_irods.txt','Temp_10M_irods.txt','Temp_100M_irods.txt','Temp_1G_irods.txt','Temp_10G_irods.txt','Temp_100G_irods.txt']

number_of_tests_per_filesize = 5

file_integrity_check = True

# File transfer direction:
# 'Upload'   : Local Machine --> Cyverse
# 'Download' : Cyverse       --> Local Machine 
Direction = 'Upload'

# irods commands
irods_upload_no_check = 'iput %s'
irods_upload_with_check = 'iput -K %s'

irods_download_no_check = 'iget %s %s'
irods_download_with_check = 'iget -K %s %s'

irods_list = 'ils'
irods_remove = 'irm %s'


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



def RemoveRemoteFile(filename):
    os.system('ils > files_in_remote.out')
    file_found = False
    with open('files_in_remote.out','r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 0 and filename in row[0]:
                file_found = True
                break
            else:
                pass
    if file_found == True:
        os.system(irods_remove%filename)
    if os.path.exists('files_in_remote.out') == True:
        os.remove('files_in_remote.out')
    return    
    

#####################################################################################


'''
This submodule executes the command to transfer the specified dummy file either
to or from Google Drive with a profilers that captures the amount of time
taken.
'''
def PerformProfileAnalysis(irods_execution_command,filename_with_path):
        
    # We use cProfile as our profiler
    cProfile.run('os.system(irods_execution_command)', 'restats')

    # We want to be able to pull the output from the cProfile run so we can store
    # it for later analysis. To do this, we redirect stdout in a way we can use.
    sysout = sys.stdout

    sys.stdout = io.StringIO()
    
    # We use the pstats module to pull the times listed for each command execution 
    p = pstats.Stats('restats')
    p.strip_dirs().sort_stats(-1).print_stats('posix.system')
    stats_out = sys.stdout.getvalue()

    # We redirect the stdout back to the terminal
    sys.stdout = sysout
    upload_stats =[[k for k in sublist if k!= ''] for sublist in [j.split(' ') for j in [i for i in stats_out.split('\n') if i != ''][-2:] if j != '']]
    upload_time = float({j:k for j,k in zip(upload_stats[0],upload_stats[1])}['cumtime'])
    exact_file_size = os.path.getsize(filename_with_path)

    profile_time = exact_file_size/upload_time/float(1e6)
    return profile_time


def CreateOutputFilename(Direction, file_integrity_check):
    if Direction == 'Upload':
        output_prefix = 'HPC_to_Cyverse'
    elif Direction == 'Download':
        output_prefix = 'Cyverse_to_HPC'
    else:
        print('Please specify a valid option for file transfer direction')
        sys.exit(0)

    if file_integrity_check == True:
        output_filename = output_prefix + '_with_integrity_check.csv'
    else:
        output_filename = output_prefix + '_without_integrity_check.csv'
    return output_filename



def CreateExecutionCommand(Direction, file_integrity_check, file_with_local_path, filename):
    if Direction == 'Upload' and file_integrity_check == False:
        irods_execution_command = irods_upload_no_check%file_with_local_path
    elif Direction == 'Upload' and file_integrity_check == True:
        irods_execution_command = irods_upload_with_check%file_with_local_path
    elif Direction == 'Download' and file_integrity_check == False:
        irods_execution_command = irods_download_no_check%(filename, file_with_local_path)
    elif Direction == 'Download' and file_integrity_check == True:
        irods_execution_command = irods_download_with_check%(filename, file_with_local_path)
    return irods_execution_command


#####################################################################################
#                                 Program Executes                                  #
#####################################################################################

start_time = datetime.datetime.now()
print('Program Executing\nCurrent Time: %s\n\n'%start_time)

output_filename = CreateOutputFilename(Direction, file_integrity_check)


with open(output_filename, 'w') as f:
    f.write('FileSize,EstimatedSpeed\n')
f.close()


for filename in file_names:

    file_size = PullFileSizeFromFilename(filename)

    irods_execution_command = CreateExecutionCommand(Direction, file_integrity_check, file_location+filename, filename)

    for i in range(number_of_tests_per_filesize):
        if Direction == 'Upload':
            RemoveRemoteFile(filename)
        elif Direction == 'Download':
            if os.path.exists(file_location+filename) == True:
                os.system('rm %s%s'%(file_location,filename))
  
        profile_time = PerformProfileAnalysis(irods_execution_command, file_location+filename)

        with open(output_filename,'a') as f:
            f.write('%s,%s\n'%(file_size,profile_time))
        f.close()   

if os.path.exists('./restats'):
    os.remove('restats')

print('Analysis Complete\nTime Taken: %s'%(datetime.datetime.now()-start_time))
