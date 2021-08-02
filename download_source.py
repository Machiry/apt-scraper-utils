#####################################################################
#
# This script will download all the C/C++ package sources to a local 
# folder
#
######################################################################
from pkg_manager import PackageManager
from ctypes.util import find_library

source_file_to_read_packages_from = "/home/vidush/Applications/src/data"
mirror_url = "http://mirror.math.ucdavis.edu/ubuntu/"
local_download_folder_for_sources = "/home/vidush/debian_sources"

p = PackageManager(source_file_to_read_packages_from, mirror_url)
p.build_pkg_entries()

p.dump_to_pickled_json("dummp.picked.json")
p2 = PackageManager.from_picked_json("dummp.picked.json")


packages_available = p.all_pkg_entries

for pkgs in packages_available:
    
    reverse_dependencies = []
    dependency_list = p.dependency_map[pkgs]
    for dependencies in dependency_list:
        reverse_dependencies.extend(p.reverse_dependency_map[dependencies])
    
    for lib in reverse_dependencies:
        if (find_library(lib) != None):
            print()
            print("...")
            print("DOWNLOADING "+ str(pkgs) + "from the mirror...")
            print("...")
            p.download_package_source(pkgs, local_download_folder_for_sources)
            break
