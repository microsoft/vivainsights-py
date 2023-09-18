# The setup.py file will contain information about the package
# specifically the name of the package, its version, platform-dependencies, etc.
from setuptools import setup, find_packages

with open('requirements.txt', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(name='vivainsights',
      version='0.2.1',
      url='https://github.com/microsoft/vivainsights',
      license= 'MIT',
      author='Martin Chan',
      author_email='martin.chan@microsoft.com',
      description='Analyze and Visualize data from Microsoft Viva Insights',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False,
      include_package_data=True,
      package_data={'vivainsights': ['data/*.csv']},
      install_requires=requirements,
      dependencies='dynamic'      
      )
