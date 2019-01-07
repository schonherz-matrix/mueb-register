import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mueb_register",
    version="0.0.1",
    author="Zsombor Bodnár",
    author_email="bodnar.zsombor@simonyi.bme.hu",
    description="App for registering MUEBs with QR code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.sch.bme.hu/matrix-group/dhcp/matrix-dhcp-tools",
    packages=setuptools.find_packages(),
    install_requires=[
        'qrcode',
        'pillow'
    ],
    entry_points = {
        'console_scripts': ['mueb_register=mueb_register.MRegister:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)