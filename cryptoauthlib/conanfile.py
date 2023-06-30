#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from conans import ConanFile, CMake, tools

class CryptoAuthLib(ConanFile):
    name = 'cryptoauthlib'
    version = '3.3.3'
    license = 'MIT'
    url = 'https://github.com/jens-totemic/conan-cryptoauthlib'
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
    exports_sources = ["lib/*", "01-support-osx.diff", "02-fix-install-location.diff"]
    generators = "cmake"

    scm = {
        'type': 'git',
        'url': 'https://github.com/MicrochipTech/cryptoauthlib.git',
        'revision': 'v'+version
    }

    def requirements(self):
        if self.settings.os == "Linux" and self.options['halHID']:
#             self.requires("libusb/1.0.22@totemic/stable")
            self.requires("libudev1/237@totemic/stable")

#     def configure(self):
#         if self.settings.os == 'Linux' and self.options['halHID']:
#             raise Exception("Sorry - libudev isn't generally available in Conan yet so I can't build the library "
#                             "with this configuration.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ATCA_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ATCA_HAL_KIT_HID"] = self.options.halHID
        cmake.definitions["ATCA_HAL_I2C"] = self.options.halI2C
        cmake.definitions["ATCA_HAL_CUSTOM"] = self.options.halCustom
        cmake.definitions["ATCA_PRINTF"] = self.options.debugOutput
        cmake.definitions["ATCA_PKCS11"] = self.options.pkcs11
        cmake.definitions["ATCA_MBEDTLS"] = self.options.mbedtls
        cmake.definitions["PKCS11_DEBUG_ENABLE"] = self.options.debugOutputPkcs11
        #cmake.configure(source_folder=self._source_subfolder)
        # cmake.configure(source_folder=os.path.join(self.build_folder, 'lib'), build_folder=self.bin_dir)
        cmake.configure()
        return cmake

    def source(self):
        # Fix linker not finding malloc and free on OSX 
        tools.patch(patch_file="01-support-osx.diff")
        # Fix install directory hard-coded to / 
        tools.patch(patch_file="02-fix-install-location.diff")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # self.copy('*.so' if self.options.shared else '*.a', src=os.path.join(self.bin_dir), dst='lib')
        # self.copy('*.h', src=os.path.join(self.build_folder, 'lib'), dst='include')
        self.copy('*.h', src='lib', dst='include/cryptoauthlib')
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = [
            'include',
            os.path.join('include', 'cryptoauthlib'),
            os.path.join('include', 'cryptoauthlib', 'hal'),
            os.path.join('include', 'cryptoauthlib', 'basic'),
            os.path.join('include', 'cryptoauthlib', 'crypto'),
            os.path.join('include', 'cryptoauthlib', 'atcacert')
        ]
        self.cpp_info.libs = ["cryptoauth"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["rt"])
