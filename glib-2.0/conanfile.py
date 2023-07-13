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
    name = "glib-2.0"
    version = "2.56.4"
    build_version = "0ubuntu0.18.04.9" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libglib2.0-0"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libglib2.0-dev
    description = "Systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/glib-2.0"    
    license = "LGPL"
    settings = "os", "arch"
    exports = ["../debiantools.py"]

    # def requirements(self):
    #     if self.settings.os == "Linux":
    #         # todo: we should also add depdencies to libselinux.so.1, liblzma.so.5, libgcrypt.so.20
    #         # right now this is handled by telling the linker to ignore unknown symbols in secondary dependencies
    #         self.requires("libudev1/237@totemic/stable")

    def build(self):
        # For anything non-linux, we will fetch the header files, using the x86 package
        if self.settings.arch == "x86_64":
            # https://packages.ubuntu.com/bionic-updates/amd64/libglib2.0-0/download
            sha_lib = "0f629a40a5ea5e73195365c9a00adb5f7bd8761681bfa6c94adf6f20d1485b4e"
            # https://packages.ubuntu.com/bionic-updates/amd64/libglib2.0-dev/download
            sha_dev = "ad316346dd0792b65146159a32424d3041113e26e05304d44baa25a0f225593b"

            url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
            url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
        elif self.settings.arch == "armv8":
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-0/download
            sha_lib = "634d9bd5a1210693f99eafe3c3a10b67576bdd6323e783a8e5c61fe942bda8ea"
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-dev/download
            sha_dev = "f814bcceb63568c0cd9e7cf6db69eb7eb09a8ea666aea43b11bbaaf6e18b42ee"

            url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
            url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
        else:
            raise Exception("Todo: add binary urls for this architecture")

        download_extract_deb(self, url_lib, sha_lib)
        download_extract_deb(self, url_dev, sha_dev)

    def package(self):
        pattern = "*" if self.settings.os == "Linux" else "*.h"
        triplet = triplet_name(self, self.settings.os != "Linux")
        copy(self, pattern, src=Path(self.build_folder)/"lib"/triplet, dst=Path(self.package_folder)/"lib")
        copy(self, pattern, src=Path(self.build_folder)/"usr"/"lib"/triplet, dst=Path(self.package_folder)/"lib")
        copy(self, "*", src=Path(self.build_folder)/"usr"/"include", dst=Path(self.package_folder)/"include")
        copy(self, "copyright", src=Path(self.build_folder)/"usr"/"share"/"doc"/self.name, dst=self.package_folder)

    def package_info(self):
        #self.cpp_info.libdirs = ["lib"]

        # we only add the libs on Linux, on other platforms just the include files
        if self.settings.os == "Linux":
            # only export from pkginfo "gio-unix-2.0" for now, not gio-2.0, glib-2.0, gmodule-2.0, gmodule-export-2.0, gmodule-no-export-2.0, gobject-2.0, gthread-2.0
            self.cpp_info.libs = ['gio-2.0', 'gobject-2.0', 'glib-2.0']

        # add additional path to sub directories since some libraries use them this way
        # add extra include path for glibconfig.h
        self.cpp_info.includedirs = ["include", str(Path("include")/"glib-2.0"), str(Path("include")/"gio-unix-2.0"), str(Path("lib")/"glib-2.0"/"include")]

        # https://github.com/conan-io/conan-center-index/blob/master/recipes/glib/all/conanfile.py
        # set these variables, so that the libostree recipe can call the native programs during run of "configuration" script
        # (we assume that glib is installed on the native build system to avoid downloading more dependencies here)
        pkgconfig_variables = {
            'glib_genmarshal': 'glib-genmarshal',
            'gobject_query': 'gobject-query',
            'glib_mkenums': 'glib-mkenums'
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key, value in pkgconfig_variables.items()))

        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")
