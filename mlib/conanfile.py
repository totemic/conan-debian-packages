from conan import ConanFile
from conan.tools.files import copy, get

from pathlib import Path

required_conan_version = ">=1.53.0"

class MlibConan(ConanFile):
    name = "mlib"
    version = "0.7.0"
    homepage = "https://github.com/P-p-H-d/mlib"
    description = "Library for using generic and type safe container in pure C language (C99 or C11) for a wide collection of container (comparable to the C++ STL)."
    url = "https://github.com/totemic/conan-package-recipes/tree/main/mlib"
    license = "BSD-2-clause"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.h", excludes=["bench/*", "tests/*"], src=self.build_folder, dst=Path(self.package_folder)/"mlib")
            
    def package_info(self):
        self.cpp_info.includedirs = ["."]
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")