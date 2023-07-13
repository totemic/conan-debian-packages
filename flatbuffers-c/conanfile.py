import os
from conans import ConanFile, CMake, tools


class FlatbuffersConan(ConanFile):
    name = "flatbuffers-c"
    version = "0.6.1"
    license = "Apache License 2.0"
    homepage = "https://github.com/dvidelabs/flatcc"
    description = "FlatBuffers Compiler and Library in C for C"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/flatbuffers-c"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "runtimeOnly": [True, False],
               "tests": [True, False],
               "reflection": [True, False]}
    default_options = {"shared": False, "fPIC": True, "runtimeOnly": True, "tests": False, "reflection": False}
    exports_sources = ["patches/0.6.1-001-RemoveDebugPostfix.diff"]
    generators = "cmake"


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FLATCC_RTONLY"] = self.options.runtimeOnly
        cmake.definitions["FLATCC_INSTALL"] = True
        cmake.definitions["FLATCC_TEST"] = self.options.tests
        cmake.definitions["FLATCC_REFLECTION"] = self.options.reflection
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        # TODO: this setting was needed since CLang generated a warning in v 0.6.1. 
        # Check if this can be removed in future versions again 
        cmake.definitions["FLATCC_ALLOW_WERROR"] = False
        #cmake.configure(source_folder=self._source_subfolder)
        cmake.configure()
        return cmake

    def source(self):
        # Run patch that removes the "_d" prefix from libraries and compiler. 
        # We don't need it as each version has it's own conan package anyway 
        tools.get(**self.conan_data["sources"][self.version], destination=".", strip_root=True)
        tools.patch(patch_file="patches/0.6.1-001-RemoveDebugPostfix.diff")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
#         self.copy("epl-v10", src=self._source_subfolder, dst="licenses", keep_path=False)
#         self.copy("notice.html", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['flatccrt']
        self.output.info("lib_paths %s" % self.cpp_info.lib_paths)
        self.output.info("libs: %s" % self.cpp_info.libs)
        self.output.info("include_paths: %s" % self.cpp_info.include_paths)
