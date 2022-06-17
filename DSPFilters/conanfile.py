from conans import ConanFile, CMake, tools


class DSPFiltersRecipe(ConanFile):
    name = "DSPFilters"
    homepage = "https://github.com/vinniefalco/DSPFilters"
    description = "A Collection of Useful C++ Classes for Digital Signal Processing"
    url = "https://github.com/vinniefalco/DSPFilters.git"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports = ["CMakeLists.txt"]

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["DSPFilters"]
