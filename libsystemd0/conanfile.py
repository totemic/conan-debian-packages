import os
from conans import ConanFile, tools
try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import copy_cleaned, download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

class DebianDependencyConan(ConanFile):
    name = "libsystemd0"
    version = "237"
    build_version = "3ubuntu10.42" 
    homepage = "https://packages.ubuntu.com/bionic-updates/libsystemd0"
    # dev_url = https://packages.ubuntu.com/bionic-updates/libsystemd-dev
    description = "Systemd is a suite of basic building blocks for a Linux system. It provides a system and service manager that runs as PID 1 and starts the rest of the system."
    url = "https://github.com/totemic/conan-package-recipes/libsystemd0"    
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
                sha_lib = "939b4bba449ef4974a01981cea8339bfc7d925b1bf2e9baa9617db529c730157"
                # https://packages.ubuntu.com/bionic-updates/amd64/libsystemd-dev/download
                sha_dev = "32f1f3f917c5f0d7b53e4bfb1f1087159e365d89405ec85acf0bd43dee0fbac0"

                url_lib = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libsystemd0_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
                url_dev = ("http://us.archive.ubuntu.com/ubuntu/pool/main/s/systemd/libsystemd-dev_%s-%s_%s.deb"
                   % (str(self.version), self.build_version, translate_arch(self)))
            elif self.settings.arch == "armv8":
                # https://packages.ubuntu.com/bionic-updates/arm64/libsystemd0/download
                sha_lib = "2ec53633f7ad8998159ac65da5a7dbd545abdf6e250382c0a70d8be6dbe74185"
                # https://packages.ubuntu.com/bionic-updates/arm64/libsystemd-dev/download
                sha_dev = "2c3c39e385b61826862dac7f5f480fa925810d41666acc0c29b0ff58c13c0aa1"

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
        pkgpath =  "lib/pkgconfig"
        pkgconfigpath = os.path.join(self.package_folder, pkgpath)
        if self.settings.os == "Linux":
            self.output.info("package info file: " + pkgconfigpath)
            with tools.environment_append({'PKG_CONFIG_PATH': pkgconfigpath}):
                pkg_config = tools.PkgConfig("libsystemd", variables={ "prefix" : self.package_folder } )

                # if self.settings.compiler == 'gcc':
                #     # Allow executables consuming this package to ignore missing secondary dependencies at compile time
                #     # needed so we can use libsystemd.so withouth providing a couple of secondary library dependencies
                #     # http://www.kaizou.org/2015/01/linux-libraries.html
                #     self.cpp_info.exelinkflags.extend(['-Wl,--unresolved-symbols=ignore-in-shared-libs'])

                self.output.info("lib_paths %s" % self.cpp_info.lib_paths)

                # exclude all libraries from dependencies here, they are separately included
                copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs)
                self.output.info("libs: %s" % self.cpp_info.libs)

                self.output.info("include_paths: %s" % self.cpp_info.include_paths)
