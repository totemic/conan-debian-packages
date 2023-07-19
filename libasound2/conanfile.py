from conan import ConanFile
from conan.tools.files import copy
from pathlib import Path

try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import copy_cleaned_no_prefix, download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

required_conan_version = ">=1.53.0"

class DebianDependencyConan(ConanFile):
    name = "libasound2"
    version = "1.1.8"
    build_version = "1" 
    homepage = "https://packages.debian.org/buster/libasound2"
    # dev_url = https://packages.debian.org/buster/libasound2-dev
    description = "shared library for ALSA applications -- development files. This package contains files required for developing software that makes use of libasound2, the ALSA library."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libasound2"
    license = "GNU Lesser General Public License"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    def build(self):
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.debian.org/buster/amd64/libasound2/download
                sha_lib = "6cc281b4a6d1faffe4fc6d83ec71365c1af0ee6d7806fa122fef00f85a0dde62"
                # https://packages.debian.org/buster/amd64/libasound2-dev/download
                sha_dev = "efcae0522800ac0f32a72d7ac240375effde06473bb5aeabbe20d2d4057c185e"

                url_lib = ("http://ftp.debian.org/debian/pool/main/a/alsa-lib/libasound2_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://ftp.debian.org/debian/pool/main/a/alsa-lib/libasound2-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.debian.org/buster/arm64/libasound2/download
                sha_lib = "af663d07d10b085f590c539772dbf70b279df187210ea818446dfd896487adee"
                # https://packages.debian.org/buster/arm64/libasound2-dev/download
                sha_dev = "617ed035bd7caaab64c7f68e5b673bd60160eb536b9e7ca3c748cc9c46949ffe"

                url_lib = ("http://ftp.debian.org/debian/pool/main/a/alsa-lib/libasound2_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://ftp.debian.org/debian/pool/main/a/alsa-lib/libasound2-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            else:
                raise Exception("Todo: add binary urls for this architecture")
        else:
            raise Exception("Binary does not exist for these settings")
        download_extract_deb(self, url_lib, sha_lib)
        download_extract_deb(self, url_dev, sha_dev)

    def package(self):
        copy(self, "*", src=Path(self.build_folder)/"usr"/"lib"/triplet_name(self), dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)

    def package_info(self):
        # pkgconfigpath = str(Path(self.package_folder)/"lib"/"pkgconfig")
        # self.output.info("package info file: " + pkgconfigpath)
        # pkg_config = PkgConfig(self, "alsa", pkgconfigpath)
        # # read the prefix so we can remove it later
        # prefix = pkg_config.variables['prefix']
        # copy_cleaned_no_prefix(pkg_config.libdirs, prefix, self.cpp_info.libdirs)
        # copy_cleaned_no_prefix(pkg_config.libs, prefix, self.cpp_info.libs)
        # copy_cleaned_no_prefix(pkg_config.includedirs, prefix, self.cpp_info.includedirs)

        #pkg_config = tools.PkgConfig("alsa", variables={ "prefix" : self.package_folder } )
        #self.output.info(pkg_config.variables)
        #self.output.info(f"pkg_config.libs_only_L: {pkg_config.libdirs} - {pkg_config._get_option('libs-only-L').split()}")
        #self.output.info(f"pkg_config.libs_only_l: {pkg_config.libs} - {pkg_config._get_option('libs-only-l').split()}")
        #self.output.info(f"pkg_config.cflags_only_I: {pkg_config.includedirs} - {pkg_config._get_option('cflags-only-I').split()}")

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["asound"]
        self.cpp_info.includedirs = ["include", "include/alsa"]

        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")

