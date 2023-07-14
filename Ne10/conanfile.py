# -*- coding: utf-8 -*-
import os
from conans import ConanFile, CMake, tools


class Ne10Conan(ConanFile):
    name = "Ne10"
    version = "1.2.2-2020.04.08"  # version number rarely changes, so add date
    homepage = "https://github.com/projectNe10/Ne10"
    description = "An open optimized software library project for the ARM® Architecture."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/Ne10"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    generators = "cmake"
    exports = "LICENSE"
    exports_sources = ["patches/01-build-c-only.patch", "patches/02-increase-cpuinfo-buffer-size.patch"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def _configure_cmake(self):
        cmake = CMake(self)
        armOnly = False
        if self.settings.os == "Linux":
            # Need to manually set this, as the CMake project has no 'conan_setup' step
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
            if self.settings.arch == "armv7hf":
                armOnly = True
                cmake.definitions["NE10_LINUX_TARGET_ARCH"] = "armv7"
                cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm"
            elif self.settings.arch == "armv8":
                armOnly = True
                cmake.definitions["NE10_LINUX_TARGET_ARCH"] = "aarch64"
                cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "arm"

        cmake.definitions["GNULINUX_PLATFORM"] = True
        cmake.definitions["NE10_BUILD_ARM_ONLY"] = armOnly
        cmake.definitions["NE10_BUILD_SHARED"] = self.options.shared
        cmake.definitions["NE10_BUILD_STATIC"] = not self.options.shared
        cmake.configure()
        return cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=".", strip_root=True)
        tools.patch(patch_file="patches/01-build-c-only.patch")
        tools.patch(patch_file="patches/02-increase-cpuinfo-buffer-size.patch")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "ne10"))
        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")