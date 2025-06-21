from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="farmpower_backend_v2",
    version="0.1.0",
    packages=find_packages(include=['app*', 'middleware*', 'models*', 'schemas*', 'routers*']),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=required,
    python_requires='>=3.10',
)
