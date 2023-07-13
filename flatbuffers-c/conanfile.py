from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get

required_conan_version = ">=1.53.0"

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # According to https://github.com/conan-io/conan/issues/11937#issuecomment-1224038952
        # we need to define all cmake variables as "cached" that are defined in the CMakeLists.txt file
        # before the call to "project()"
        tc.cache_variables["FLATCC_TEST"] = bool(self.options.tests)
        # these variables are defined after project() in the CMakeLists.txt file
        tc.variables["FLATCC_RTONLY"] = bool(self.options.runtimeOnly)
        tc.variables["FLATCC_INSTALL"] = True
        tc.variables["FLATCC_REFLECTION"] = bool(self.options.reflection)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        # TODO: this setting was needed since CLang generated a warning in v 0.6.1. 
        # Check if this can be removed in future versions again 
        tc.variables["FLATCC_ALLOW_WERROR"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        # Run patch that removes the "_d" prefix from libraries and compiler. 
        # We don't need it as each version has it's own conan package anyway 
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        #self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["flatccrt"]
        #self.cpp_info.includedirs = ["include"]
        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")
