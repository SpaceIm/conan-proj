import os

from conans import ConanFile, CMake, tools

class ProjConan(ConanFile):
    name = "proj"
    description = "Cartographic Projections and Coordinate Transformations Library."
    license = "MIT"
    topics = ("conan", "dsp", "proj", "proj4", "projections", "gis", "geospatial")
    homepage = "https://proj.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("sqlite3/3.31.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PROJ_TESTS"] = False
        self._cmake.definitions["BUILD_LIBPROJ_SHARED"] = self.options.shared
        self._cmake.definitions["USE_THREAD"] = self.options.threadsafe
        self._cmake.definitions["ENABLE_LTO"] = False # let consumer set proper linker flag himself
        self._cmake.definitions["JNI_SUPPORT"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*.db",
                  src=os.path.join(self.package_folder, "share", "proj"),
                  dst=os.path.join(self.package_folder, "res"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared and self.settings.compiler == "Visual Studio":
            self.cpp_info.defines.append("PROJ_MSVC_DLL_IMPORT")
        self.env_info.PROJ_LIB.append(os.path.join(self.package_folder, "res"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
