
class PkgEntry:
    def __init__(self, p_name):
        self.pkg_name = p_name
        self.pkg_url = ""
        self.dependencies = set()
        self.source_urls = set()
        self.build_binaries = set()

    def add_dependencies(self, deps):
        if isinstance(deps, list) or isinstance(deps, set):
            self.dependencies.update(set(deps))
        else:
            self.dependencies.add(deps)

    def add_source_abs_urls(self, src_urls):
        if isinstance(src_urls, list) or isinstance(src_urls, set):
            self.source_urls.update(set(src_urls))
        else:
            self.source_urls.add(src_urls)

    def add_build_binaries(self, build_bins):
        if isinstance(build_bins, list) or isinstance(build_bins, set):
            self.build_binaries.update(set(build_bins))
        else:
            self.build_binaries.add(build_bins)

    def set_pkg_url(self, purl):
        self.pkg_url = purl
