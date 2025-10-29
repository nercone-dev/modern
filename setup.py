from setuptools import setup, find_packages

setup(
    name='nercone-modern',
    version='1.0.0',
    packages=find_packages(),
    description='Nercone Modern is a simple package for logging and progress bar and More!',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nercone',
    author_email='nercone@diamondgotcat.net',
    url='https://github.com/DiamondGotCat/Modern',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)