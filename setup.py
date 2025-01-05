from setuptools import setup, find_packages

setup(
    name="dtn-simulator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'networkx',
        'matplotlib',
        'numpy',
        'seaborn',
        'pandas'
    ]
)
