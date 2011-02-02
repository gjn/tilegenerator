from setuptools import setup, find_packages
import sys, os

import tileforge

setup(name='tileforge',
      version=tileforge.__version__,
      description="",
      long_description="",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS",
      ],
      # keywords='',
      author='Camptocamp SA',
      # author_email='',
      # url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      tests_require=["nose"],
      test_suite="nose.collector",
      zip_safe=False,
      install_requires=[
#        "TileCache", "boto", "tempita", "pyproj", "cloudfiles"
        "TileCache", "boto", "tempita", "pyproj"
      ],
      entry_points={
        "console_scripts": ["tilemanager = tileforge.bin.tilemanager:main",
                            "wmts_capability = tileforge.utils.wmts:main"]
      },
      )
