from os.path import join

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy

class Exocortic(ConanFile):
    name = 'exocortic'
    version = '0.0.1'

    # enforce full mode when resolving dependencies
    package_id_non_embed_mode = "full_mode"
    package_id_unknown_mode = "full_mode"

    settings = 'os', 'compiler', 'build_type', 'arch'

    exports_sources = (
        'CMakeLists.txt',
        'cmake/*',
        'tools/*',
        )

    requires = (
        'lyric/0.0.1',
        'tempo/0.0.1',
        'zuri/0.0.1',
        )

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['EXOCORTIC_VERSION'] = self.version
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target='package')

    def package(self):
        copy(self, 'exocortic-*', self.build_folder, join(self.package_folder, 'dist'))
