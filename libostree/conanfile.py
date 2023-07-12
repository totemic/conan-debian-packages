#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, copy
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os
from pathlib import Path

class LibOSTreeConan(ConanFile):
    name = "libostree"
    version = "2022.1"
    settings = "os", "compiler", "build_type", "arch"
    topics = ("conan", "libostree", "ostree")
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': True, 'fPIC': True}
    homepage = "https://github.com/ostreedev/ostree"
    url = "http://github.com/totemic/conan-libostree"
    license = "LGPLv2+"
    description = "libostree is both a shared library and suite of command line tools that combines a git-like model for committing and downloading bootable filesystem trees, along with a layer for deploying them and managing the bootloader configuration"
    _source_subfolder = "source_subfolder"
    #exports = ["LICENSE.md"]

    def layout(self):
        basic_layout(self, src_folder="src")
        # this set the variable '--datarootdir=${prefix}/share'
        self.cpp.package.resdirs = ["share"]

    def requirements(self):
        self.requires("libglib2.0-0/2.56.4@totemic/stable")
        # if self.settings.os == "Linux":
            # todo: we should also add depdencies to libsystemd0.so.1, libcurl.so.4
            # right now this is handled by telling the linker to ignore unknown symbols in secondary dependencies
        #     self.requires("libcurl/7.66.0@totemic/stable")

    def build_requirements(self): 
        # installer = tools.SystemPackageTool()
        # installer = tools.SystemPackageTool(default_mode="disabled")
        # installer.install("libtool bison:amd64 libglib2.0-dev:arm64", update=True, force=True)
        # installer.install(["libtool", "bison:amd64", "libglib2.0-dev:arm64"], update=True)
        # installer.install(["libtool bison"], update=True)
        # installer.install(["libtool bison libglib2.0-dev liblzma-dev libmount-dev e2fslibs-dev libfuse-dev libcurl4-openssl-dev libsystemd-dev libgpgme-dev"], update=False, arch_names=)

        # tools.SystemPackageTool() doesn't support a mode where we install some native and some cross-compile libraries
        # for now, we'll directly execute apt, which will only work on debian systems
        if self.settings.os == "Linux":
        #if tools.os_info.with_apt:
            self.run("sudo apt-get update")
            # build host dependencies
            self.run("sudo apt-get install -y --no-install-recommends libtool bison")
            # cross-compilation libraries
            packages = "libglib2.0-dev liblzma-dev libmount-dev e2fslibs-dev libfuse-dev libcurl4-openssl-dev libsystemd-dev libgpgme-dev".split(" ")
            parsed_packages = [self.get_package_name(pkg, str(self.settings.arch)) for pkg in packages]
            self.output.info(f'sudo apt-get install {" ".join(parsed_packages)}')
            self.run("sudo apt-get install -y --no-install-recommends %s" % " ".join(parsed_packages))
            self.output.info("after build_requirements")
        #else: 
        #    self.output.warn("Unsupported Linux version. Cannot install build dependencies, requires apt tooling.")

    def get_package_name(self, package, arch):
        arch_names = {"x86_64": "amd64",
                        "x86": "i386",
                        "ppc32": "powerpc",
                        "ppc64le": "ppc64el",
                        "armv7": "arm",
                        "armv7hf": "armhf",
                        "armv8": "arm64",
                        "s390x": "s390x"}
        if arch in arch_names:
            return "%s:%s" % (package, arch_names[arch])
        return package

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.settings.os != "Linux":
            return

        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        static_compiler = os.environ['CC'] if 'CC' in os.environ else "gcc"
        cfgArgs = [
            "--libexecdir=${prefix}/bin",
            "--with-curl", 
            "--without-soup", # --with-soup
            "--without-avahi",  # --with-avahi
            "--with-dracut",
            "--with-gpgme=no", 
            "--with-libmount",
            # --with-libarchive 
            # --with-grub2
            # --with-grub2-mkconfig-path=/usr/sbin/grub-mkconfig
            "--with-selinux",
            "--with-libsystemd",
            "--with-systemdsystemunitdir=${libdir}/systemd/system",
            "--with-systemdsystemgeneratordir=${libdir}/systemd/system-generators", 
            "--with-static-compiler=%s" % static_compiler
        ]

        #'--libexecdir=${prefix}/bin'
        #'--prefix=/home/conan/.conan/data/libostree/2022.1/totemic/stable/package/2a7b9f2a721e6eadffccde89211f77ec6e2b6307'
        tc = AutotoolsToolchain(self, prefix="")

        # these setting not needed, are added automatically by AutotoolsToolchain 
        # if self.options.shared:
        #     cfgArgs += ["--enable-shared", "--disable-static"]
        # else:
        #     cfgArgs += ["--disable-shared", "--enable-static"]
        #tc.fpic = self.options.get_safe("fPIC", True)

        tc.configure_args.extend(cfgArgs)

        # set BASH_COMPLETIONSDIR to fixed value that honors ${prefix}. 
        # Otherwise it is set through pkgconfig variables and might fail in the installation step if it points to /usr/share 
        env = tc.environment()
        env.define("BASH_COMPLETIONSDIR", "${prefix}/share/bash-completion/completions")
        tc.generate(env)

        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        if self.settings.os == "Linux":
            autotools = Autotools(self)
            #autotools.autoreconf()
            autotools.configure()
            autotools.make()
        else:
            # We allow using it on all platforms, but for anything except Linux nothing is produced
            # this allows unconditionally including this conan package on all platforms
            self.output.info("Nothing to be done for this OS")  

    def package(self):
        if self.settings.os == "Linux":
            autotools = Autotools(self)
            autotools.install()
            # this link is pointing to the wrong location. Since we don't need it, just remove it
            os.remove(Path(self.package_folder)/"etc"/"grub.d"/"15_ostree")
        else:
            self.output.info(f"source_folder: {self.source_folder}")
            # on non-linux platforms, expose the header files to help cross-development
            copy(self, "*.h", src=Path(self.source_folder)/"src"/"libostree", dst=Path(self.package_folder)/"include"/"ostree-1")


    def package_info(self):
        #self.cpp_info.libdirs = ["lib"]

        # we only add the libs on Linux, on other platforms just the include files
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["ostree-1"]

        self.cpp_info.includedirs = ["include", str(Path("include")/"ostree-1")]

        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")
