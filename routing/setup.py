from distutils.core import setup, Extension

module1 = Extension('gisutil',
                    sources = ['gisutil.c'],
                    extra_compile_args = ["-std=c99"])

setup (name = 'gisutil',
       version = '.1',
       description = 'GIS utilities package.',
       ext_modules = [module1])

# module1 = Extension('quadtree',
#                     sources = ['quadtree.c'],
#                     extra_compile_args = ["-std=c99"])

# setup (name = 'quadtree',
#        version = '1.0',
#        description = 'This is a quadtree package',
#        ext_modules = [module1])
