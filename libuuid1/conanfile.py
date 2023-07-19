from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy
import os
from pathlib import Path

try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

required_conan_version = ">=1.53.0"

class DebianDependencyConan(ConanFile):
    name = "libuuid1"
    version = "2.27.1"
    build_version = "6ubuntu3.10" 
    homepage = "https://packages.ubuntu.com/xenial-updates/libuuid1"
    # dev_url = https://packages.ubuntu.com/xenial-updates/uuid-dev
    description = "The libuuid library generates and parses 128-bit Universally Unique IDs (UUIDs). A UUID is an identifier that is unique within the space of all such identifiers across both space and time. It can be used for multiple purposes, from tagging objects with an extremely short lifetime to reliably identifying very persistent objects across a network."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libuuid1"
    license = "BSD-3-clause"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.ubuntu.com/xenial-updates/amd64/libuuid1/download
                sha_lib = "2448657baae15d88d964022bd3827e9274129928ae8a9f04556866b26cf8a4dd"
                # https://packages.ubuntu.com/xenial-updates/amd64/uuid-dev/download
                sha_dev = "0ce9ae9941443446446c7f0338ea7edf9a512f893b584d196d6ccbe54c722a58"
                
                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/libuuid1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/u/util-linux/uuid-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/xenial-updates/arm64/libuuid1/download
                sha_lib = "69e162382bf4f33f34b8a3ab06633eb4013276d145d13f433805ef8659769b35"
                # https://packages.ubuntu.com/xenial-updates/arm64/uuid-dev/download
                sha_dev = "bf72ad7a6dfd846513500f978a0bd605a87fd61b19a7c8a5c02df6318a169ad7"
                
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
        copy(self, "*", src=Path(self.build_folder)/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)


    def package_info(self):
        if self.settings.os == "Linux":
            #self.cpp_info.libdirs = ["lib"]
            self.cpp_info.libs = ["uuid"]
            #self.cpp_info.includedirs = ["include"]
            self.output.info(f"libdirs {self.cpp_info.libdirs}")
            self.output.info(f"libs: {self.cpp_info.libs}")
            self.output.info(f"includedirs: {self.cpp_info.includedirs}")
