import os
from conans import AutoToolsBuildEnvironment, CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class SpeechSDKConan(ConanFile):
    name = "SpeechSDK"
    version = "1.24.2"
    description = "Microsoft Speech SDK library"
    homepage = "https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/"
    license = "Microsoft"
    settings = "os", "arch"

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libasound2/1.1.8@totemic/stable")

    def translate_arch(self) -> str:
        arch_names = {
            "x86_64": "x64",
            "x86": "x86",
            "armv7": "arm32",
            "armv7hf": "arm32",
            "armv8": "arm64"
        }
        return arch_names[str(self.settings.arch)]

    # the name of the directory after uncompressing
    def main_dir(self):
        if self.settings.os == "Linux":
            return f"SpeechSDK-Linux-{self.version}"
        elif self.settings.os == "Macos":
            return f"MicrosoftCognitiveServicesSpeech-MacOSXCFramework-{self.version}"
        else:
            return "unsupported"

    def build(self):
        if self.settings.os == "Linux" and self.translate_arch():
            filename = f"{self.main_dir()}.tar.gz"
            url = f"https://csspeechstorage.blob.core.windows.net/drop/{self.version}/{filename}"
            tools.download(url, filename)
            tools.unzip(filename)

        elif self.settings.os == "Macos":
            filename_osx = f"{self.main_dir()}.zip"
            url_osx = f"https://csspeechstorage.blob.core.windows.net/drop/{self.version}/{filename_osx}"
            tools.download(url_osx, filename_osx)
            tools.unzip(filename_osx)            

            # we extract the OSX libraries from the Java library, since the regular version only contains a framework bundle
            url_java = f"https://search.maven.org/remotecontent?filepath=com/microsoft/cognitiveservices/speech/client-sdk/{self.version}/client-sdk-{self.version}.jar"
            filename_java = f"SpeechSDK-Java.zip"
            tools.download(url_java, filename_java)
            tools.unzip(filename_java)
        else:
            raise Exception("Binary does not exist for these settings")


    def package(self):
        self.copy(pattern="*.txt", src=f"{self.main_dir()}", symlinks=True)
        self.copy(pattern="*.md", src=f"{self.main_dir()}", symlinks=True)
        if self.settings.os == "Linux":
            self.copy(pattern="*", dst="include", src=f"{self.main_dir()}/include", symlinks=True)
            self.copy(pattern="*", dst="lib", src=f"{self.main_dir()}/lib/{self.translate_arch()}", symlinks=True)
        elif self.settings.os == "Macos":
            headers_dir="MicrosoftCognitiveServicesSpeech.xcframework/macos-arm64_x86_64/MicrosoftCognitiveServicesSpeech.framework/Versions/A/Headers"
            self.copy(pattern="*api_cxx*.h", dst="include/cxx_api", src=headers_dir, symlinks=True)
            self.copy(pattern="*", excludes="*api_cxx*.h", dst="include/c_api", src=headers_dir, symlinks=True)
            # extract the OSX libraries from the Java. But don't copy the Java bindings
            self.copy(pattern="*", dst="lib", src=f"ASSETS/osx-{self.translate_arch()}", excludes="*java*", symlinks=True)

    def package_info(self):
        self.cpp_info.libs = ["Microsoft.CognitiveServices.Speech.core"]
        self.cpp_info.includedirs = [
            'include',
            os.path.join('include', 'c_api'),
            os.path.join('include', 'cxx_api'),
        ]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("c")
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.exelinkflags.append('-framework AudioToolbox')
            self.cpp_info.exelinkflags.append('-framework IOKit')
            self.cpp_info.exelinkflags.append('-framework CoreFoundation')
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
