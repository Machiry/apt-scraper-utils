##########################################################################
#
# This script will download all the C/C++ package tar sources to a local 
# folder -> extract, build and install the tar sources -> extract the .bc 
# files from the installed archives using wllvm
# 
# invoke this script with sudo, so that packages can be installed
#
# Make sure that clang and llvm-link are set to the same llvm version before 
# invoking this script. 
#
##########################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library
import os
import subprocess
import sys
import re

#make sure paths are set correctly 
# path the the mirror file
source_file_to_read_packages_from = "/pathto/apt-scraper-utils/Sources"

#mirror url 
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"

#sources will be downloaded here
local_download_folder_for_sources = "/pathto/apt-scraper-utils/apt_scraper_sources"

#script will extract and build it here
extracted_tar_sources = '/pathto/apt-scraper-utils/extracted_tar_sources'

#bitcodes will here extracted here
afl_fuzzing_sources = '/pathto/apt-scraper-utils/afl_sources'

if not os.path.isdir(local_download_folder_for_sources):
    cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(afl_fuzzing_sources):
    cmd = "(" + "mkdir " + afl_fuzzing_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(extracted_tar_sources):
    cmd = "(" + "mkdir " + extracted_tar_sources + ")"
    subprocess.call(cmd, shell=True)


p = PackageManager(source_file_to_read_packages_from, mirror_url)
p.build_pkg_entries()

p.dump_to_pickled_json("dummp.picked.json")
p2 = PackageManager.from_picked_json("dummp.picked.json")


packages_available = p.all_pkg_entries

#for making package installation noninterative
cmd = "(" + "export DEBIAN_FRONTEND=noninteractive" + ")"
subprocess.call(cmd, shell=True)

for pkgs in packages_available:
    
    reverse_dependencies = []
    dependency_list = p.dependency_map[pkgs]
    for dependencies in dependency_list:
        # install all reverse dependencies might be too slow (not necessary), uncomment if needed
        #for reverse_deps in p.reverse_dependency_map[dependencies]:
        #    subprocess.call(['sudo apt -yq install', str(reverse_deps)], shell=True)        
        subprocess.call(['sudo apt -yq install', str(dependencies)], shell=True)
        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
    
    for lib in reverse_dependencies:
        if (find_library(lib) != None):
            print()
            print("...")
            print("DOWNLOADING "+ str(pkgs) + "from the mirror...")
            print("...")
            p.download_package_source(pkgs, local_download_folder_for_sources)
            break


#Extract the tar sources, build them and install and put them in another folder
for subdir, dirs, files in os.walk(local_download_folder_for_sources):
    
    for File in files:
        if ".orig." in str(File):

            #extract the archive
            cmd = "(" + "cd " + local_download_folder_for_sources + " && " + "tar -xf " + str(File) + ")"
            subprocess.call(cmd, shell=True)

            archive_parts = File.split(".orig")
            underscore_split = archive_parts[0].split("_")
            
            directory_name = ""
            try:
                directory_name = str(underscore_split[0]) + "-" + str(underscore_split[1])
            except:
                continue

            configure_path = local_download_folder_for_sources + "/" + directory_name + "/" + "configure"
            
            #check if a configure script exists in the directory
            if( os.path.exists(configure_path) == True ):
                print(File)
                #now cd into the archive
                cmd = "(" + "cd " + local_download_folder_for_sources + "/" + directory_name + " && " + "export LLVM_COMPILER=clang" + " && " + "export WLLVM_OUTPUT_LEVEL=Debug" + " && " + "export WLLVM_OUTPUT_FILE=/tmp/" + str(File) +  "_wllvm.log"  + " && " + "CC=wllvm CXX=wllvm++ yes '' | ./configure" +  " && " + "make CC=wllvm CXX=wllvm++ -j12" + " && " + "make CC=wllvm CXX=wllvm++ install DESTDIR=" + extracted_tar_sources + "/" + directory_name  + ")"
                subprocess.call(cmd, shell=True)

#run extract-bc to get the bit-code files form the binaries
for subdir, dirs, files in os.walk(extracted_tar_sources):

    if subdir.endswith("/bin"):

        for File in files:
            cmd = "(" + "cd " + subdir + " && " + "extract-bc " + File + " && " + "mv " + File + ".bc " + afl_fuzzing_sources + ")"
            subprocess.call(cmd, shell=True)
            
#run extract-bc to get bitcodes from library files if any
for subdir, dirs, files in os.walk(extracted_tar_sources):

    if subdir.endswith("/lib"):
        
        for File in files:
            if (".a") in File:
                cmd = "(" + "cd " + subdir + " && " + "extract-bc -b " + File + " && " + "mv " + File + ".bc " + afl_fuzzing_sources + ")"
                subprocess.call(cmd, shell=True)



