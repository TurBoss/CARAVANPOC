# TO BUILD, RUN:
# caravan_exe.py py2exe

from distutils.core import setup
from py2exe.build_exe import py2exe
import os, sys
sys.path.append("panels")

class Py2exe(py2exe):

    def initialize_options(self):
        # Add a new "upx" option for compression with upx
        py2exe.initialize_options(self)
        self.upx = 0

    def copy_file(self, *args, **kwargs):
        # Override to UPX copied binaries.
        (fname, copied) = result = py2exe.copy_file(self, *args, **kwargs)

        basename = os.path.basename(fname)
        if (copied and self.upx and
            (basename[:6]+basename[-4:]).lower() != 'python.dll' and
            fname[-4:].lower() in ('.pyd', '.dll',)):
            os.system('upx --best "%s"' % os.path.normpath(fname))
        return result

    def patch_python_dll_winver(self, dll_name, new_winver=None):
        # Override this to first check if the file is upx'd and skip if so
        if not self.dry_run:
            if not os.system('upx -qt "%s" >nul' % dll_name):
                if self.verbose:
                    print "Skipping setting sys.winver for '%s' (UPX'd)" % \
                          dll_name
            else:
                py2exe.patch_python_dll_winver(self, dll_name, new_winver)
                # We UPX this one file here rather than in copy_file so
                # the version adjustment can be successful
                if self.upx:
                    os.system('upx --best "%s"' % os.path.normpath(dll_name))

#import py2exe as mod
#help(mod)
#raw_input()

setup(
    
    cmdclass = {"py2exe": Py2exe},
        
    windows = [
                {
                    "script":   "caravan.py",
                    "icon_resources": [(1, "caravan.ico")],

                    "dest_base": "Caravan",
                }
            ],
    
    options = {
                "py2exe": 
                {
                    #"packages": "wx",
                    #"optimize": 2,
                    #"compressed": 2,
                    #"bundle_files": 1,
                    "skip_archive": 1,
                    #"packages": "PIL",
                },
                
            },
    
    data_files = [
        ("", [
            
            "68k.xml",
            "sf2data.dat",
            "alpha.png",

            "caravan.ico",
            "terrain_lowsky.ico",
            "terrain_plains.ico",
            "terrain_road.ico",
            "terrain_grass.ico",
            "terrain_hill.ico",
            "terrain_forest.ico",
            "terrain_desert.ico",
            "terrain_sky.ico",
            "terrain_water.ico",
            "terrain_blocked.ico",
        ]),
    ],
    
    #zipfile = None,
    
    )