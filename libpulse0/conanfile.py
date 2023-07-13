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


class DebianDependencyConan(ConanFile):
    name = "libpulse0"
    version = "12.2"
    build_version = "4+deb10u1" 
    homepage = "https://packages.debian.org/buster/libpulse0"
    # dev_url = https://packages.debian.org/buster/libpulse-dev
    description = "PulseAudio client development headers and libraries"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libpulse0"    
    license = "GNU Lesser General Public License"
    settings = "os", "arch"
    exports = ["../debiantools.py"]
    
    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.debian.org/buster/amd64/libpulse0/download
                sha_lib = "a7edaf4424894b0e83c81d37c26ad351daa76d74f0e01e750c6679ae74c59362"
                # https://packages.debian.org/buster/amd64/libpulse-dev/download
                sha_dev = "6aa5973e00ac561ee1219983d78c40fa6341fe7e4ce25acc0b047e297f9a8095"
            elif self.settings.arch == "armv8":
                # https://packages.debian.org/buster/arm64/libpulse0/download
                sha_lib = "543c2329b85893045e10b7a3f59801851c92267f1f17a2cbb27473066b8eecb3"
                # https://packages.debian.org/buster/arm64/libpulse-dev/download
                sha_dev = "ada3da8f3245ce82fda28f2ef494029213c8a4acb16bf66bb9c6664138749182"
            else:
                raise Exception("Todo: add binary urls for this architecture")

            url_lib = ("http://ftp.debian.org/debian/pool/main/p/pulseaudio/libpulse0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
            url_dev = ("http://ftp.debian.org/debian/pool/main/p/pulseaudio/libpulse-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
        else:
            raise Exception("Binary does not exist for these settings")
        download_extract_deb(self, url_lib, sha_lib)
        download_extract_deb(self, url_dev, sha_dev)
        
        # we are currently not supporting the use of https://packages.debian.org/buster/libpulse-mainloop-glib0
        # remove the symlink here. If needed, it can be imported with the same steps as above
        mainloop_glib_so_path = "usr/lib/%s/libpulse-mainloop-glib.so" % triplet_name(self)
        os.remove(mainloop_glib_so_path)

    def package(self):
        copy(self, "*", src=Path(self.build_folder)/"usr"/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)

    def package_info(self):
        if self.settings.os == "Linux":
            # need to add a library path from field Libs.private of pkg-config
            self.cpp_info.libdirs = ["lib", "lib/pulseaudio"]
            # need to also add the pulsecommon library from field Libs.private of pkg-config
            self.cpp_info.libs = ['pulse-simple', 'pulse', f'pulsecommon-{self.version}']
            #self.cpp_info.includedirs = ["include"]
            self.output.info(f"libdirs {self.cpp_info.libdirs}")
            self.output.info(f"libs: {self.cpp_info.libs}")
            self.output.info(f"includedirs: {self.cpp_info.includedirs}")
