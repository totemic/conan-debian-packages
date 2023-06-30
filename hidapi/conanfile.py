#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan receipt package for USB Library
"""
import os
from conans import ConanFile, CMake, tools
#from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools


class LibUSBConan(ConanFile):
    """Download libusb source, build and create package
    """
    name = "hidapi"
    version = "0.9.0"
    settings = "os", "compiler", "build_type", "arch"
    topics = ("conan", "libusb", "usb", "device")
    options = {"shared": [True, False], "libusb": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'libusb': False, 'fPIC': True}
    homepage = "https://github.com/libusb/hidapi"
    url = "http://github.com/jens-totemic/conan-hidapi"
    license = "LGPL-2.1"
    description = "A Simple library for communicating with USB and Bluetooth HID devices on Linux, Mac and Windows."
    _source_subfolder = "sources"
    generators = "cmake"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.libusb
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        release_name = "%s-%s" % (self.name, self.version)
        unpacked_name = "%s-%s" % (self.name, release_name)
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, release_name),
                  sha256="630ee1834bdd5c5761ab079fd04f463a89585df8fcae51a7bfe4229b1e02a652")
        os.rename(unpacked_name, self._source_subfolder)

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.libusb:
                self.requires("libusb/1.0.22@totemic/stable")
            else:
                self.requires("libudev1/237@totemic/stable")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["HIDAPI_BUILD_SHARED"] = self.options.shared
        if self.settings.os == "Linux":
            cmake.definitions["HIDAPI_BUILD_LIBUSB"] = self.options.libusb
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):   
        self.cpp_info.libs = ["hidapi"]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("c")
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "FreeBSD":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Macos":
            # self.cpp_info.libs.append("objc")
            # self.cpp_info.libs.append("-Wl,-framework,IOKit")
            # self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
            self.cpp_info.exelinkflags.append('-framework IOKit')
            self.cpp_info.exelinkflags.append('-framework CoreFoundation')
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags     
        else:
            self.cpp_info.libs.append("c")
            self.cpp_info.libs.append("pthread")

    # def _build_visual_studio(self):
    #     with tools.chdir(self._source_subfolder):
    #         solution_file = "libusb_2015.sln"
    #         if self.settings.compiler.version == "12":
    #             solution_file = "libusb_2013.sln"
    #         elif self.settings.compiler.version == "11":
    #             solution_file = "libusb_2012.sln"
    #         solution_file = os.path.join("msvc", solution_file)
    #         platforms = {"x86":"Win32"}
    #         msbuild = MSBuild(self)
    #         msbuild.build(solution_file, platforms=platforms, upgrade_project=False)

    # def _build_autotools(self, configure_args=None):
    #     autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
    #     autotools.fpic = self.options.fPIC
    #     with tools.chdir(self._source_subfolder):
    #         autotools.configure(args=configure_args)
    #         autotools.make()
    #         autotools.make(args=["install"])

    # def _build_mingw(self):
    #     configure_args = ['--enable-shared' if self.options.shared else '--disable-shared']
    #     configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
    #     if self.settings.arch == "x86_64":
    #         configure_args.append('--host=x86_64-w64-mingw32')
    #     if self.settings.arch == "x86":
    #         configure_args.append('--build=i686-w64-mingw32')
    #         configure_args.append('--host=i686-w64-mingw32')
    #     self._build_autotools(configure_args)

    # def _build_unix(self):
    #     configure_args = ['--enable-shared' if self.options.shared else '--disable-shared']
    #     configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
    #     if self.settings.os == "Linux":
    #         configure_args.append('--enable-udev' if self.options.enableUdev else '--disable-udev')
    #     self._build_autotools(configure_args)

    # def build(self):
    #     if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
    #         self._build_visual_studio()
    #     elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
    #         self._build_mingw()
    #     else:
    #         self._build_unix()

    # def _package_visual_studio(self):
    #     self.copy(pattern="libusb.h", dst=os.path.join("include", "libusb-1.0"), src=os.path.join(self._source_subfolder, "libusb"), keep_path=False)
    #     arch = "x64" if self.settings.arch == "x86_64" else "Win32"
    #     source_dir = os.path.join(self._source_subfolder, arch, str(self.settings.build_type), "dll" if self.options.shared else "lib")
    #     if self.options.shared:
    #         self.copy(pattern="libusb-1.0.dll", dst="bin", src=source_dir, keep_path=False)
    #         self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
    #         self.copy(pattern="libusb-usbdk-1.0.dll", dst="bin", src=source_dir, keep_path=False)
    #         self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)
    #     else:
    #         self.copy(pattern="libusb-1.0.lib", dst="lib", src=source_dir, keep_path=False)
    #         self.copy(pattern="libusb-usbdk-1.0.lib", dst="lib", src=source_dir, keep_path=False)

    # def package(self):
    #     self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
    #     if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
    #         self._package_visual_studio()

    # def package_info(self):
    #     self.cpp_info.libs = tools.collect_libs(self)
    #     self.cpp_info.includedirs.append(os.path.join("include", "libusb-1.0"))
    #     if self.settings.os == "Linux":
    #         self.cpp_info.libs.append("pthread")
    #         # if self.options.enableUdev:
    #         #     self.cpp_info.libs.append("udev")
    #     elif self.settings.os == "Macos":
    #         self.cpp_info.libs.append("objc")
    #         self.cpp_info.libs.append("-Wl,-framework,IOKit")
    #         self.cpp_info.libs.append("-Wl,-framework,CoreFoundation")
