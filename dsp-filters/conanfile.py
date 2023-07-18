from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get

required_conan_version = ">=1.53.0"

class DSPFiltersRecipe(ConanFile):
    name = "dsp-filters"
    version = "cci.20170309"
    homepage = "https://github.com/vinniefalco/DSPFilters"
    description = "A Collection of Useful C++ Classes for Digital Signal Processing"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/dsp-filters"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = ["CMakeLists.txt"]

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        #self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = ["DSPFilters"]
        #self.cpp_info.includedirs = ["include"]
        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")
