import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.client.tools.oss import get_gnu_triplet

class DebianDependencyConan(ConanFile):
    name = "libglib2.0-0"
    version = "2.56.4"
    build_version = "0ubuntu0.18.04.6" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libglib2.0-0"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libglib2.0-dev
    description = "Systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    url = "https://github.com/totemic/conan-debian-packages/libglib2.0-0"    
    license = "LGPL"
    settings = "os", "arch"

    # def requirements(self):
    #     if self.settings.os == "Linux":
    #         # todo: we should also add depdencies to libselinux.so.1, liblzma.so.5, libgcrypt.so.20
    #         # right now this is handled by telling the linker to ignore unknown symbols in secondary dependencies
    #         self.requires("libudev1/237@totemic/stable")

    def translate_arch(self):
        # ubuntu does not have v7 specific libraries
        arch_names = {
            "x86_64": "amd64",
            "x86": "i386",
            "ppc32": "powerpc",
            "ppc64le": "ppc64el",
            "armv7": "arm",
            "armv7hf": "armhf",
            "armv8": "arm64",
            "s390x": "s390x"
        }
        return arch_names[str(self.settings.arch)]
        
    def _download_extract_deb(self, url, sha256):
        filename = "./download.deb"
        deb_data_file = "data.tar.xz"
        tools.download(url, filename)
        tools.check_sha256(filename, sha256)
        # extract the payload from the debian file
        self.run("ar -x %s %s" % (filename, deb_data_file))
        os.unlink(filename)
        tools.unzip(deb_data_file)
        os.unlink(deb_data_file)

    def triplet_name(self, force_linux=False):
        # we only need the autotool class to generate the host variable
        autotools = AutoToolsBuildEnvironment(self)

        if force_linux:
            return get_gnu_triplet("Linux", str(self.settings.arch), "gnu")
        # construct path using platform name, e.g. usr/lib/arm-linux-gnueabihf/pkgconfig
        # if not cross-compiling it will be false. In that case, construct the name by hand
        return autotools.host or get_gnu_triplet(str(self.settings.os), str(self.settings.arch), self.settings.get_safe("compiler"))
        
    def build(self):
        # For anything non-linux, we will fetch the header files, using the x86 package
        if self.settings.arch == "x86_64":
            # https://packages.ubuntu.com/bionic-updates/amd64/libglib2.0-0/download
            sha_lib = "d83313ca3bd99eec1934f2da1c7cddabe9acf42fa0914eb7af778139db216da6"
            # https://packages.ubuntu.com/bionic-updates/amd64/libglib2.0-dev/download
            sha_dev = "dae746eebff565fd183a29b8c1b9d26179f07d897541b0ae1ee8dbe9beca8589"

            url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
            url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
        elif self.settings.arch == "armv8":
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-0/download
            sha_lib = "c16be203f547a977326e13cd6f3935022679f9fcdaa918bdcd315e820b33e5d0"
            # https://packages.ubuntu.com/bionic-updates/arm64/libglib2.0-dev/download
            sha_dev = "c1e66bf2e5e5d8f658c0e4362c965741d950425608aecd51518f26ffe040f6da"

            url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
            url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
        else: # armv7hf
            # https://packages.ubuntu.com/bionic-updates/armhf/libglib2.0-0/download
            sha_lib = "a795e2277aaa81c05b6c507f39fba04ddddafe9a9acccda357034ff05da4846f"
            # https://packages.ubuntu.com/bionic-updates/armhf/libglib2.0-dev/download
            sha_dev = "ee2a5443bf5a9d912ff22978a61224ef6856f125de5b81d95721a5af37a088e8"

            url_lib = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-0_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
            url_dev = ("http://ports.ubuntu.com/ubuntu-ports/pool/main/g/glib2.0/libglib2.0-dev_%s-%s_%s.deb"
                % (str(self.version), self.build_version, self.translate_arch()))
        self._download_extract_deb(url_lib, sha_lib)
        self._download_extract_deb(url_dev, sha_dev)

    def package(self):
        pattern = "*" if self.settings.os == "Linux" else "*.h"
        triplet_name = self.triplet_name(self.settings.os != "Linux")
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
                self.copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
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
