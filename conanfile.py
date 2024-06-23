from os.path import join

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy

class XocoDist(ConanFile):
    name = 'xoco-dist'
    version = '0.0.1'

    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {'shared': [True, False], 'compiler.cppstd': ['17', '20'], 'build_type': ['Debug', 'Release']}
    default_options = {'shared': True, 'compiler.cppstd': '20', 'build_type': 'Debug'}

    exports_sources = (
        'CMakeLists.txt',
        'cmake/*',
        'tools/*',
        )

    requires = (
        'chord/0.0.1',
        'lyric/0.0.1',
        'tempo/0.0.1',
        'zuri/0.0.1',
        )

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['XOCO_DIST_VERSION'] = self.version
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.build(target='package')

    def package(self):
        copy(self, 'xoco-dist-*', join(self.build_folder, 'dist'), join(self.package_folder, 'dist'))
