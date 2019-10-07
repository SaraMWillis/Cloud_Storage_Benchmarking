import os, sys, csv, cProfile, io, pstats, re, datetime

'''

Author : Sara Willis
Date   : October 1, 2019

This script is used to run benchmarking tests on transfers to/from AWS S3 using the Globus CLI. 

The tests can be performed four ways:

1) Personal Computer --> AWS S3
2) AWS S3            --> Personal Computer
3) HPC               --> AWS S3
4) AWS S3            --> HPC

This script outputs a csv file where it prints the file sizes of the transfers and their associated transfer speeds.

'''

#####################################################################################
#                                   User Options                                    #
#####################################################################################


# Options:
#   1) HPC
#   2) Personal Computer
#   3) AWS
#   4) Gdrive
Source                           = 'HPC'
Destination                      = 'AWS'


# Globus, by default, checks the integrity of files after they've been transferred. This can
# greatly slow down the whole process. This option allows the checksum process to be turned off.
Checksum = False


# Globus Keys -- These can either be found in the Globus site: https://app.globus.org/endpoints
# or can be extracted by searching for endpoints using the Globus CLI endpoint search, eg:
# globus endpoint search arizona#sdmz-dtn
# For more information on Globus CLI commands, you can use the following commands:
# globus --help
# globus list-commands
personal_computer_key            = ''
HPC_filexfer_node_key            = ''
AWS_S3_key                       = ''
Gdrive_key                       = ''

# Paths within endpoints where files should be transferred from/to
personal_computer_file_directory = ''
hpc_file_directory               = ''
AWS_S3_home_directory            = ''
Gdrive_file_directory            = ''


# Names of dummy files used for transfer benchmarking
filenames                        = ['Example_filename_1','Example_filename2']

number_of_transfers_per_file     = 5

# Globus output will be collected in temporary files for processing
globus_output_file               = 'globus_output.txt'
globus_summary_name              = 'globus_task_summary.txt'



#####################################################################################
#                                    Submodules                                     #
#####################################################################################



# Globus output is redirected to a text file so we can grab the data we need. Once
# the file has been written, this tiny module will grab the relevant data for us. It
# just needs the filename and the name of the entry. All Globus output is stored in
# the format:
#
#   entry1 : <relevant data>
#   entry2 : <relevant data>
#   ...

def ExtractGlobusOutput(filename, entry_name):
    with open(filename,'r') as f:
        reader = csv.reader(f)
        for row in reader:
            message = row[0].split(':')
            if message[0] == entry_name:
                relevant_output = message[1].replace(' ','')
                break
    if os.path.exists(filename) == True:
        os.remove(filename)
        
    return relevant_output



#...................................................................................#



# Though Globus will overwrite files at the destination endpoint, I've chosen
# to delete files if they exist in the event that overwriting interferes
# with the speed of the transfer. I doubt it will mess with anything,
# it could be something to test in the future, but I'll just avoid it
# for the time being. 
def DeleteDestinationFile(destination_path,filename):
    temp_filename = 'temp.txt'

    # List all files available in the destination 
    os.system('globus ls '+destination_path+' >'+temp_filename)
    file_exists = False
    with open(temp_filename,'r') as f:
        reader =csv.reader(f)
        for row in reader:
            # Searches our filename against the destination to see
            # if it already exists
            if row[0] == filename:
                file_exists = True
                break
            
    if file_exists:

        # If the file exists, we delete it from the destination and wait until
        # the deletion is complete so Globus tasks don't start dogpiling
        os.system('globus delete '+destination_path+filename + ' >'+temp_filename)
        task_ID = ExtractGlobusOutput(temp_filename, 'Task ID')
        os.system('globus task wait '+task_ID)

    if os.path.exists(temp_filename) == True:
        os.remove(temp_filename)
        
    return
        

#####################################################################################
#                               Program Executes Below                              #
#####################################################################################

start_time = datetime.datetime.now()
print('Program Executing\nCurrent Time: %s'%start_time)
sys.stdout.flush()


# Used to convert all speeds to MB/s for uniformity in results
prefix_dictionary = {'B':1,'K':float(1e3), 'M':float(1e6),'G':float(1e9)}

# Paths used by Globus to interact with files
personal_computer_path = ':\\'.join([personal_computer_key,personal_computer_file_directory]) if personal_computer_file_directory[0]=='~' else ':'.join([personal_computer_key,personal_computer_file_directory])
HPC_filexfer_node_path = ':\\'.join([HPC_filexfer_node_key,hpc_file_directory]) if hpc_file_directory[0]=='~' else ':'.join([HPC_filexfer_node_key,hpc_file_directory])
AWS_S3_path = ':\\'.join([AWS_S3_key,AWS_S3_home_directory]) if AWS_S3_home_directory[0]=='~' else ':'.join([AWS_S3_key,AWS_S3_home_directory])

# So we don't need to mess with all the various combinatorics induced
# by three transfer to/from options, we create a dictionary so we'll only
# need one command 
transfer_options = {'Personal Computer': {'Key'      : personal_computer_key,
                                          'Location' : personal_computer_file_directory,
                                          'Path'     : personal_computer_path},
                    'HPC'              : {'Key'      : HPC_filexfer_node_key,
                                          'Location' : hpc_file_directory,
                                          'Path'     : HPC_filexfer_node_path},
                    'AWS'              : {'Key'      : AWS_S3_key,
                                          'Location' : AWS_S3_home_directory,
                                          'Path'     : AWS_S3_path}
                    }

source_path = transfer_options[Source]['Path']
destination_path = transfer_options[Destination]['Path']

# The output file will be in csv format with the transfer speeds and the file sizes
output_filename = 'GlobusBenchmarkingTest_%s_to_%s.csv'%(Source.replace(' ',''),Destination.replace(' ',''))
if Checksum == False:
    output_filename.replace('.csv','_NoChecksum.csv')

# We write the heading and close the file. This action will overwrite any previous
# files existing in the working directory with the same name
output_file = open(output_filename,'w')
output_file.write('FileSize,GlobusSpeedEstimate\n')
output_file.close()


for filename in filenames:
    # For the time being, the sizes of files are stored in their filenames. Later,
    # I might change this as it's a bit cumbersome
    file_size = re.findall(r"[0-9]+[MGKB]B?",filename)
    if len(file_size) == 0:
        print('\n\nFile Size Required in Dummy Filename!\nFuture versions may remove this requirement.\n\n')
        sys.exit(0)
    else:
        file_size = file_size[0]

        
    for count in range(0,number_of_transfers_per_file):
        
        DeleteDestinationFile(destination_path,filename)

        # Initiates a transfer and pulls the job ID
        if Checksum == False:
            os.system('globus transfer --no-verify-checksum '+source_path+filename+' '+destination_path+filename + ">"+globus_output_file)
        else:
            os.system('globus transfer '+source_path+filename+' '+destination_path+filename + ">"+globus_output_file)
        task_ID = ExtractGlobusOutput(globus_output_file, 'Task ID')

        # Waits while the transfer is performed so jobs don't dogpile and we can
        # retrieve Globus transfer estimates 
        os.system('globus task wait '+task_ID)

        # Retrieves Globus' estimates 
        os.system('globus task show '+task_ID + '>'+globus_summary_name)
        
        transfer_speed_bps = float(ExtractGlobusOutput(globus_summary_name,'Bytes Per Second'))

        # The results file is opened, appended to, and closed each iteration so
        # in case the program terminates unexpectedly, results are not lost.
        output_file = open(output_filename,'a')
        output_file.write('%s,%s\n'%(file_size,transfer_speed_bps/prefix_dictionary['M']))
        output_file.close()

# The program is fastideous and cleans up after itself. Well done, program.
if os.path.exists(globus_output_file) == True:
    os.remove(globus_output_file)
if os.path.exists(globus_summary_name) == True:
        os.remove(globus_summary_name)

print('Program Complete\nTime Taken: %s'%(datetime.datetime.now()-start_time))
sys.stdout.flush()
