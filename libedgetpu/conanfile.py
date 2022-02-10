import os
from os.path import join

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class LibEdgeTpuConan(ConanFile):
    name = "libedgetpu"
    description = "Source code for the userspace level runtime driver for Coral devices."
    license = "Apache-2.0"
    topics = ("machine-learning", "neural-networks", "deep-learning")

    homepage = "https://github.com/google-coral/libedgetpu"
    url = "https://github.com/totemic/conan-package-recipes"

    settings = "os", "arch", "compiler", "build_type"
    options = {'throttled': [True, False]}
    default_options = {'throttled': False}

    exports = ["patches/*"]

    tf_revisions = {
        "2.6.2": dict(commit="c2363d6d025981c661f8cbecf4c73ca7fbf38caf",
                      sha256="add5982a3ce3b9964b7122dd0d28927b6a9d9abd8f95a89eda18ca76648a0ae8"),
        "2.8.0": dict(commit="3f878cff5b698b82eea85db2b60d65a2e320850e",
                      sha256="21d919ad6d96fcc0477c8d4f7b1f7e4295aaec2986e035551ed263c2b1cd52ee")
    }

    def _should_use_bazel(self):
        return self.settings.os == 'Macos'

    def package_id(self):
        # Making sure that changes in minor version or options of `tensorflow-lite` trigger a unique package id
        # https://docs.conan.io/en/latest/creating_packages/define_abi_compatibility.html
        self.info.requires["tensorflow-lite"].full_package_mode()

    def configure(self):
        is_linux = self.settings.os == 'Linux' and self.settings.arch in ('x86_64', 'armv8')
        is_macos = self.settings.os == 'Macos'
        if not (is_linux or is_macos):
            raise ConanInvalidConfiguration(f"Not available for "
                                            f"({self.settings.os}, {self.settings.arch})")

    def requirements(self):
        self.requires(f'tensorflow-lite/[>=2.6.0]')
        self.requires(f'libusb/1.0.22@totemic/stable')

    def build_requirements(self):
        self.build_requires('flatc/1.12.0')
        if self._should_use_bazel():
            self.build_requires('bazel/4.0.0')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

        tf_lite_version = self.deps_cpp_info['tensorflow-lite'].version

        self.output.info(f"TFLite dependency version {tf_lite_version} detected")

        workspace_path = join(self.source_folder, "workspace.bzl")
        tgt_tf_revision = self.tf_revisions[tf_lite_version]

        # Replacing tensorflow dependency version with the desired one
        base_commit = "a4dfb8d1a71385bd6d122e4f27f86dcebb96712d"
        base_sha256 = "cb99f136dc5c89143669888a44bfdd134c086e1e2d9e36278c1eb0f03fe62d76"
        tools.replace_in_file(workspace_path, base_commit, tgt_tf_revision["commit"])
        tools.replace_in_file(workspace_path, base_sha256, tgt_tf_revision["sha256"])

        # Make sure bazel uses conan's libusb installation as opposed to the system one
        tools.patch(patch_file="patches/bazel_conan_libusb_dep.patch")

        tools.patch(patch_file="patches/makefile_fixes.patch")

    def build(self):
        if self._should_use_bazel():
            env_vars = dict(CONAN_LIBUSB_ROOT=self.deps_cpp_info["libusb"].rootpath)
            if self.settings.os == 'Linux' and self.settings.arch == 'armv8':
                env_vars["CPU"] = "aarch64"

            with tools.environment_append(env_vars):
                suffix = 'throttled' if self.options.throttled else 'direct'
                self.run(f"make -C {self.source_folder} libedgetpu-{suffix}")
        else:
            autotools = AutoToolsBuildEnvironment(self)
            suffix = '-throttled' if self.options.throttled else ''
            autotools.make(target=f"-f {self.source_folder}/makefile_build/Makefile -j6 libedgetpu{suffix}")

    def package(self):
        variant = 'throttled' if self.options.throttled else 'direct'
        bin_dir = join(self.source_folder, 'out')
        include_dir = join(self.source_folder, 'tflite', 'public')

        if self.settings.os == 'Linux':
            if self._should_use_bazel() and self.settings.arch == 'armv8':
                arch = 'aarch64'
            else:
                # The CMake build pipeline has k8 hardcoded in the path
                arch = 'k8'
            lib_name = "libedgetpu.so.1"
            link_name = "libedgetpu.so"
        else:
            arch = 'darwin'
            lib_name = "libedgetpu.1.dylib"
            link_name = "libedgetpu.dylib"

        self.copy("LICENSE", src=self.source_folder, dst="licenses", keep_path=False)
        self.copy("*.h", src=include_dir, dst="include", keep_path=False)
        self.copy("*", src=f"{bin_dir}/{variant}/{arch}", dst="lib", keep_path=False, symlinks=True)

        with tools.chdir(f"{self.package_folder}/lib"):
            os.symlink(lib_name, link_name)

        # Remove absolute path to libusb from the mac binary
        # otool -L libedgetpu.1.0.dylib
        # otool -l libedgetpu.1.0.dylib | grep LC_RPATH -A2
        if self.settings.os == 'Macos':
            # TODO: fix this in the libusb package when building
            self.output.info("Removing hardcoded path from the libusb dependency")
            libusb_root = self.deps_cpp_info["libusb"].rootpath
            self.run(f"install_name_tool -change {libusb_root}/lib/libusb-1.0.0.dylib @rpath/libusb-1.0.0.dylib "
                     f"{self.package_folder}/lib/{lib_name}")

    def package_info(self):
        self.cpp_info.libs = ["edgetpu"]
