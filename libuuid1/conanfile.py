import os
from conans import ConanFile, tools
try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import copy_cleaned, download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

class DebianDependencyConan(ConanFile):
    name = "libuuid1"
    version = "2.27.1"
    build_version = "6ubuntu3.7" 
    homepage = "https://packages.ubuntu.com/xenial-updates/libuuid1"
    # dev_url = https://packages.ubuntu.com/xenial-updates/uuid-dev
    description = "The libuuid library generates and parses 128-bit Universally Unique IDs (UUIDs). A UUID is an identifier that is unique within the space of all such identifiers across both space and time. It can be used for multiple purposes, from tagging objects with an extremely short lifetime to reliably identifying very persistent objects across a network."
    url = "https://github.com/totemic/conan-package-recipes/libuuid1"    
    license = "BSD-3-clause"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.ubuntu.com/xenial-updates/amd64/libuuid1/download
                sha_lib = "0069b9fe2ac138b980db186d88369e40d68570ab31925c19f9beabe1eb3af79e"
                # https://packages.ubuntu.com/xenial-updates/amd64/uuid-dev/download
                sha_dev = "a9d5d94c8181fcafa7464fb3298a36ece0ff64f1df7d599fe7258fa91dc23d62"
                
                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/xenial-updates/arm64/libuuid1/download
                sha_lib = "1d886309c5b24257e5cc6ba0aa27085b01fc4702049b780e01fef2dce52b0c70"
                # https://packages.ubuntu.com/xenial-updates/arm64/uuid-dev/download
                sha_dev = "8086d900b015b4be3a78c43c4a8a41954998a8d978e42c4d82b513468d8dc6a4"
                
                url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            else:
                raise Exception("Todo: add binary urls for this architecture")

            download_extract_deb(self, url_lib, sha_lib)
            download_extract_deb(self, url_dev, sha_dev)
            # remove libuuid.so which is an absolute link to /lib/arm-linux-gnueabihf/libuuid.so.1.3.0
            libuuid_so_path = "usr/lib/%s/libuuid.so" % triplet_name(self)
            os.remove(libuuid_so_path)
            os.symlink("libuuid.so.1.3.0", libuuid_so_path)
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
                pkg_config = tools.PkgConfig("uuid", variables={ "prefix" : self.package_folder } )

                #copy_cleaned(pkg_config.libs_only_L, "-L", self.cpp_info.lib_paths)
                self.output.info("lib_paths %s" % self.cpp_info.lib_paths)

                # exclude all libraries from dependencies here, they are separately included
                copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
                self.output.info("libs: %s" % self.cpp_info.libs)

                #copy_cleaned(pkg_config.cflags_only_I, "-I", self.cpp_info.include_paths)
                self.output.info("include_paths: %s" % self.cpp_info.include_paths)
