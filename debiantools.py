import os
from typing import List
from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conans.client.tools.oss import get_gnu_triplet

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
    tools.download(url, filename)
    tools.check_sha256(filename, sha256)
    # extract the payload from the debian file
    conanfile.run("ar -x %s %s" % (filename, deb_data_file))
    os.unlink(filename)
    tools.unzip(deb_data_file)
    os.unlink(deb_data_file)

def triplet_name(conanfile: ConanFile, force_linux: bool=False) -> str:
    # we only need the autotool class to generate the host variable
    autotools = AutoToolsBuildEnvironment(conanfile)

    if force_linux:
        return get_gnu_triplet("Linux", str(conanfile.settings.arch), "gnu")

    # construct path using platform name, e.g. usr/lib/arm-linux-gnueabihf/pkgconfig
    # if not cross-compiling it will be false. In that case, construct the name by hand
    return autotools.host or get_gnu_triplet(str(conanfile.settings.os), str(conanfile.settings.arch), conanfile.settings.get_safe("compiler"))

def copy_cleaned(source: List[str], prefix_remove: str, dest: List[str]) -> None:
    for e in source:
        if (e.startswith(prefix_remove)):
            entry = e[len(prefix_remove):]
            if len(entry) > 0 and not entry in dest:
                dest.append(entry)

