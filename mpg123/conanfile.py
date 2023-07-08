from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
import os

try:
    # we can only use this file when running conan install. When exporting this recipe, the file does not yet exist
    # since it's in a different location and conan fails. In order to handle this, we need to catch this here
    from debiantools import download_extract_deb, translate_arch, triplet_name
except ImportError:
    pass 

required_conan_version = ">=1.53.0"

class Mpg123Conan(ConanFile):
    name = "mpg123"
    version = "1.25.10"
    debian_build_version = "2" 
    description = "Fast console MPEG Audio Player and decoder library"
    topics = ("mpeg", "audio", "player", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpg123.org/"
    license = "LGPL-2.1-or-later", "GPL-2.0-or-later"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        # "shared": [True, False],
        # "fPIC": [True, False],
        # "flexible_resampling": [True, False],
        # "network": [True, False],
        # "icy": [True, False],
        # "id3v2": [True, False],
        # "ieeefloat": [True, False],
        # "layer1": [True, False],
        # "layer2": [True, False],
        # "layer3": [True, False],
        # "moreinfo": [True, False],
        # "seektable": [None, "ANY"],
        # "module": ["dummy", "libalsa", "tinyalsa", "win32", "coreaudio"],
    }
    default_options = {
        # "shared": True,
        # "fPIC": True,
        # "flexible_resampling": True,
        # "network": True,
        # "icy": True,
        # "id3v2": True,
        # "ieeefloat": True,
        # "layer1": True,
        # "layer2": True,
        # "layer3": True,
        # "moreinfo": True,
        # "seektable": "1000",
        # "module": "coreaudio",
    }

    # This replaces the customizable options since we are pulling in premade libraries on linux and want to be in control of what
    # happens on OSX to mimic the Linux library settings
    fixed_options = {
        "shared": False,
        "fPIC": False,
        "flexible_resampling": True,
        "network": True,
        "icy": True,
        "id3v2": True,
        "ieeefloat": True,
        "layer1": True,
        "layer2": True,
        "layer3": True,
        "moreinfo": True,
        "seektable": "1000",
        "module": "coreaudio",
    }

    exports = ["../debiantools.py"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _audio_module(self):
        # return {
        #     "libalsa": "alsa",
        # }.get(str(self.options.module), str(self.options.module))

        # use fixed audio settings since we are pulling in ready made Linux libraries
        if self.settings.os == "Linux":
            return "alsa"
        elif self.settings.os == "Windows":
            return "win32"
        elif self.settings.os == "Macos":
            return "coreaudio"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.fixed_options.rm_safe("fPIC")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        # if self.options.shared:
        #     self.options.rm_safe("fPIC")

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")
            # set the build folder to the same location as the source folder
            # this will make sure that we have an include path set to <uuid>/src/src
            # if we don't do this, we get this error
            # In file included from /Users/jens/.conan/data/mpg123/1.25.10/totemic/stable/build/1efa8d13c9f5d5cc46b9a6053c55d5fe4d5bb9e8/src/src/libmpg123/synth_stereo_avx.S:9:
            # /Users/jens/.conan/data/mpg123/1.25.10/totemic/stable/build/1efa8d13c9f5d5cc46b9a6053c55d5fe4d5bb9e8/src/src/libmpg123/mangle.h:14:10: fatal error: 'intsym.h' file not found
            #    #include "intsym.h"
            # compiler line: gcc -E -I. -I/Users/jens/.conan/data/mpg123/1.25.10/totemic/stable/build/1efa8d13c9f5d5cc46b9a6053c55d5fe4d5bb9e8/src -I./src  -DASMALIGN_BALIGN /Users/jens/.conan/data/mpg123/1.25.10/totemic/stable/build/1efa8d13c9f5d5cc46b9a6053c55d5fe4d5bb9e8/src/src/libmpg123/synth_stereo_avx.S | yasm - -pgas -rgas -mamd64 -f macho -o src/libmpg123/synth_stereo_avx.o
            # there might be a better way to pass an additional include path to automake but this line wasn't exposed to make:
            #    self.cpp.source.includedirs = ["src"]  # maps to ./src/src
            self.folders.build = self.folders.source

    def requirements(self):
        # Linux is hard-coded to alsa in our build
        if self.settings.os == "Linux":
            self.requires("libasound2/1.1.8@totemic/stable")
            return

        if self.fixed_options["module"] == "libalsa":
            self.requires("libalsa/1.2.7.2")
        if self.fixed_options["module"] == "tinyalsa":
            self.requires("tinyalsa/2.0.0")

    def validate(self):
        if not str(self.fixed_options["seektable"]).isdigit():
            raise ConanInvalidConfiguration(f"The option -o {self.ref.name}:seektable must be an integer number.")
        if self.settings.os != "Windows" and self.fixed_options["module"] == "win32":
            raise ConanInvalidConfiguration(f"The option -o {self.ref.name}:module should not use 'win32' for non-Windows OS")


    def build_requirements(self):
        # Linux is pulling ready-made debian libraries
        if self.settings.os == "Linux":
            return
        
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")
        if self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["NO_MOREINFO"] = not self.fixed_options["moreinfo"]
            tc.variables["NETWORK"] = self.fixed_options["network"]
            tc.variables["NO_NTOM"] = not self.fixed_options["flexible_resampling"]
            tc.variables["NO_ICY"] = not self.fixed_options["icy"]
            tc.variables["NO_ID3V2"] = not self.fixed_options["id3v2"]
            tc.variables["IEEE_FLOAT"] = self.fixed_options["ieeefloat"]
            tc.variables["NO_LAYER1"] = not self.fixed_options["layer1"]
            tc.variables["NO_LAYER2"] = not self.fixed_options["layer2"]
            tc.variables["NO_LAYER3"] = not self.fixed_options["layer3"]
            tc.variables["USE_MODULES"] = False
            tc.variables["CHECK_MODULES"] = self._audio_module
            tc.variables["WITH_SEEKTABLE"] = self.fixed_options["seektable"]
            tc.generate()
            tc = CMakeDeps(self)
            tc.generate()
        else:
            yes_no = lambda v: "yes" if v else "no"
            tc = AutotoolsToolchain(self)
            tc.configure_args.extend([
                f"--enable-moreinfo={yes_no(self.fixed_options['moreinfo'])}",
                f"--enable-network={yes_no(self.fixed_options['network'])}",
                f"--enable-ntom={yes_no(self.fixed_options['flexible_resampling'])}",
                f"--enable-icy={yes_no(self.fixed_options['icy'])}",
                f"--enable-id3v2={yes_no(self.fixed_options['id3v2'])}",
                f"--enable-ieeefloat={yes_no(self.fixed_options['ieeefloat'])}",
                f"--enable-layer1={yes_no(self.fixed_options['layer1'])}",
                f"--enable-layer2={yes_no(self.fixed_options['layer2'])}",
                f"--enable-layer3={yes_no(self.fixed_options['layer3'])}",
                f"--with-audio={self._audio_module}",
                f"--with-default-audio={self._audio_module}",
                f"--with-seektable={self.fixed_options['seektable']}",
                f"--enable-modules=no",
                f"--enable-shared={yes_no(self.fixed_options['shared'])}",
                f"--enable-static={yes_no(not self.fixed_options['shared'])}",
            ])
            if is_apple_os(self):
                # Needed for fix_apple_shared_install_name invocation in package method
                tc.extra_cflags = ["-headerpad_max_install_names"]
            tc.generate()
            tc = AutotoolsDeps(self)
            tc.generate()

    def build(self):
        # Linux is pulling ready-made debian libraries
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                # https://packages.debian.org/buster/libmpg123-0
                sha_lib = "aad76b14331161db35a892d211f892e8ceda7e252a05dca98b51c00ae59d1b33"
                # https://packages.debian.org/buster/amd64/libout123-0/download
                sha_out = "319060bdf4a17f0b9d876c6ed3d87e7458d262864c7cac7fc7c46796fe06cded"
                # https://packages.debian.org/buster/libmpg123-dev
                sha_dev = "ac90ec3a573dbddbb663d6565fe9985a5d9c994509ac6b11168ed980e964d58f"

            elif self.settings.arch == "armv8":
                # https://packages.debian.org/buster/arm64/libmpg123-0/download
                sha_lib = "f6a7a962e87229af47f406449dc6837d0383be76752180ea22da17c1318e1aae"
                # https://packages.debian.org/buster/arm64/libout123-0/download
                sha_out = "4cb138ec6e20cf66857c2ca69c3914b4c9e74fc8287271fd741608af421528eb"
                # https://packages.debian.org/buster/arm64/libmpg123-dev/download
                sha_dev = "4b5312bc0a8f3a1cb765ff8f3d3d1af1fddcaf05aa723314fbc0277ba6ea43ff"
            else:
                raise Exception("Todo: add binary urls for this architecture")

            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-0_1.25.10-2_amd64.deb
            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-0_1.25.10-2_arm64.deb
            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libout123-0_1.25.10-2_amd64.deb
            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libout123-0_1.25.10-2_arm64.deb
            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-dev_1.25.10-2_amd64.deb
            #http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-dev_1.25.10-2_arm64.deb
            url_lib = ("http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-0_%s-%s_%s.deb"
                % (str(self.version), self.debian_build_version, translate_arch(self)))
            url_out = ("http://ftp.us.debian.org/debian/pool/main/m/mpg123/libout123-0_%s-%s_%s.deb"
                % (str(self.version), self.debian_build_version, translate_arch(self)))
            url_dev = ("http://ftp.us.debian.org/debian/pool/main/m/mpg123/libmpg123-dev_%s-%s_%s.deb"
                % (str(self.version), self.debian_build_version, translate_arch(self)))

            download_extract_deb(self, url_lib, sha_lib)
            download_extract_deb(self, url_out, sha_out)
            download_extract_deb(self, url_dev, sha_dev)
            return


        apply_conandata_patches(self)
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "ports", "cmake"))
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        # on Linux, use the ready made binary libraries
        if self.settings.os == "Linux":
            copy(self, "*", src=os.path.join(self.build_folder, "usr/lib", triplet_name(self)), dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*", src=os.path.join(self.build_folder, "usr/include"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "copyright", src=os.path.join(self.build_folder, "usr/share/doc", self.name), dst=self.package_folder)
            return

        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mpg123")

        self.cpp_info.components["libmpg123"].libs = ["mpg123"]
        self.cpp_info.components["libmpg123"].set_property("pkg_config_name", "libmpg123")
        self.cpp_info.components["libmpg123"].set_property("cmake_target_name", "MPG123::libmpg123")
        self.cpp_info.components["libmpg123"].names["cmake_find_package"] = "libmpg123"
        self.cpp_info.components["libmpg123"].names["cmake_find_package_multi"] = "libmpg123"
        if self.settings.os == "Windows" and self.fixed_options["shared"]:
            self.cpp_info.components["libmpg123"].defines.append("LINK_MPG123_DLL")

        self.cpp_info.components["libout123"].libs = ["out123"]
        self.cpp_info.components["libout123"].set_property("pkg_config_name", "libout123")
        self.cpp_info.components["libout123"].set_property("cmake_target_name", "MPG123::libout123")
        self.cpp_info.components["libout123"].names["cmake_find_package"] = "libout123"
        self.cpp_info.components["libout123"].names["cmake_find_package_multi"] = "libout123"
        self.cpp_info.components["libout123"].requires = ["libmpg123"]

        # Disable libsyn123 since we don't have a linux binary version for it and we don't need it
        # self.cpp_info.components["libsyn123"].libs = ["syn123"]
        # self.cpp_info.components["libsyn123"].set_property("pkg_config_name", "libsyn123")
        # self.cpp_info.components["libsyn123"].set_property("cmake_target_name", "MPG123::libsyn123")
        # self.cpp_info.components["libsyn123"].names["cmake_find_package"] = "libsyn123"
        # self.cpp_info.components["libsyn123"].names["cmake_find_package_multi"] = "libsyn123"
        # self.cpp_info.components["libsyn123"].requires = ["libmpg123"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libmpg123"].system_libs = ["m"]

            # Disable libsyn123 
            # if self.settings.arch in ["x86", "x86_64"]:
            #     self.cpp_info.components["libsyn123"].system_libs = ["mvec"]

            # hard-code libasound2 dependency
            self.cpp_info.components["libout123"].requires.append("libasound2::libasound2")
        elif self.settings.os == "Windows":
            self.cpp_info.components["libmpg123"].system_libs = ["shlwapi"]
        # add OSX support
        elif self.settings.os == "Macos":
            self.cpp_info.components["libout123"].libs.append("-Wl,-framework,AudioToolbox")

        if self.fixed_options["module"] == "libalsa":
            self.cpp_info.components["libout123"].requires.append("libalsa::libalsa")
        if self.fixed_options["module"] == "tinyalsa":
            self.cpp_info.components["libout123"].requires.append("tinyalsa::tinyalsa")
        if self.fixed_options["module"] == "win32":
            self.cpp_info.components["libout123"].system_libs.append("winmm")


        # TODO: Remove after Conan 2.x becomes the standard
        self.cpp_info.filenames["cmake_find_package"] = "mpg123"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mpg123"
        self.cpp_info.names["cmake_find_package"] = "MPG123"
        self.cpp_info.names["cmake_find_package_multi"] = "MPG123"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
