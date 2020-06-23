from setuptools import setup, find_packages

setup(name='TableDataExtractor',
      version='1.5.9',
      url='https://www.tabledataextractor.com',
      license='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License',
      author='Juraj Mavračić',
      author_email='jm2111@cam.ac.uk',
      description='Extracts data from tables',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md', 'r', encoding='utf-8').read(),
      zip_safe=False,
      test_suite='unittest',
      tests_require=[
            'django>2.1.6',
            'numpy==1.16',
            'sympy',
            'beautifulsoup4==4.6.3',
            'requests==2.21.0',
            'selenium==3.141.0',
            'prettytable==0.7.2',
            'pandas==0.23.4'],
      install_requires=[
            'django>2.1.6',
            'numpy==1.16',
            'sympy',
            'beautifulsoup4==4.6.3',
            'requests==2.21.0',
            'urllib3==1.24.2',
            'selenium==3.141.0',
            'prettytable==0.7.2',
            'pandas==0.23.4'])

