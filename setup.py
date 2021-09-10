"""Setup file for the Python Thermotec AeroFlow® Library"""
import thermotecaeroflowflexismart
from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='thermotecaeroflowflexismart',
      version=thermotecaeroflowflexismart.__version__,
      description='Python Thermotec AeroFlow® Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/KaiGrassnick/py-thermotec-aeroflow-flexismart',
      author='Kai Grassnick',
      author_email='py-thermotec-aeroflow-flexismart@kai-grassnick.de',
      license='GNU GPLv3',
      packages=['thermotecaeroflowflexismart'],
      install_requires=["asyncio_dgram"],
      python_requires=">=3.7",
      )
