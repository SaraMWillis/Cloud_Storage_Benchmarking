import datetime, os, sys, subprocess,re, cProfile, pstats, csv, io
from io import BytesIO as StringIO


'''
Author : Sara Willis
Date   : September 13, 2019


This script is used to run benchmarking tests on transfers to/from Google Drive using the Cyberduck CLI, duck. 

The tests can be performed four ways:

1) Personal Computer --> Google Drive
2) Google Drive      --> Personal Computer
3) HPC               --> Google Drive
4) Google Drive      --> HPC

This script outputs a csv file where it prints the file sizes of the transfers and their associated transfer speeds 
'''

#####################################################################################
#                                   User Options                                    #
#####################################################################################

NetID = ''

# Choose either Personal Computer or HPC. This will allow the program to find the correct path to the dummy
# files. 
WorkingComputer = 'Personal Computer'

Direction = 'Download'

number_of_tests_per_filesize = 5

# The name of the CSV file where the results will be saved
benchmarking_output_file = 'RcloneProfilingTest_%s_to_%s.out'

# The dummy files and their paths used in this benchmarking test
personal_computer_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']

hpc_file_names = ['/path/to/file/filename_1.txt','/path/to/file/filename_2.txt']

duck_executable_path = 'duck'

# Results from the cyberduck stdout used to pull program-generated speed estimates
cyberduck_output = 'cyberduck_output.out'

# If you run into problems, try manually sending a file so your credentials are established
# prior to rerunning this script
cyberduck_upload_command = duck_executable_path+' --username '+NetID+'@email.arizona.edu --upload "googledrive:My Drive/%s" %s --existing overwrite >'+cyberduck_output

cyberduck_delete_command = duck_executable_path + ' --username '+NetID+'@email.arizona.edu --delete "googledrive:My Drive/%s"'

cyberduck_download_command = duck_executable_path+' --username '+NetID+'@email.arizona.edu --download "googledrive:My Drive/%s" %s --existing overwrite >'+cyberduck_output

# Used to convert Cyberduck output speeds to MB/s 
prefix_dictionary = {'B':1,'K':float(1e3), 'M':float(1e6),'G':float(1e9)}



#####################################################################################
#                                   Submodules                                      #
#####################################################################################

def RunProfilingTest(loadFile):

    global cyberduck_transfer_command
    
    if Direction == 'Upload':
        cyberduck_transfer_command = cyberduck_upload_command%(loadFile.split('/')[-1],loadFile)
    else:
        cyberduck_transfer_command = cyberduck_download_command%(loadFile.split('/')[-1],loadFile)

    
    # Executes the command to upload the temp file to Google Drive with a profiler
    cProfile.run('os.system(cyberduck_transfer_command)','restats')
    #sys.exit(0)
    # For this version of the script, we're not going to generate files as we go since
    # it's too cumbersome to generate files that are over 10GB for a single trials.
    # Instead, we'll be making use of files that have already been created 
    #if Direction == "Upload":
    #    os.system(cyberduck_delete_command%loadFile.split('/')[-1])
    
    # Extracts the statistics from the profiler which otherwise would have been piped to
    # stdout, hence the temporary redirection
    sysout = sys.stdout
    if python_version == '2':
        sys.stdout = StringIO()
    elif python_version == '3':
        sys.stdout = io.StringIO()
    p = pstats.Stats('restats')
    p.strip_dirs().sort_stats(-1).print_stats('posix.system')
    stats_out = sys.stdout.getvalue()
    sys.stdout = sysout

    # Cyberduck upload stats are in a human-readable format. The easiest way I could think
    # of to pull the data I wanted was to 
    upload_stats =[[k for k in sublist if k!= ''] for sublist in [j.split(' ') for j in [i for i in stats_out.split('\n') if i != ''][-2:] if j != '']]


    upload_time = float({j:k for j,k in zip(upload_stats[0],upload_stats[1])}['cumtime'])

    exact_file_size = os.path.getsize(loadFile)
    profile_speed = exact_file_size/upload_time/float(1e6)

    # Cyberduck gives upload speed estimates every second or so. This program collects each
    # estimate and finds the mean speed to compare with the speed predicted by the profiler.
    # This may not be the most accurate estimate, but I decided to pull the data anyway
    predictedSpeeds = []

    if python_version == '2':
        reader_option = 'rU'
    else:
        reader_option = 'r'
        
    # Reads in the Cyberduck instantaneous estimates
    with open(cyberduck_output,reader_option) as f:
        reader = csv.reader(f,dialect=csv.excel_tab)
        for row in reader:
            if len(row) != 0:
                speed_output = re.findall(r"[0-9]*\.[0-9]*\s[MGK]?B/sec",','.join(row))
                if len(speed_output) != 0:
                    predicted_speed, scale = speed_output[0].split(' ')
                    predicted_speed = float(predicted_speed)/(prefix_dictionary['M']/prefix_dictionary[scale[0]])
                    predictedSpeeds.append(predicted_speed)
    os.system('rm %s restats'%cyberduck_output)

    # Given what I'm trying to do (run a profiler on the file transfer node), I can't use
    # numpy at the moment, so I'm brute-forcing means
    predictedSpeeds_mean = sum(predictedSpeeds)/len(predictedSpeeds)
    return predictedSpeeds_mean, profile_speed



#####################################################################################
#                                 Program Executes                                  #
#####################################################################################

# Detects python version
python_version = str(sys.version_info[0])

# Which computer is being used determines where this script looks for the dummy scripts
if WorkingComputer == 'Personal Computer':
    file_names = personal_computer_file_names
elif WorkingComputer == 'HPC':
    file_names = hpc_computer_file_names
else:
    print('\nPlease specify a valid working computer\n')
    sys.exit(0)

if Direction == 'Download':
    benchmarking_output_file%('GoogleDrive',WorkingComputer.replace(" ",""))
elif Direction == 'Upload':
    benchmarking_output_file%(WorkingComputer.replace(" ",""),'GoogleDrive')
else:
    print('Please specify file transfer direction:\n\t1) Download\n\t2) Upload')
    sys.exit(0)



output_file = open(benchmarking_output_file,'w')
output_file.write('FileSize,ProfiledSpeed,cyberduckEst\n')
output_file.close()


for loadFile in file_names:

    for trial in range(0,number_of_tests_per_filesize):

        duck,profile = RunProfilingTest(loadFile)
        # Results are printed each iteration 
        output_file = open(benchmarking_output_file,'a')
        output_file.write('%s,%s,%s\n'%(loadFile.split('/')[-1].split('_')[1],profile,duck))
        output_file.close()

    
