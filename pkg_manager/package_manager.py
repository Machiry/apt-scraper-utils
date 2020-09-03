import os
import logging
import sys
import jsonpickle
import json
from .source_file_parser import parse_all_entries

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.DEBUG)


class PackageManager:
    '''
    The main class that manages all the packages.
    This class has following members of interest.

        source_file_path (str): Path to the source file

        base_url (str): Base URL of the mirror repository.

        all_pkg_entries (map) : Map of package name and PkgEntry object.

        dependency_map (map: str -> list): Map of package name and all the build dependencies of the package.

        reverse_dependency_map (map: str -> list): Reverse dependency map i.e., map of a dependency and all the package
                                that depend on the dependency.
    '''
    def __init__(self, source_file, base_url):
        '''
        Create package manager object.
        :param source_file: Path to the source file.
        :param base_url: Base mirror url.
        '''
        self.source_file_path = source_file
        self.base_url = base_url
        self.all_pkg_entries = {}
        self.dependency_map = {}
        self.reverse_dependency_map = {}

    @staticmethod
    def from_picked_json(pickled_json):
        '''
        Create PackageManager object from the saved json file.
        Note that this should be saved before using dump_to_pickled_json method.
        :param pickled_json: Local path to the picked json file.
        :return: None
        '''
        if not os.path.exists(pickled_json):
            logging.error("Provided pickled json file %s does not exist. Exiting!", pickled_json)
            sys.exit(-1)
        fp = open(pickled_json, "r")
        all_conts = fp.read()
        fp.close()
        return jsonpickle.decode(all_conts)

    def _build_dependency_map(self) -> None:
        self.dependency_map.clear()
        self.reverse_dependency_map.clear()
        logging.info("Building dependency map.")
        for curr_pkg_name in self.all_pkg_entries.keys():
            curr_entry = self.all_pkg_entries[curr_pkg_name]
            self.dependency_map[curr_pkg_name] = list(set(curr_entry.dependencies))
            for curr_dep in curr_entry.dependencies:
                if curr_dep not in self.reverse_dependency_map:
                    self.reverse_dependency_map[curr_dep] = list()
                self.reverse_dependency_map[curr_dep].append(curr_pkg_name)
        logging.info("Finished building dependency map.")

    def build_pkg_entries(self) -> None:
        '''
        Build an index of all the package entries from the provided source file.
        :return: None
        '''
        logging.info("Trying to build package entries from %s", self.source_file_path)
        if os.path.exists(self.source_file_path):
            fp = open(self.source_file_path, "r")
            all_lines = fp.readlines()
            fp.close()
            logging.debug("Parsing pkg entries from source file:" + self.source_file_path)
            all_entries = parse_all_entries(all_lines, self.base_url)
            for ce in all_entries:
                self.all_pkg_entries[ce.pkg_name] = ce
            self._build_dependency_map()
            logging.debug("Got %d package entries.", len(all_lines))
        else:
            logging.error("Unable to open the provided file %s", self.source_file_path)

    def get_pkgs_with_dependency(self, dep_name):
        '''
        Get all packages that contain the provided dependency.
        :param dep_name: Dependency name
        :return: list of package names that contain the provided dependency.
        '''
        dep_name = dep_name.lower()
        all_rev_deps = set(self.reverse_dependency_map.keys())
        all_rel_deps = list(filter(lambda x: dep_name in x.lower(), all_rev_deps))
        all_interesting_pkgs = set()
        for curr_d in all_rel_deps:
            all_interesting_pkgs.update(set(self.reverse_dependency_map[curr_d]))
        all_interesting_pkgs = list(filter(lambda x: dep_name in x.lower(), all_interesting_pkgs))
        return list(all_interesting_pkgs)

    def get_pkgs_without_dependency(self, dep_name):
        '''
        Get all packages that DO NOT contain the provided dependency.
        :param dep_name: Dependency name
        :return: list of package names that DO NOT contain the provided dependency.
        '''
        dep_name = dep_name.lower()
        all_rev_deps = set(self.reverse_dependency_map.keys())
        all_rel_deps = list(filter(lambda x: dep_name not in x.lower(), all_rev_deps))
        all_interesting_pkgs = set()
        for curr_d in all_rel_deps:
            all_interesting_pkgs.update(set(self.reverse_dependency_map[curr_d]))
        all_interesting_pkgs = list(filter(lambda x: dep_name not in x.lower(), all_interesting_pkgs))
        return list(all_interesting_pkgs)

    def rebuild_pkg_entries(self) -> None:
        '''
        Rebuild package entries.
        :return: None
        '''
        # clear out everything
        self.all_pkg_entries.clear()
        self.dependency_map.clear()
        self.reverse_dependency_map.clear()
        logging.info("Removed all the existing entries. Rebuilding Package List.")
        # build pkg entries
        self.build_pkg_entries()

    def dump_to_pickled_json(self, path_to_json):
        '''
        Dump this package manager object to a json file that can be loaded later.
        :param path_to_json: Local file path where the json should be stored.
        :return: None
        '''
        json_str = jsonpickle.encode(self)
        json_obj = json.loads(json_str)
        fp = open(path_to_json, "w")
        json.dump(json_obj, fp, indent=4)
        fp.close()

    def download_package_source(self, pkg_name, output_folder) -> None:
        '''
        Download all the files that are part of the sources of the provided package
         into a local folder.
        :param pkg_name: Package name whose contents needs to be downloaded.
        :param output_folder: Local file path where the files should be stored.
        :return: None
        '''
        if pkg_name not in self.all_pkg_entries:
            logging.error("Unrecognized package %s", pkg_name)
        else:
            logging.info("Trying to download files for package %s", pkg_name)
            pkg_en = self.all_pkg_entries[pkg_name]
            curr_dir = os.getcwd()
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            logging.info("Downloading %d files to %s using wget", len(pkg_en.source_urls), output_folder)
            os.chdir(output_folder)
            for curr_f in pkg_en.source_urls:
                os.system("wget " + curr_f)
            os.chdir(curr_dir)
            logging.info("Finished downloading files for package %s", pkg_name)

    def download_packages_source(self, pkgs, output_folder) -> None:
        '''
        Download all the files of all the packages in the given list of packages
        into a local folder.
        :param pkgs: List of packages that need to be downloaded.
        :param output_folder: Path to the local folder where the files of the provided package need to be stored.
        :return: None
        '''
        logging.info("Downloading %d packages to %s", len(pkgs), output_folder)
        for curr_pkg in pkgs:
            pkg_folder = os.path.join(output_folder, curr_pkg)
            self.download_package_source(curr_pkg, pkg_folder)
        logging.info("Finished downloading %d packages to %s", len(pkgs), output_folder)

    def download_all_packages_source(self, output_folder) -> None:
        '''
        Download sources of all the packages in to the provided folder.
        :param output_folder: Path to the local folder where the files should be downloaded.
        :return: None
        '''
        self.download_packages_source(self.all_pkg_entries.keys(), output_folder)
