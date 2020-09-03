from .pkg_entry import PkgEntry
import logging

PKG_NAME_PREFIX = "Package:"
BIN_NAME_PREFIX = "Binary:"
BUILD_DEPENDENCIES_PREFIX = "Build-Depends:"
BUILD_DEPENDENCIES_IND_PREFIX = "Build-Depends-Indep:"
DIRECTORY_PREFIX = "Directory:"
FILE_ENTRY_PREFIX = "Files:"

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.DEBUG)


def parse_single_entry(all_lines, base_url) -> (PkgEntry, int):
    to_ret_obj = None
    to_ret_line_no = 0
    while to_ret_line_no < len(all_lines):
        curr_line = all_lines[to_ret_line_no]
        curr_line = curr_line.strip()
        if curr_line:
            # Package:
            if curr_line.startswith(PKG_NAME_PREFIX):
                to_ret_obj = PkgEntry(curr_line.split(PKG_NAME_PREFIX)[1].strip())

            # Binary:
            if curr_line.startswith(BIN_NAME_PREFIX):
                if to_ret_obj is not None:
                    all_bins = curr_line.split(BIN_NAME_PREFIX)[1].strip().split(",")
                    all_bins = list(map(lambda x: x.strip(), all_bins))
                    to_ret_obj.add_build_binaries(all_bins)

            # Build-Depends:
            if curr_line.startswith(BUILD_DEPENDENCIES_IND_PREFIX):
                if to_ret_obj is not None:
                    all_deps = curr_line.split(BUILD_DEPENDENCIES_IND_PREFIX)[1].strip().split(",")
                    all_deps = list(map(lambda x: x.strip().split()[0], all_deps))
                    to_ret_obj.add_dependencies(all_deps)

            # Build-Depends-Indep:
            if curr_line.startswith(BUILD_DEPENDENCIES_PREFIX):
                if to_ret_obj is not None:
                    all_deps = curr_line.split(BUILD_DEPENDENCIES_PREFIX)[1].strip().split(",")
                    all_deps = list(map(lambda x: x.strip().split()[0], all_deps))
                    to_ret_obj.add_dependencies(all_deps)

            # Directory:
            if curr_line.startswith(DIRECTORY_PREFIX):
                if to_ret_obj is not None:
                    pkg_url = curr_line.split(DIRECTORY_PREFIX)[1].strip()
                    abs_url = base_url + "/" + pkg_url
                    to_ret_obj.set_pkg_url(abs_url)

            # Files:
            if curr_line.startswith(FILE_ENTRY_PREFIX):
                if to_ret_obj is not None:
                    src_pkgs = []
                    tmp_line_num = to_ret_line_no + 1
                    tmp_line = all_lines[tmp_line_num]
                    while tmp_line.startswith(" "):
                        tmp_line = tmp_line.strip()
                        src_pkgs.append(tmp_line.split()[-1])
                        tmp_line_num += 1
                        tmp_line = all_lines[tmp_line_num]
                    abs_src_urls = list(map(lambda x: to_ret_obj.pkg_url + "/" + x, src_pkgs))
                    to_ret_obj.add_source_abs_urls(abs_src_urls)
                    to_ret_line_no = tmp_line_num - 1
            to_ret_line_no += 1
        else:
            break

    if to_ret_obj is not None:
        logging.info("Got Entry for %s", to_ret_obj.pkg_name)
    else:
        logging.error("Unable to parse entry.")
    return to_ret_obj, to_ret_line_no


def parse_all_entries(all_lines, base_url) -> list:
    all_entries = []
    curr_line_num = 0
    logging.info("Parsing %d source lines.", len(all_lines))
    while True:
        curr_obj, new_line_num = parse_single_entry(all_lines[curr_line_num:], base_url)
        if new_line_num > 0:
            curr_line_num += new_line_num + 1
            if curr_obj is not None:
                all_entries.append(curr_obj)
        else:
            break
    logging.info("Finished parsing source lines. Got %d entries.", len(all_lines))
    return all_entries
