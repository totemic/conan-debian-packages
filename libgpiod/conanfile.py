from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, copy
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from pathlib import Path

required_conan_version = ">=1.53.0"

# TODO: switch to https://github.com/conan-io/conan-center-index/blob/master/recipes/libgpiod once it supports v1.2.1

class LibgpiodConan(ConanFile):
    name = "libgpiod"
    version = "1.2.1"
    license = "LGPL-2.1-or-later"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/libgpiod"
    description = "Library for interacting with the linux GPIO character device"
    topics = ["gpio"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def build_requirements(self):
        if self.settings.os == "Linux":
            pass
            # installer = tools.SystemPackageTool()
            # installer.install("autoconf-archive")
            # self.build_requires("libtool/2.4.6")
            # self.build_requires("pkgconf/1.7.4")
            # self.build_requires("autoconf-archive/2021.02.19")
            # self.build_requires("linux-headers-generic/5.13.9")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.settings.os != "Linux":
            return

        # env = VirtualBuildEnv(self)
        # env.generate()
        # if not cross_building(self):
        #     env = VirtualRunEnv(self)
        #     env.generate(scope="build")

        tc = AutotoolsToolchain(self, prefix="")

        # these setting not needed, are added automatically by AutotoolsToolchain 
        # if self.options.shared:
        #     cfgArgs += ["--enable-shared", "--disable-static"]
        # else:
        #     cfgArgs += ["--disable-shared", "--enable-static"]
        #tc.fpic = self.options.get_safe("fPIC", True)

        tc.configure_args.extend([
            "--enable-bindings-cxx", 
            "--enable-tools"
        ])
        if cross_building(self):
            # fixes error "undefined reference to `rpl_malloc'"
            tc.configure_args.append("ac_cv_func_malloc_0_nonnull=yes")
            tc.configure_args.append("ac_cv_func_realloc_0_nonnull=yes")
        tc.generate()

        # env = tc.environment()
        # # fixes error "undefined reference to `rpl_malloc'"
        # env.define("ac_cv_func_malloc_0_nonnull", "yes")
        # tc.generate(env)

        AutotoolsDeps(self).generate()
        # PkgConfigDeps(self).generate()

    def build(self):
        if self.settings.os == "Linux":
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()
        else:
            # We allow using it on all platforms, but for anything except Linux nothing is produced
            # this allows unconditionally including this conan package on all platforms
            self.output.info("Nothing to be done for this OS")

    def package(self):
        if self.settings.os == "Linux":
            autotools = Autotools(self)
            autotools.install()
        else:
            # On non-linux platforms, expose the header files to help cross-development
            copy(self, pattern="*.h", src=Path(self.source_folder)/"include", dst=Path(self.package_folder)/"include")
            copy(self, pattern="*.hpp", src=Path(self.source_folder)/"bindings"/"cxx", dst=Path(self.package_folder)/"include")

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.libs = ["gpiodcxx", "gpiod"]

        self.output.info(f"libdirs {self.cpp_info.libdirs}")
        self.output.info(f"libs: {self.cpp_info.libs}")
        self.output.info(f"includedirs: {self.cpp_info.includedirs}")
