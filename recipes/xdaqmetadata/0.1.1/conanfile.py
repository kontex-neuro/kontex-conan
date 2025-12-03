from pathlib import Path
from conan import ConanFile
from conan.tools.gnu import PkgConfig
from conan.tools.files import get, copy


class xdaqmetadata(ConanFile):
    name = "xdaqmetadata"
    version = "0.1.1"
    settings = "os", "compiler", "build_type", "arch"
    license = ""
    url = "https://github.com/kontex-neuro/xdaqmetadata.git"
    description = "XDAQ Video Capture Metadata"
    build_policy = "missing"

    def requirements(self):
        self.requires("fmt/10.2.1")
        self.requires("spdlog/1.13.0")

    def build(self):
        base_url = "https://xdaq.sgp1.digitaloceanspaces.com/xdaqmetadata"

        _os = str(self.settings.os).lower()
        _arch = str(self.settings.arch).lower()
        url = f"{base_url}/{_os}-{_arch}-{self.version}.zip"
        get(self, url, strip_root=True)

    def package(self):
        local_include_folder = Path(self.build_folder, "include")
        local_lib_folder = Path(self.build_folder, "lib")
        copy(self, "*", local_include_folder, Path(self.package_folder, "include"))
        copy(self, "*", local_lib_folder, Path(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["xdaqmetadata"]
        pkg_config = PkgConfig(self, "gstreamer-codecparsers-1.0")
        self.cpp_info.includedirs.extend(pkg_config.includedirs)
        self.cpp_info.libdirs.extend(pkg_config.libdirs)
        self.cpp_info.libs.extend(pkg_config.libs)
