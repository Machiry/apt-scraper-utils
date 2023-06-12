# Apt-scraper-utils API
A humble python API to query, manage and download debian packages.

> Requires python >= 3.5

## Needed information
* Source File (`src`): This is a file maintained by apt mirror sites that acts as a catalogue for all the packages in the apt repository.
    > Example: http://mirror.math.ucdavis.edu/ubuntu/dists/bionic/main/source/Sources.gz download and extract the file.
* Mirror url (`mirr_base_url`): The base URL for the mirror site.
    > Example: http://mirror.math.ucdavis.edu/ubuntu/

## Using the API
### Install requirements
```
$ sudo pip3.5 install -r requirements.txt
```
### Using the API
#### Initializing
```
cd <repo_dir>
python main.py
# This will open an ipython shell to explore.
# Initializing package manager.
# Here the first argument is path to Source File and Second argument is the mirror url.
In [1]: p = PackageManager("/home/machiry/Downloads/Sources", "http://mirror.math.ucdavis.edu/ubuntu/")
# Next build pkg entries
In [2]: p.build_pkg_entries()
```
### Using
The `PackageManager` has docstrings that your can use to understand the methods provides. Example in `Ipython`:
```
Type p. and tab
In [8]: p.
p.all_pkg_entries               p.build_pkg_entries             p.download_all_packages_source  p.download_packages_source      p.from_picked_json              p.reverse_dependency_map        
p.base_url                      p.dependency_map                p.download_package_source       p.dump_to_pickled_json          p.rebuild_pkg_entries           p.source_file_path    
```
#### Knowing about a function
```
In [8]: p.download_all_packages_source?
Type:        method
String form: <bound method PackageManager.download_all_packages_source of <pkg_manager.package_manager.PackageManager object at 0x7f119c7a9978>>
File:        /home/machiry/projects/apt-scraper-utils/pkg_manager/package_manager.py
Definition:  p.download_all_packages_source(self, output_folder) -> None
Docstring:
Download sources of all the packages in to the provided folder.
:param output_folder: Path to the local folder where the files should be downloaded.
:return:

In [5]: p.get_pkgs_with_dependency?
Type:        method
String form: <bound method PackageManager.get_pkgs_with_dependency of <pkg_manager.package_manager.PackageManager object at 0x7f0d4de3ff60>>
File:        /home/machiry/projects/apt-scraper-utils/pkg_manager/package_manager.py
Definition:  p.get_pkgs_with_dependency(self, dep_name)
Docstring:
Get all packages that contain the provided dependency.
:param dep_name: Dependency name
:return: list of package names that contain the provided dependency.

In [6]: p.get_pkgs_without_dependency?
Type:        method
String form: <bound method PackageManager.get_pkgs_without_dependency of <pkg_manager.package_manager.PackageManager object at 0x7f0d4de3ff60>>
File:        /home/machiry/projects/apt-scraper-utils/pkg_manager/package_manager.py
Definition:  p.get_pkgs_without_dependency(self, dep_name)
Docstring:
Get all packages that DO NOT contain the provided dependency.
:param dep_name: Dependency name
:return: list of package names that DO NOT contain the provided dependency.

```

You can refer the docstring of any of the function to understand its uses.
### Accessing package
```
# Number of packges
In [3]: len(p.all_pkg_entries)
Out[3]: 2323
# Here p.all_pkg_entries is a map from package name to pkg_entry object
# Getting a package name
In [5]: list(p.all_pkg_entries.keys())[0]
Out[5]: 'libnatpmp'
```
### Knowing package dependencies
```
In [6]: p.dependency_map['libnatpmp']
Out[6]: ['python3-dev', 'python3-setuptools', 'dh-python', 'debhelper']
```
### Knowing reverse dependencies
```
p.reverse_dependency_map['python3-dev']
Out[7]: 
['hplip',
 'lirc',
 'tdb',
 'vim',
 'liborcus',
 'gpgme1.0',
 'sssd',
 'libreoffice',
 'landscape-client',
 'gobject-introspection',
 'libpeas',
 'libreoffice-l10n',
 'libnatpmp',
 'rhythmbox',
 'gdb',
 'apturl',
 'python-cryptography',
 'libixion',
 'lvm2',
 'postgresql-10']
```
#### Downloading a package
```
# Downloading a package sources to a folder
In [7]: p.download_package_source('libnatpmp', "/tmp/libdownload")
2020-09-02 22:32:24,845-INFO-Trying to download files for package libnatpmp
2020-09-02 22:32:24,846-INFO-Downloading 3 files to /tmp/libdownload using wget
--2020-09-02 22:32:24--  http://mirror.math.ucdavis.edu/ubuntu//pool/main/libn/libnatpmp/libnatpmp_20150609.orig.tar.gz
Resolving mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)... 169.237.99.105
Connecting to mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)|169.237.99.105|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 24392 (24K) [application/x-gzip]
Saving to: ‘libnatpmp_20150609.orig.tar.gz’

libnatpmp_20150609.orig.tar.gz                            100%[====================================================================================================================================>]  23.82K  --.-KB/s    in 0.08s   

2020-09-02 22:32:25 (315 KB/s) - ‘libnatpmp_20150609.orig.tar.gz’ saved [24392/24392]

--2020-09-02 22:32:25--  http://mirror.math.ucdavis.edu/ubuntu//pool/main/libn/libnatpmp/libnatpmp_20150609-2.dsc
Resolving mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)... 169.237.99.105
Connecting to mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)|169.237.99.105|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 2168 (2.1K)
Saving to: ‘libnatpmp_20150609-2.dsc’

libnatpmp_20150609-2.dsc                                  100%[====================================================================================================================================>]   2.12K  --.-KB/s    in 0s      

2020-09-02 22:32:25 (92.8 MB/s) - ‘libnatpmp_20150609-2.dsc’ saved [2168/2168]

--2020-09-02 22:32:25--  http://mirror.math.ucdavis.edu/ubuntu//pool/main/libn/libnatpmp/libnatpmp_20150609-2.debian.tar.xz
Resolving mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)... 169.237.99.105
Connecting to mirror.math.ucdavis.edu (mirror.math.ucdavis.edu)|169.237.99.105|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4564 (4.5K) [application/x-xz]
Saving to: ‘libnatpmp_20150609-2.debian.tar.xz’

libnatpmp_20150609-2.debian.tar.xz                        100%[====================================================================================================================================>]   4.46K  --.-KB/s    in 0s      

2020-09-02 22:32:25 (144 MB/s) - ‘libnatpmp_20150609-2.debian.tar.xz’ saved [4564/4564]

2020-09-02 22:32:25,539-INFO-Finished downloading files for package libnatpmp
```
    
