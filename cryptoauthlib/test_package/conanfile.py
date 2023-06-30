#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake


class CryptoAuthLibTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run('ctest --output-on-failure')
