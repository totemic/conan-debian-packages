from conan import ConanFile
from conan.tools.files import copy, download, unzip
from pathlib import Path

required_conan_version = ">=1.53.0"

class SpeechSDKConan(ConanFile):
    name = "speech-sdk"
    version = "1.35.0"
    description = "Microsoft Speech SDK library"
    homepage = "https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/"
    url = "https://github.com/totemic/conan-package-recipes/tree/main/speech-sdk"
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
            download(self, url, filename)
            unzip(self, filename)

        elif self.settings.os == "Macos":
            filename_osx = f"{self.main_dir()}.zip"
            url_osx = f"https://csspeechstorage.blob.core.windows.net/drop/{self.version}/{filename_osx}"
            download(self, url_osx, filename_osx)
            unzip(self, filename_osx)            

            # we extract the OSX libraries from the Java library, since the regular version only contains a framework bundle
            url_java = f"https://search.maven.org/remotecontent?filepath=com/microsoft/cognitiveservices/speech/client-sdk/{self.version}/client-sdk-{self.version}.jar"
            filename_java = f"SpeechSDK-Java.zip"
            download(self, url_java, filename_java)
            unzip(self, filename_java)
        else:
            raise Exception("Binary does not exist for these settings")


    def package(self):
        copy(self, "*.txt", src=Path(self.build_folder)/self.main_dir(), dst=self.package_folder)
        copy(self, "*.md", src=Path(self.build_folder)/self.main_dir(), dst=self.package_folder)
        if self.settings.os == "Linux":
            copy(self, "*", src=Path(self.build_folder)/self.main_dir()/"include", dst=Path(self.package_folder)/"include")
            copy(self, "*", src=Path(self.build_folder)/self.main_dir()/"lib"/self.translate_arch(), dst=Path(self.package_folder)/"lib")
        elif self.settings.os == "Macos":
            headers_dir="MicrosoftCognitiveServicesSpeech.xcframework/macos-arm64_x86_64/MicrosoftCognitiveServicesSpeech.framework/Versions/A/Headers"
            copy(self, "*api_cxx*.h", src=Path(self.build_folder)/headers_dir, dst=Path(self.package_folder)/"include"/"cxx_api")
            copy(self, "*", excludes="*api_cxx*.h", src=Path(self.build_folder)/headers_dir, dst=Path(self.package_folder)/"include"/"c_api")
            # extract the OSX libraries from the Java. But don't copy the Java bindings
            copy(self, "*", excludes="*java*", src=Path(self.build_folder)/"ASSETS"/f"osx-{self.translate_arch()}", dst=Path(self.package_folder)/"lib")

    def package_info(self):
        self.cpp_info.libs = ["Microsoft.CognitiveServices.Speech.core"]
        self.cpp_info.includedirs = [
            'include',
            str(Path('include')/'c_api'),
            str(Path('include')/'cxx_api'),
        ]

        if self.settings.os == "Linux":
            self.cpp_info.libs.append("c")
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.exelinkflags.append('-framework AudioToolbox')
            self.cpp_info.exelinkflags.append('-framework IOKit')
            self.cpp_info.exelinkflags.append('-framework CoreFoundation')
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
