
import os
from os import path
from io import open
from setuptools import setup, find_packages, Extension

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    INSTALL_REQUIRES = f.read().split('\n')

# Get VERSION from the VERSION file
with open(path.join(HERE, 'VERSION'), encoding='utf-8') as f:
    PACKAGE_VERSION = f.read().rstrip()


setup(
    name='cherrant',

    version=PACKAGE_VERSION,

    description='Chinese ERRANT',

    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    url='https://github.com/yuhuang-cst/cherrant',

    author='Yu Huang',

    author_email='yuhuang-cst@foxmail.com',

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='',  # Optional

    packages=find_packages(exclude=[
        'contrib',
        'docs',
        ]),  # Required

    python_requires='>=3.6, <4',

    install_requires=[] + INSTALL_REQUIRES,  # Optional

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': [
            'coverage',
            'pytest',
            'pylint',
        ],
    },

    package_data={  # Optional
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/yuhuang-cst/cherrant/issues',
        'Source': 'https://github.com/yuhuang-cst/cherrant',
    },
    include_package_data=True,
)
