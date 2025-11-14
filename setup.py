"""
Setup configuration for FATE Secure Function Component
"""

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Read version
about = {}
with open(
    os.path.join(here, "fate_secure_func", "__version__.py"), "r", encoding="utf-8"
) as f:
    exec(f.read(), about)

# Read README
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fate-secure-func",
    version=about["__version__"],
    description="Secure Function Computation Component for FATE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Iotsp Laboratory",
    author_email="iotsp@example.com",
    url="https://github.com/iotsp/fate-secure-func",
    license="MIT",
    packages=find_packages(exclude=["examples", "examples.*"]),
    # Include non-Python files
    include_package_data=True,
    package_data={
        "fate_secure_func_client": ["component_define/*.yaml"],
    },
    # Dependencies
    install_requires=[
        "pyfate>=2.2.0",  # FATE framework
        "torch>=1.13.0",  # PyTorch (used in guest implementation)
    ],
    # Entry points: Register FATE component
    entry_points={
        "fate.ext.component_desc": [
            "secure_func = fate_secure_func.secure_func:secure_func",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering",
    ],
)
