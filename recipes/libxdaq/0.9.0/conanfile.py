from pathlib import Path
from conan import ConanFile
from conan.tools.files import get, copy


class libxdaq(ConanFile):
    name = "libxdaq"
    version = "0.9.0"
    settings = "os", "compiler", "build_type", "arch"
    build_policy = "missing"

    def requirements(self):
        self.requires("fmt/10.2.1")
        self.requires("spdlog/1.13.0")

    def configure(self):
        pass

    def build(self):
        base_url = "https://xdaq.sgp1.cdn.digitaloceanspaces.com/libxdaq"

        _os = str(self.settings.os).lower()
        _arch = str(self.settings.arch).lower()
        url = f"{base_url}/{_os}-{_arch}-{self.version}.zip"
        get(self, url, strip_root=True)

    def package(self):
        local_bin_folder = Path(self.build_folder, "bin")
        local_include_folder = Path(self.build_folder, "include")
        local_lib_folder = Path(self.build_folder, "lib")
        copy(self, "*", local_bin_folder, Path(self.package_folder, "bin"))
        copy(self, "*", local_include_folder, Path(self.package_folder, "include"))
        copy(self, "*", local_lib_folder, Path(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xdaq")
        self.cpp_info.set_property("cmake_target_name", "xdaq::xdaq")
        self.cpp_info.set_property("cmake_build_modules", ["lib/cmake/xdaq/xdaq-variables.cmake"])
        self.cpp_info.libs = ["xdaq_device"]
        self.cpp_info.includedirs = ["include", "include/xdaq", "include/xdaq/third_party"]
        self.cpp_info.libdirs = ["lib/xdaq", "lib/xdaq/devices"]
        self.cpp_info.builddirs.append(str(Path("lib", "cmake", "xdaq")))