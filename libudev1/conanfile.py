from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy
from pathlib import Path

try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

class DebianDependencyConan(ConanFile):
    name = "libudev1"
    version = "237"
    build_version = "3ubuntu10.57" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libudev1"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libudev-dev
    description = "libudev provides APIs to introspect and enumerate devices on the local system"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libudev1"    
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
                sha_lib = "04cb377b1ecaa3f4a8e1d2612c428ccf6d87b9f9cda267ac78d34d99388675df"
                # https://packages.ubuntu.com/bionic-updates/amd64/libudev-dev/download
                sha_dev = "bc4c38aea09a6930a081c1b7d100f573bf60fa5ca4e5671320327a926c5e2464"
                
                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libudev1_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libudev-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/bionic-updates/arm64/libudev1/download
                sha_lib = "ee9800e091c1c53e67f97f1719938554169f18a64d3c37f116426c4d814cdad4"
                # https://packages.ubuntu.com/bionic-updates/arm64/libudev-dev/download
                sha_dev = "d6bf9a582454e082b733a4d0a42fe1e8951ae959f4561452524c40b45852c50b"
                
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
        copy(self, "*", src=Path(self.build_folder)/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)

    def package_info(self):
        if self.settings.os == "Linux":
            #self.cpp_info.libdirs = ["lib"]
            self.cpp_info.libs = ["udev"]
            #self.cpp_info.includedirs = ["include"]
            self.output.info(f"libdirs {self.cpp_info.libdirs}")
            self.output.info(f"libs: {self.cpp_info.libs}")
            self.output.info(f"includedirs: {self.cpp_info.includedirs}")
