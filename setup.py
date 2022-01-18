# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 00:19:53 2022

@author: asheesh Janda
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coarseclassevaluator",                     # This is the name of the package
    version="1.1",                        # The initial release version
    author="Asheesh Janda",                     # Full name of the author
    author_email='asheesh.janda.ds@gmail.com',
    description="CoarseClassvisual formulator",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], # Information to filter the project on PyPi website
    project_urls={
    'Source': 'https://github.com/AsheeshJandaDS/coarseclassvisual',
    'Tracker': 'https://github.com/AsheeshJandaDS/coarseclassvisual/issues',
},                                     
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["coarseclassevaluator"],             # Name of the python package
    package_dir={'':'src'},     # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)