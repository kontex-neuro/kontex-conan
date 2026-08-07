from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get


class xdaqmetadata(ConanFile):
    name = "xdaqmetadata"
    version = "0.3.1"
    settings = "os", "compiler", "build_type", "arch"
    license = ""
    url = "https://github.com/kontex-neuro/xdaqmetadata.git"
    description = "XDAQ Video Capture Metadata (prebuilt)"
    package_type = "shared-library"
    build_policy = "missing"

    # GStreamer is NOT a Conan dependency. It is a system prerequisite installed
    # from the official gstreamer.freedesktop.org packages (runtime + devel).
    # The public header includes <gst/gstpad.h>, so consumers must have it
    # available on PKG_CONFIG_PATH. See docs/conan-publishing.md.
    _supported = {
        ("Windows", "x86_64"): "windows-x86_64",
        ("Macos", "armv8"): "macos-armv8",
    }

    def requirements(self):
        # spdlog is a private implementation dependency, but the installed
        # xdaqmetadata-config.cmake calls find_dependency(spdlog), so consumers
        # of the prebuilt package need it resolvable.
        self.requires("spdlog/1.13.0")

    def validate(self):
        key = (str(self.settings.os), str(self.settings.arch))
        if key not in self._supported:
            raise ConanInvalidConfiguration(
                f"xdaqmetadata has no prebuilt archive for {key[0]}/{key[1]}. "
                f"Supported: {sorted(self._supported)}"
            )
        if str(self.settings.build_type) not in ("Release", "Debug"):
            raise ConanInvalidConfiguration(
                "xdaqmetadata prebuilt archives exist only for Release and Debug."
            )

    def build(self):
        # Must stay identical to the KONTEX_R2_PUBLIC_BASE_URL and
        # KONTEX_R2_PACKAGE_PREFIX repository variables. This recipe is
        # source-free and cannot read them at consume time.
        base_url = "https://dl-conan.kontex.io/xdaqmetadata"
        archive = "{}-{}-{}-{}.zip".format(
            str(self.settings.os).lower(), str(self.settings.arch).lower(),
            str(self.settings.build_type).lower(), self.version,
        )
        get(self, f"{base_url}/{archive}", strip_root=True)

    def package(self):
        for folder in ("bin", "include", "lib"):
            copy(self, "*", Path(self.build_folder, folder), Path(self.package_folder, folder))

    def package_info(self):
        self.cpp_info.libs = ["xdaqmetadata"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.set_property("cmake_file_name", "xdaqmetadata")
        self.cpp_info.set_property("cmake_target_name", "xdaqmetadata::xdaqmetadata")
