import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class MlibConan(ConanFile):
    name = "mlib"
    version = "0.7.0"
    homepage = "https://github.com/P-p-H-d/mlib"
    description = "Library for using generic and type safe container in pure C language (C99 or C11) for a wide collection of container (comparable to the C++ STL)."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/mlib"
    exports = "LICENSE"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=".", strip_root=True)

    def package(self):
        self.copy("*.h", excludes=["bench/*", "tests/*"], dst="mlib")
            
    def package_info(self):
        self.cpp_info.include_paths.append(self.package_folder)
        self.output.info("include_paths: %s" % self.cpp_info.include_paths)
