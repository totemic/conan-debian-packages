# -*- coding: utf-8 -*-
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get
from pathlib import Path

required_conan_version = ">=1.53.0"

class Ne10Conan(ConanFile):
    name = "Ne10"
    version = "1.2.2-2020.04.08"  # version number rarely changes, so add date
    homepage = "https://github.com/projectNe10/Ne10"
    description = "An open optimized software library project for the ARM® Architecture."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/Ne10"
    license = 'BSD-3-Clause'
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}    
    # exports = "LICENSE"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        armOnly = False
        if self.settings.os == "Linux":
            # Need to manually set this, as the CMake project has no 'conan_setup' step
            tc.variables['CMAKE_POSITION_INDEPENDENT_CODE'] = bool(self.options.fPIC)
            if self.settings.arch == "armv7hf":
                armOnly = True
                tc.variables["NE10_LINUX_TARGET_ARCH"] = "armv7"
                tc.variables["CMAKE_SYSTEM_PROCESSOR"] = "arm"
            elif self.settings.arch == "armv8":
                armOnly = True
                tc.variables["NE10_LINUX_TARGET_ARCH"] = "aarch64"
                tc.variables["CMAKE_SYSTEM_PROCESSOR"] = "arm"

        tc.variables["GNULINUX_PLATFORM"] = True
        tc.variables["NE10_BUILD_ARM_ONLY"] = armOnly
        tc.variables["NE10_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["NE10_BUILD_STATIC"] = not self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(str(Path("include")/"ne10"))
        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")