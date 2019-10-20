from setuptools import setup

setup(
   name='transax',
   version='1.0',
   description='',
   author='Scott Eisele',
   author_email='scott.r.eisele@vanderbilt.edu',
   packages=['transax'],  #same as name
   install_requires=['scipy','pycurl'], #external packages as dependencies
)