import os
import shutil

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import download, unzip, check_sha1


class libxvc(ConanFile):
    name = "libxvc"
    version = "0.2.1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/kontex-neuro/libxvc.git"
    description = "Thor Vision Video Capture library"
    options = {"build_testing": [True, False]}
    default_options = {"build_testing": False}

    def source(self):
        zip_name = f"v{self.version}.tar.gz"
        download(
            self, f"https://github.com/kontex-neuro/libxvc/archive/{zip_name}", zip_name
        )
        # Recommended practice, always check hashes of downloaded files
        # check_sha1(self, zip_name, "8d87812ce591ced8ce3a022beec1df1c8b2fac87")
        unzip(self, zip_name)
        
        extracted_folder = f"libxvc-{self.version}"
        for item in os.listdir(extracted_folder):
            shutil.move(os.path.join(extracted_folder, item), item)
        os.rmdir(extracted_folder)
        os.unlink(zip_name)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25.0 <3.30.0]")
        self.tool_requires("ninja/[>=1.12.0]")
        if self.options.build_testing:
            self.test_requires("catch2/3.8.0")
            self.test_requires("gtest/1.14.0")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("fmt/10.2.1")
        self.requires("spdlog/1.13.0")
        self.requires("nlohmann_json/3.11.3")
        self.requires("cpr/1.10.5")
        self.requires("xdaqmetadata/0.1.1")
        self.requires("openssl/3.4.1")
        self.requires("cli11/2.5.0")

    def configure(self):
        # Enable required Boost modules
        self.options["boost/*"].with_atomic = True
        self.options["boost/*"].with_system = True
        self.options["boost/*"].with_filesystem = True
        self.options["boost/*"].with_program_options = True
        # Configure Boost options for GitHub Actions build
        self.options["boost/*"].with_stacktrace_backtrace = False
        self.options["boost/*"].without_stacktrace = True
        self.options["boost/*"].without_locale = True
        # List of Boost modules to disable for faster build speed
        disable_for_build_speed = (
            "charconv",
            "chrono",
            "cobalt",
            "container",
            "context",
            "contract",
            "coroutine",
            "date_time",
            "exception",
            "fiber",
            "graph",
            "graph_parallel",
            "iostreams",
            "json",
            "log",
            "math",
            "mpi",
            "nowide",
            "python",
            "random",
            "regex",
            "serialization",
            "test",
            "thread",
            "timer",
            "type_erasure",
            "url",
            "wave",
        )
        for opt in disable_for_build_speed:
            setattr(self.options["boost/*"], f"without_{opt}", True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generator = "Ninja"
        tc.variables["BUILD_TESTING"] = self.options.build_testing
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libxvc"]
