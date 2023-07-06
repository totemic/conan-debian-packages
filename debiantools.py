import os
from typing import List
from conan import ConanFile
from conan.tools.files import download, unzip
from conan.errors import ConanException

# Fork of the private function that used to be public in Conan 1: https://github.com/conan-io/conan/issues/14230
# from conan.tools.gnu.get_gnu_triplet import _get_gnu_triplet
# https://github.com/conan-io/conan/blob/release/1.60/conan/tools/gnu/get_gnu_triplet.py
def get_gnu_triplet(os_, arch, compiler=None):
    """
    Returns string with <machine>-<vendor>-<op_system> triplet (<vendor> can be omitted in practice)

    :param os_: os to be used to create the triplet
    :param arch: arch to be used to create the triplet
    :param compiler: compiler used to create the triplet (only needed fo windows)
    """

    if os_ == "Windows" and compiler is None:
        raise ConanException("'compiler' parameter for 'get_gnu_triplet()' is not specified and "
                             "needed for os=Windows")

    # Calculate the arch
    machine = {"x86": "i686" if os_ != "Linux" else "x86",
               "x86_64": "x86_64",
               "armv8": "aarch64",
               "armv8_32": "aarch64",  # https://wiki.linaro.org/Platform/arm64-ilp32
               "armv8.3": "aarch64",
               "asm.js": "asmjs",
               "wasm": "wasm32",
               }.get(arch, None)

    if not machine:
        # https://wiki.debian.org/Multiarch/Tuples
        if os_ == "AIX":
            if "ppc32" in arch:
                machine = "rs6000"
            elif "ppc64" in arch:
                machine = "powerpc"
        elif "arm" in arch:
            machine = "arm"
        elif "ppc32be" in arch:
            machine = "powerpcbe"
        elif "ppc64le" in arch:
            machine = "powerpc64le"
        elif "ppc64" in arch:
            machine = "powerpc64"
        elif "ppc32" in arch:
            machine = "powerpc"
        elif "mips64" in arch:
            machine = "mips64"
        elif "mips" in arch:
            machine = "mips"
        elif "sparcv9" in arch:
            machine = "sparc64"
        elif "sparc" in arch:
            machine = "sparc"
        elif "s390x" in arch:
            machine = "s390x-ibm"
        elif "s390" in arch:
            machine = "s390-ibm"
        elif "sh4" in arch:
            machine = "sh4"
        elif "e2k" in arch:
            # https://lists.gnu.org/archive/html/config-patches/2015-03/msg00000.html
            machine = "e2k-unknown"

    if machine is None:
        raise ConanException("Unknown '%s' machine, Conan doesn't know how to "
                             "translate it to the GNU triplet, please report at "
                             " https://github.com/conan-io/conan/issues" % arch)

    # Calculate the OS
    if compiler == "gcc":
        windows_op = "w64-mingw32"
    elif compiler == "Visual Studio":
        windows_op = "windows-msvc"
    else:
        windows_op = "windows"

    op_system = {"Windows": windows_op,
                 "Linux": "linux-gnu",
                 "Darwin": "apple-darwin",
                 "Android": "linux-android",
                 "Macos": "apple-darwin",
                 "iOS": "apple-ios",
                 "watchOS": "apple-watchos",
                 "tvOS": "apple-tvos",
                 # NOTE: it technically must be "asmjs-unknown-emscripten" or
                 # "wasm32-unknown-emscripten", but it's not recognized by old config.sub versions
                 "Emscripten": "local-emscripten",
                 "AIX": "ibm-aix",
                 "Neutrino": "nto-qnx"}.get(os_, os_.lower())

    if os_ in ("Linux", "Android"):
        if "arm" in arch and "armv8" not in arch:
            op_system += "eabi"

        if (arch == "armv5hf" or arch == "armv7hf") and os_ == "Linux":
            op_system += "hf"

        if arch == "armv8_32" and os_ == "Linux":
            op_system += "_ilp32"  # https://wiki.linaro.org/Platform/arm64-ilp32

    return "%s-%s" % (machine, op_system)

def translate_arch(conanfile: ConanFile) -> str:
    arch_names = {
        "x86_64": "amd64",
        "x86": "i386",
        "ppc32": "powerpc",
        "ppc64le": "ppc64el",
        "armv7": "arm",
        "armv7hf": "armhf",
        "armv8": "arm64",
        "s390x": "s390x"
    }
    return arch_names[str(conanfile.settings.arch)]
    
def download_extract_deb(conanfile: ConanFile, url: str, sha256: str) -> None:
    filename = "./download.deb"
    deb_data_file = "data.tar.xz"
    download(conanfile, url, filename, sha256=sha256)
    # extract the payload from the debian file
    conanfile.run(f"ar -x {filename} {deb_data_file}")
    os.unlink(filename)
    unzip(conanfile, deb_data_file)
    os.unlink(deb_data_file)

def triplet_name(conanfile: ConanFile, force_linux: bool=False) -> str:
    if force_linux:
        return get_gnu_triplet("Linux", str(conanfile.settings.arch), "gnu")

    # conanfile.output.info(f'autotools._host: {autotools._host}, host_triplet: {conanfile.conf.get("tools.gnu:host_triplet")}')
    # conanfile.output.info(f"autotools._build: {autotools._build}")
    # conanfile.output.info(f"autotools.target: {autotools._target}")
    # conanfile.output.info(f'os={str(conanfile.settings.os)}, arch={str(conanfile.settings.arch)}, compiler={conanfile.settings.get_safe("compiler")}, get_gnu_triplet={get_gnu_triplet(str(conanfile.settings.os), str(conanfile.settings.arch), conanfile.settings.get_safe("compiler"))}')

    return get_gnu_triplet(str(conanfile.settings.os), str(conanfile.settings.arch), conanfile.settings.get_safe("compiler"))

def copy_cleaned(source: List[str], prefix_remove: str, dest: List[str]) -> None:
    for e in source:
        if (e.startswith(prefix_remove)):
            entry = e[len(prefix_remove):]
            if len(entry) > 0 and not entry in dest:
                dest.append(entry)

def remove_prefix(text: str, prefix: str) -> str:
    return text[len(prefix):] if text.startswith(prefix) else text

def copy_cleaned_no_prefix(source: List[str], prefix_remove: str, dest: List[str]) -> None:
    for e in source:
        # also remove extra /
        entry = remove_prefix(remove_prefix(e, prefix_remove), "/")
        if len(entry) > 0 and not entry in dest:
            dest.append(entry)
