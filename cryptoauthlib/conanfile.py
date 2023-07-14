#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

from pathlib import Path

required_conan_version = ">=1.53.0"

class CryptoAuthLib(ConanFile):
    name = 'cryptoauthlib'
    version = '3.3.3'
    license = 'MIT'
    url = "https://github.com/totemic/conan-package-recipes/tree/main/cryptoauthlib"
    homepage = 'https://github.com/MicrochipTech/cryptoauthlib'
    description = 'Library for interacting with the Crypto Authentication secure elements.'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'halHID': [True, False], # Include the HID HAL Driver
        'halI2C': [True, False], # Include the I2C Hal Driver - Linux & MCU only
        'halCustom': [True, False], # Include support for Custom/Plug-in Hal Driver
        'pkcs11': [True, False], # Build PKCS11 Library
        'mbedtls': [True, False], # Integrate with mbedtls
        'debugOutput': [True, False], # Enable Debug print statements in library
        'debugOutputPkcs11': [True, False] # Enable PKCS11 Debug Output
    }
    default_options = {
        'shared': True,
        'fPIC': True, 
        'halHID': False,
        'halI2C': True,
        'halCustom': False,
        'pkcs11': False,
        'mbedtls': False,
        'debugOutput': False,
        'debugOutputPkcs11': False
    }

    def requirements(self):
        if self.settings.os == "Linux" and self.options['halHID']:
#             self.requires("libusb/1.0.22@totemic/stable")
            self.requires("libudev1/237@totemic/stable")

    def export_sources(self):
        # TODO: we copy the OSX dummy HAL driver here. Should this rather be done through the patch file for the version? 
        copy(self, "*", Path(self.recipe_folder)/"lib", Path(self.export_sources_folder)/"lib")
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

#     def configure(self):
#         if self.settings.os == 'Linux' and self.options['halHID']:
#             raise Exception("Sorry - libudev isn't generally available in Conan yet so I can't build the library "
#                             "with this configuration.")
   
    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ATCA_BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["ATCA_HAL_KIT_HID"] = bool(self.options.halHID)
        tc.variables["ATCA_HAL_I2C"] = bool(self.options.halI2C)
        tc.variables["ATCA_HAL_CUSTOM"] = bool(self.options.halCustom)
        tc.variables["ATCA_PRINTF"] = bool(self.options.debugOutput)
        tc.variables["ATCA_PKCS11"] = bool(self.options.pkcs11)
        tc.variables["ATCA_MBEDTLS"] = bool(self.options.mbedtls)
        tc.variables["PKCS11_DEBUG_ENABLE"] = bool(self.options.debugOutputPkcs11)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # copy(self, "*.h", src=Path(self.build_folder)/"lib", dst=Path(self.package_folder)/"include"/"cryptoauthlib")
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = [
            'include',
            str(Path('include')/'cryptoauthlib'),
            str(Path('include')/'cryptoauthlib'/'hal'),
            str(Path('include')/'cryptoauthlib'/'basic'),
            str(Path('include')/'cryptoauthlib'/'crypto'),
            str(Path('include')/'cryptoauthlib'/'atcacert')
        ]
        self.cpp_info.libs = ["cryptoauth"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["rt"])

        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")