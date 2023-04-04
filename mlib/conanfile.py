import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class MlibConan(ConanFile):
    name = "mlib"
    version = "0.7.0"
    source_subfolder = "mlib"
    scm = {
        "type": "git",
        "subfolder": source_subfolder,
        "url": "https://github.com/P-p-H-d/mlib.git",
        "revision": "V" + version
    }

    homepage = "https://github.com/P-p-H-d/mlib"
    description = "Library for using generic and type safe container in pure C language (C99 or C11) for a wide collection of container (comparable to the C++ STL)."
    url = "https://github.com/jens-totemic/conan-mlib"
    exports = "LICENSE"

    def package(self):
        with tools.chdir(self.source_subfolder):
            #self.copy("LICENSE")
            self.copy("*.h", excludes=["mlib/bench/*", "mlib/tests/*"])
            
    def package_info(self):
            self.cpp_info.include_paths.append(self.package_folder)
            self.output.info("include_paths: %s" % self.cpp_info.include_paths)
