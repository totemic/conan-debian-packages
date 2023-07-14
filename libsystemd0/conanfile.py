from conan import ConanFile
from conan.tools.files import copy
from pathlib import Path

try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

required_conan_version = ">=1.53.0"

class DebianDependencyConan(ConanFile):
    name = "libsystemd0"
    version = "237"
    build_version = "3ubuntu10.57" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libsystemd0"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libsystemd-dev
    description = "Systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libsystemd0"
    license = "LGPL"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    def requirements(self):
        if self.settings.os == "Linux":
            # todo: we should also add depdencies to libselinux.so.1, liblzma.so.5, libgcrypt.so.20
            # right now this is handled by telling the linker to ignore unknown symbols in secondary dependencies
            self.requires("libudev1/237@totemic/stable")

    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.ubuntu.com/bionic-updates/amd64/libsystemd0/download
                sha_lib = "637d89dd31920db1baf2c4b9a34d7bb3d9829ff01e5d7ad75d302791120a2f45"
                # https://packages.ubuntu.com/bionic-updates/amd64/libsystemd-dev/download
                sha_dev = "0d6e7785b8aa2e2ab71b67bcdb664da9e963e36027640c9c414984dac2a2e9b7"

                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libsystemd0_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libsystemd-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/bionic-updates/arm64/libsystemd0/download
                sha_lib = "8d353aca9674e09a0b493a6daed5404331bb391fb4ae0bafb18434168524e50b"
                # https://packages.ubuntu.com/bionic-updates/arm64/libsystemd-dev/download
                sha_dev = "dabd0e0dbcd867d85a6ef9968d5e98f55b91a213724a94a58631fb716472a2a3"

                url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/s/systemd/libsystemd0_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/s/systemd/libsystemd-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            else:
                raise Exception("Todo: add binary urls for this architecture")

            download_extract_deb(self, url_lib, sha_lib)
            download_extract_deb(self, url_dev, sha_dev)
            # remove libsystemd.so which is an absolute link to /lib/aarch64-linux-gnu/libsystemd.so.0.14.0
            # libsystemd_so_path = "lib/%s/libsystemd.so" % triplet_name(self)
            # os.remove(libsystemd_so_path)
            # os.symlink("libsystemd.so.0.21.0", libsystemd_so_path)
        else:
            # We allow using systemd on all platforms, but for anything except Linux nothing is produced
            # this allows unconditionally including this conan package on all platforms
            self.output.info("Nothing to be done for this OS")

    def package(self):
        copy(self, "*", src=Path(self.build_folder)/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)

    def package_info(self):
        if self.settings.os == "Linux":
            #self.cpp_info.libdirs = ["lib"]
            self.cpp_info.libs = ["systemd"]
            #self.cpp_info.includedirs = ["include"]
            self.output.info(f"libdirs {self.cpp_info.libdirs}")
            self.output.info(f"libs: {self.cpp_info.libs}")
            self.output.info(f"includedirs: {self.cpp_info.includedirs}")
