# setup.py
from setuptools import setup, find_packages

setup(
    name="analizador_legislativo",
    version="0.1",
    packages=find_packages(include=['analizador_legislativo', 'analizador_legislativo.*']),
    package_dir={'': 'src'}  # Añade esta línea
)