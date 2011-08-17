from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

modules = [
    Extension('Config', sources=['cXdg/Config.pyx']),
    Extension('BaseDirectory', sources=['cXdg/BaseDirectory.pyx']),
    Extension('DesktopEntry', sources=['cXdg/DesktopEntry.pyx']),
    Extension('Exceptions', sources=['cXdg/Exceptions.pyx']),
    Extension('IconTheme', sources=['cXdg/IconTheme.pyx']),
    Extension('IniFile', sources=['cXdg/IniFile.pyx']),
    Extension('Locale', sources=['cXdg/Locale.pyx']),
    Extension('Menu', sources=['cXdg/Menu.pyx']),
    Extension('MenuEditor', sources=['cXdg/MenuEditor.pyx']),
    Extension('Mime', sources=['cXdg/Mime.pyx']),
    Extension('RecentFiles', sources=['cXdg/RecentFiles.pyx'])
]

setup(
    name = 'cXdg',
    cmdclass = {'build_ext': build_ext},
    ext_package = 'cXdg',
    ext_modules = modules
)
