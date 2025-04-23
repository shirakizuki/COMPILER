from setuptools import setup, find_packages

setup(
    name="mini-compiler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mini-compiler=compiler.main:main",
        ],
    },
) 