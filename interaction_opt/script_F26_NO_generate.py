#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import platform
import sys
import re
#import numpy as np
# module NumPy SciPy
import shutil



# "input_quad_type" : file_name           : input to modify <---------------------------- file expected to be read
# "input_quad_i"    : file_name_in        : input modified
# "out_quad_i"      : file_name_out       : output file
# "quad_i/"         : directory_name      : directory where calculations are done
# "quad_i.sh"       : file_name_to_submit : file to submit

input_file_name="F26_optimized_with_Berggren_basis.in"
file_root = "dir_Li_fit"
file_name_in_root = "input_" + file_root
file_name = file_name_in_root + "type"
file_name_out_root = "out_F26_" + file_root
workspace = "workspace"
file_name_job_out = "_qsub.out"

list_patterns = ["SVD_cutoff"]


def float_range (min_val , max_val , num_val):
	if min_val > max_val:
		print ("float_range: minimum greater than maximum")
		sys.exit(0)

	result = num_val*[None]
	step = (max_val - min_val)/num_val
	for i in range (num_val):
		result[i] = min_val + i*step

	return result


def replace_in_file (file_name , list_new_str , file_name_in):
	# open the future modified file
	file_out = open (file_name_in , "w")

	# open the original file
	file_name_path = "../" + file_name
	with open (file_name_path) as file_in:
		# for each line
		for line in file_in:
			# search each pattern to be replaced and replace it
			for pattern , new_str in zip (list_patterns , list_new_str):
				line = line.replace (pattern , new_str)

				# write the line in the new file once all patterns have been replaced
				#file_out.write (re.sub (pattern , new_str , line))
			file_out.write (line)

		file_in.close ()

	file_out.close ()
	#os.rename (file_name_in , file_name)


# fullname = os.path.join (dirpath , file_name)


#######################################################################
def write_script_to_submit (file_name_job_out , file_name_in , file_name_out , directory_name):
	HOME_path = os.getcwd ()
	SCRATCH_path = "/mnt/gs18/scratch/users/" + str(HOME_path[20:])
	string = \
		"#!/bin/bash -login" + " \n" +\
		"#SBATCH --time=00:20:00 "+ "\n" + \
		"#SBATCH --ntasks=2 " +"\n" + \
		"#SBATCH --cpus-per-task=20 " + "\n" +\
		"#SBATCH --mem=100G " + "\n" + \
		"#SBATCH --job-name " + directory_name + "\n\n" +\
		"module purge "+"\n"+\
		"module load GNU/7.3.0-2.30 " +" \n" +\
		"module load OpenMPI/3.1.1 " + "\n\n" +\
		"cp " + HOME_path+"/"+file_name_in + "  " + SCRATCH_path +"\n\n"+\
		"cp " + HOME_path+"/GSM_opt_exe  "+ SCRATCH_path +"\n\n"+\
		"cd " + str(SCRATCH_path) + "\n\n"+\
		"mpirun -np 2 -map-by node -bind-to none ./GSM_opt_exe <"+file_name_in +" > "+ file_name_out+"\n\n"+\
		"cp "+SCRATCH_path + "/"+file_name_out+"  "+HOME_path 
		#"./mol_exe < " + file_name_in + " > " + file_name_out + "\n\n"
		#"qstat -f ${PBS_JOBID}\n" + \
		#"showstart ${PBS_JOBID}"

	return string

#module load GNU/4.4.5b
#module load OpenMPI/1.4.3
#module load LAPACK
#module load BLAS
#module load FFTW

#######################################################################

# open a typical input file
# replace values using the "id_" system
# write the new input file
# generate a bash script to be submitted for the input file
# submit via qsub
# iterate over the next set of values

def main ():
	#num_a = 20
	#id_a_val_tab = float_range (0.0012000135 , 0.0012000145 , num_a)

	id_a_val_tab=[]
	id_a_start_val_tab =[]
	id_kN_tab=[]
	id_E_start_DIM=[]	#save the starting energy for DIM
	id_G_start_DIM=[]	#save the starting gamma for DIM
	for line in open ("SVD_cut_limit"):
		values = line.strip ("\n").split ()
		id_kN_tab.append(values[0])

##	The following two lines are prepared to build mirror directories in scratch
	HOME_path = os.getcwd ()
	SCRATCH_path = "/mnt/gs18/scratch/users/"+ str(HOME_path[20:])	
	#i = 0
	#for id_a_index in range (0 , num_a):
	#for id_a_val in id_a_val_tab:
	#for index, id_a_val in enumerate(id_a_val_tab):
	for id_a_val in id_kN_tab:
		# create the directory where calculations are done and move inside
		#directory_name = file_root + str (i)
		directory_name = file_root + id_a_val
		os.system ("mkdir " + directory_name)
		os.system ("mkdir " + SCRATCH_path +"/"+ directory_name)
	##	shutil.copyfile ("script_qsub.qsub", directory_name + "/script_qsub.qsub")
		shutil.copyfile ("GSM_opt_exe" , directory_name + "/GSM_opt_exe")
		os.chmod (directory_name + "/GSM_opt_exe" , 0o755)
		os.chdir (directory_name)

################workspace and node_* files are built only in the scratch
		os.chdir(SCRATCH_path+"/"+directory_name)
		os.system ("mkdir "+ workspace)
		os.chdir (workspace)
		for i in range(40):
			os.system(" mkdir " + " node_"+str(i))
		os.chdir (HOME_path+"/"+directory_name)

		# create the file for this set of values
		file_name_in = file_name + id_a_val

		list_new_str = [id_a_val]
		replace_in_file (input_file_name , list_new_str , file_name_in)	

		#file_name_out = file_name_out_root + str (i)
		file_name_out = file_name_out_root + id_a_val

		os.system (" ls " + file_name_in +" > input_file")

		#os.system ("qsub " + " script_qsub.qsub " )


		# write the script to submit
		file_name_to_submit = directory_name + ".sb"
		with open (file_name_to_submit , "w+") as f2:
			f2.write( write_script_to_submit (file_name_job_out , file_name_in , file_name_out , directory_name))
		f2.close ()

		# submit and exit the directory
		os.system ("sbatch " + file_name_to_submit)
		os.chdir ("..")

		#i = i + 1

main ()



