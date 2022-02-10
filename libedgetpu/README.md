# libedgetpu

## Package creation

To test the creation of a package locally using a step-by-step approach, run the following steps:

```shell
# Get dependencies, set target version/user, set settings/options/profiles
conan install . <version>@totemic/stable -if build --build=outdated [--profile=<profile> --profile:build=default]

# Fetch source and apply patches
conan source . -if build -sf source

# Build targets
conan build . -bf build -sf source -pf package

# Package headers, libs, binaries ...
conan package . -bf build -sf source -pf package
```
you can then inspect the contents of the package by browsing the `package` folder.

Alternatively, you can build the package in one step with the following single command:
```shell
# Create package with specified version/user and settings/options/profiles
conan create . <version>@totemic/stable --build=outdated [--profile=<profile> --profile:build=default]
```

The `conan create` command shares the same options as the `conan install` but runs the build within the
local conan cache under `~/.conan/data/<package>/<version>/<user>/<channel>`, and because of this reason you don't
need to specify folder paths

Note: when cross-compiling, [it's common practice to specify a build profile](https://docs.conan.io/en/latest/systems_cross_building/cross_building.html#using-a-profile),
otherwise the host profile will be used for build tools as well, which is not desired as
they should run on the build machine

## Examples

```shell
# Build for local machine
conan create . grouper@totemic/stable --build=outdated

# Build against specific tensorflow-lite version
conan create . grouper@totemic/stable --build=outdated --require-override tensorflow-lite/2.8.0

# Cross compile package (remember to specify build profile too)
conan create . grouper@totemic/stable --build=outdated --profile=armv8-cc --profile:build=default
```