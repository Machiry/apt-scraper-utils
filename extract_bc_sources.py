#####################################################################
#
# This script will download all the C/C++ package sources to a local 
# folder
#
######################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library
import os
import subprocess
import sys
import re

source_file_to_read_packages_from = "/home/singhav/Sources"
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"
local_download_folder_for_sources = "/home/singhav/apt_scraper_sources"
tar_sources = '/home/singhav/tar_sources'
extracted_tar_sources = '/home/singhav/extracted_tar_sources'
afl_fuzzing_sources = '/home/singhav/afl_sources'

if not os.path.isdir(local_download_folder_for_sources):
    cmd = "(" + "mkdir " + local_download_folder_for_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(afl_fuzzing_sources):
    cmd = "(" + "mkdir " + afl_fuzzing_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(extracted_tar_sources):
    cmd = "(" + "mkdir " + extracted_tar_sources + ")"
    subprocess.call(cmd, shell=True)

if not os.path.isdir(tar_sources):
    cmd = "(" + "mkdir " + tar_sources + ")"
    subprocess.call(cmd, shell=True)


p = PackageManager(source_file_to_read_packages_from, mirror_url)
p.build_pkg_entries()

p.dump_to_pickled_json("dummp.picked.json")
p2 = PackageManager.from_picked_json("dummp.picked.json")


packages_available = p.all_pkg_entries

for pkgs in packages_available:
    
    reverse_dependencies = []
    dependency_list = p.dependency_map[pkgs]
    for dependencies in dependency_list:
        subprocess.call(['sudo apt install', str(dependencies)], shell=True)
        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
    
    for lib in reverse_dependencies:
        subprocess.call(['sudo apt install', str(lib)], shell=True)
        if (find_library(lib) != None):
            print()
            print("...")
            print("DOWNLOADING "+ str(pkgs) + "from the mirror...")
            print("...")
            p.download_package_source(pkgs, local_download_folder_for_sources)
            break


#Extract the tar sources and put them in another folder
for subdir, dirs, files in os.walk(tar_sources):
    
    for File in files:
        if "orig" in str(File):

            #extract the archive
            cmd = "(" + "tar -xf " + str(File) + ")"
            subprocess.call(cmd, shell=True)

            archive_parts = File.split(".orig")
            underscore_split = archive_parts[0].split("_")
            directory_name = str(underscore_split[0]) + "-" + str(underscore_split[1])

            configure_path = tar_sources + "/" + directory_name + "/" + "configure"
            
            #check if a configure script exists in the directory
            if( os.path.exists(configure_path) == True ):
                print(File)
                #now cd into the archive
                cmd = "(" + "cd " + directory_name + " && " + "export LLVM_COMPILER=clang" + " && " + "CC=wllvm ./configure" +  " && " + "make" + " && " + "make install DESTDIR=" + extracted_tar_sources + directory_name  + ")"
                subprocess.call(cmd, shell=True)

for subdir, dirs, files in os.walk(extracted_tar_sources):

    if subdir.endswith("/bin"):

        for File in files:
            cmd = "(" + "cd " + subdir + " && " + "extract-bc " + File + " && " + "mv " + File + ".bc " + afl_fuzzing_sources + ")"
            subprocess.call(cmd, shell=True)



