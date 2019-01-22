from setuptools import setup, find_packages

setup(name='TableDataExtractor',
      version='1.0',
      url='https://www.tabledataextractor.com',
      license='proprietary',
      author='Juraj Mavračić',
      author_email='jm2111@cam.ac.uk',
      description='Extracts data from tables',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False,
      test_suite='pytest',
      tests_require=[
            'numpy==1.15.2',
            'sympy==1.3',
            'beautifulsoup4==4.6.3',
            'requests==2.21.0',
            'selenium==3.141.0',
            'prettytable==0.7.2',
            'pandas==0.23.4'],
      install_requires=[
            'numpy==1.15.2',
            'sympy==1.3',
            'beautifulsoup4==4.6.3',
            'requests==2.21.0',
            'selenium==3.141.0',
            'prettytable==0.7.2',
            'pandas==0.23.4'])

