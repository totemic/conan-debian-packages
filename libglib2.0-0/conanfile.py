import os
from conans import ConanFile, tools
try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import copy_cleaned, download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

class DebianDependencyConan(ConanFile):
    name = "libglib2.0-0"
    version = "2.56.4"
    build_version = "0ubuntu0.18.04.6" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libglib2.0-0"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libglib2.0-dev
    description = "Systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    url = "https://github.com/totemic/conan-package-recipes/libglib2.0-0"    
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
            sha_lib = "d83313ca3bd99eec1934f2da1c7cddabe9acf42fa0914eb7af778139db216da6"
            # https://packages.ubuntu.com/bionic-updates/amd64/libglib2.0-dev/download
            sha_dev = "dae746eebff565fd183a29b8c1b9d26179f07d897541b0ae1ee8dbe9beca8589"

            url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
            url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, translate_arch(self)))
        elif self.settings.arch == "armv8":
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-0/download
            sha_lib = "c16be203f547a977326e13cd6f3935022679f9fcdaa918bdcd315e820b33e5d0"
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-dev/download
            sha_dev = "c1e66bf2e5e5d8f658c0e4362c965741d950425608aecd51518f26ffe040f6da"

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
        triplet_name = triplet_name(self, self.settings.os != "Linux")
        self.copy(pattern=pattern, dst="lib", src="lib/" + triplet_name, symlinks=True)
        self.copy(pattern=pattern, dst="lib", src="usr/lib/" + triplet_name, symlinks=True)
        self.copy(pattern="*", dst="include", src="usr/include", symlinks=True)
        self.copy(pattern="copyright", src="usr/share/doc/" + self.name, symlinks=True)

    def copy_cleaned(self, source, prefix_remove, dest):
        for e in source:
            if (e.startswith(prefix_remove)):
                entry = e[len(prefix_remove):]
                if len(entry) > 0 and not entry in dest:
                    dest.append(entry)

    def package_info(self):
        pkgpath =  "lib/pkgconfig"
        pkgconfigpath = os.path.join(self.package_folder, pkgpath)
        if self.settings.os == "Linux":
            self.output.info("package info file: " + pkgconfigpath)
            with tools.environment_append({'PKG_CONFIG_PATH': pkgconfigpath}):
                # only export gio-unix-2.0 for now, not gio-2.0, glib-2.0, gmodule-2.0, gmodule-export-2.0, gmodule-no-export-2.0, gobject-2.0, gthread-2.0
                pkg_config = tools.PkgConfig("gio-unix-2.0", variables={ "prefix" : self.package_folder } )

                # if self.settings.compiler == 'gcc':
                #     # Allow executables consuming this package to ignore missing secondary dependencies at compile time
                #     # needed so we can use libglib2.0.so withouth providing a couple of secondary library dependencies
                #     # http://www.kaizou.org/2015/01/linux-libraries.html
                #     self.cpp_info.exelinkflags.extend(['-Wl,--unresolved-symbols=ignore-in-shared-libs'])

                self.output.info("lib_paths %s" % self.cpp_info.lib_paths)

                # exclude all libraries from dependencies here, they are separately included
                copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
                self.output.info("libs: %s" % self.cpp_info.libs)
        else:
            self.cpp_info.includedirs.append(os.path.join("include"))
        # add additional path to sub directories since some libraries use them this way
        self.cpp_info.includedirs.append(os.path.join("include", "glib-2.0"))
        self.cpp_info.includedirs.append(os.path.join("include", "gio-unix-2.0"))
        # add extra include path for glibconfig.h
        self.cpp_info.includedirs.append(os.path.join("lib", "glib-2.0", "include"))
        self.output.info("include_paths: %s" % self.cpp_info.include_paths)
        self.output.info("includedirs: %s" % self.cpp_info.includedirs)
