Conan recipe for Microsoft Speech SDK
https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/
Release notes:
https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/releasenotes?tabs=speech-sdk

Steps for integration:
Get linux client SDK
The Mac version uses a framework that needs to be installed. To work around this, we can use headers from linux version and then extract the link libraries from the Java SDK.

Source files download locations

https://aka.ms/csspeech/linuxbinary
https://aka.ms/csspeech/macosbinary
also get Java binary: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/quickstarts/setup-platform?pivots=programming-language-java&tabs=macos%2Cdebian%2Cdotnet%2Cjre%2Cgradle%2Cnodejs%2Cmac%2Cpypi
(https://azureai.azureedge.net/maven)

https://csspeechstorage.blob.core.windows.net/drop/1.24.2/SpeechSDK-Linux-1.24.2.tar.gz
https://csspeechstorage.blob.core.windows.net/drop/1.24.2/MicrosoftCognitiveServicesSpeech-MacOSXCFramework-1.24.2.zip

https://repo1.maven.org/maven2/com/microsoft/cognitiveservices/speech/client-sdk/
https://search.maven.org/artifact/com.microsoft.cognitiveservices.speech/client-sdk
https://search.maven.org/remotecontent?filepath=com/microsoft/cognitiveservices/speech/client-sdk/1.24.2/client-sdk-1.24.2.jar
https://search.maven.org/remotecontent?filepath=com/microsoft/cognitiveservices/speech/client-sdk/1.24.2/client-sdk-1.24.2-sources.jar

for code understanding: https://github.com/Microsoft/cognitive-services-speech-sdk-js

conan install speech-sdk/1.35.0@totemic/stable -s os=Linux --build=speech-sdk
