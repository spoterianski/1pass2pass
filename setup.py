from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='1pass2pass',
    version='0.0.3',
    description='Utility for transfer items from the 1password (*.1pif files) to the pass',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Sergey Poterianski',
    author_email='spoterianski@gmail.com',
    license='MIT',
    requires=['loguru'],
    install_requires=['loguru'],
    url='https://github.com/spoterianski/1pass2pass',
    download_url='https://github.com/spoterianski/1pass2pass/tarball/v0.0.3',
    scripts=['bin/1pass2pass'],
    keywords= ("1pass2pass", "1password", "pass"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        "Environment :: Console"
    ],
    python_requires='>=3.6'
)
