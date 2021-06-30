import os
from conans import ConanFile, tools
try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import copy_cleaned, download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

class DebianDependencyConan(ConanFile):
    name = "libudev1"
    version = "237"
    build_version = "3ubuntu10.33" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libudev1"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libudev-dev
    description = "libudev provides APIs to introspect and enumerate devices on the local system"
    url = "https://github.com/totemic/conan-package-recipes/libudev1"    
    license = "LGPL"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only supported on Linux")

    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.ubuntu.com/bionic-updates/amd64/libudev1/download
                sha_lib = "d9d84a0a62002b17369e289912a370e23645099744a52a3bed0d4c57323de7be"
                # https://packages.ubuntu.com/bionic-updates/amd64/libudev-dev/download
                sha_dev = "99094f5144d0b9857ebc65415a2a331be8b5595f63e12a574243905fded2fd1b"
                
                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libudev1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libudev-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/bionic-updates/arm64/libudev1/download
                sha_lib = "0ce8fd96fc131cf8887ec181900d7b566385cc628ab0f7316266fe102ed8cbfe"
                # https://packages.ubuntu.com/bionic-updates/arm64/libudev-dev/download
                sha_dev = "9f134e6de6bed76cd63e3a3ec74500e82c80c516b23346ade709b0cc4b3e2129"
                
                url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/s/systemd/libudev1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/s/systemd/libudev-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            else:
                raise Exception("Todo: add binary urls for this architecture")

            download_extract_deb(self, url_lib, sha_lib)
            download_extract_deb(self, url_dev, sha_dev)
        else:
            self.output.info("Nothing to be done for this OS")

    def package(self):
        self.copy(pattern="*", dst="lib", src="lib/" + triplet_name(self), symlinks=True)
        self.copy(pattern="*", dst="lib", src="usr/lib/" + triplet_name(self), symlinks=True)
        self.copy(pattern="*", dst="include", src="usr/include", symlinks=True)
        self.copy(pattern="copyright", src="usr/share/doc/" + self.name, symlinks=True)

    def copy_cleaned(self, source, prefix_remove, dest):
        for e in source:
            if (e.startswith(prefix_remove)):
                entry = e[len(prefix_remove):]
                if len(entry) > 0 and not entry in dest:
                    dest.append(entry)

    def package_info(self):
        # pkgpath = "usr/lib/%s/pkgconfig" % triplet_name(self)
        pkgpath =  "lib/pkgconfig"
        pkgconfigpath = os.path.join(self.package_folder, pkgpath)
        if self.settings.os == "Linux":
            self.output.info("package info file: " + pkgconfigpath)
            with tools.environment_append({'PKG_CONFIG_PATH': pkgconfigpath}):
                pkg_config = tools.PkgConfig("libudev", variables={ "prefix" : self.package_folder } )

                self.output.info("lib_paths %s" % self.cpp_info.lib_paths)

                # exclude all libraries from dependencies here, they are separately included
                copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
                self.output.info("libs: %s" % self.cpp_info.libs)

                self.output.info("include_paths: %s" % self.cpp_info.include_paths)
