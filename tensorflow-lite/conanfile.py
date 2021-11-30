from os.path import join
from conans import AutoToolsBuildEnvironment, ConanFile, tools

BUILD_SUBFOLDER = "tensorflow/lite/tools/make"


class TFLiteConan(ConanFile):
    # Basic info
    name = "tensorflow-lite"
    scm = None

    # Other package details
    description = "https://www.tensorflow.org"
    license = "Apache-2.0"

    # Conan build process settings
    settings = "os", "arch", "compiler", "build_type"

    # def system_requirements(self):
    #     installer = tools.SystemPackageTool()
    #     installer.install("make")

    def configure(self):
        self.scm = dict(
            type="git",
            url="https://github.com/tensorflow/tensorflow.git",
            revision=self.conan_data["revisions"][self.version]
        )

    def export(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            self.copy(patch)

    def requirements(self):
        self.requires('flatbuffers/1.12.0@google/stable')

    # def build_requirements(self):
    #     self.build_requires('libzip/1.8.0')

    def source(self):
        for patch in self.conan_data["patches"][self.version]:
           tools.patch(patch_file=patch)

        self.run(join(BUILD_SUBFOLDER, "download_dependencies.sh"))

    def build(self):
        build_folder = join(self.source_folder, BUILD_SUBFOLDER)
        is_aarch64 = self.settings.arch == "armv8"

        # Note: the only advantage of using scripts is that when building
        #  on aarch64 with low memory, building will be single-threaded

        # if is_aarch64:
        #     self.run(join(build_folder, "build_aarch64_lib.sh"))
        # else:
        #     self.run(join(build_folder, "build_lib.sh"))

        target_opt = "TARGET=aarch64" if is_aarch64 else ""
        env_vars = {'SCRIPT_DIR': build_folder, 'TENSORFLOW_DIR': self.source_folder}

        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(self.source_folder):
            autotools.make(target=f"{target_opt} -f {build_folder}/Makefile micro", vars=env_vars)

    def package(self):
        self.copy(pattern="*/libtensorflow-lite.a", dst="lib", src=f"tensorflow/lite", keep_path=False)
        self.copy(pattern="*.h", dst="include/tensorflow/lite", src=f"tensorflow/lite", keep_path=True)

    def package_info(self):
        self.cpp_info.libs = ["tensorflow-lite", "stdc++"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["c", "m", "dl", "rt", "pthread"])
