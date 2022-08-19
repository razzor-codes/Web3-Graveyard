from setuptools import setup
import os
import io
here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


setup(
    name='gravedigger',
    version='0.1.0',
    description='Web3 Graveyard Interaction Tool',
    url='https://github.com/razzor-codes/Web3-Graveyard',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Razzor',
    license='Apache License 2.0',
    python_requires = '>=3.6.0',
    packages=['gravedigger'],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        gravedigger=gravedigger.main:cli
    ''',
    zip_safe=False
)