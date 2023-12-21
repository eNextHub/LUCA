from setuptools import setup, find_packages

setup(
    name='LUCA',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pint',
    ],
    entry_points={
        'console_scripts': [
            'fuel_context=LUCA.fuel_context:main',
        ],
    },
    author='Nicolò Golinucci',
    author_email='nicolo.golinucci@enextgen.it',
    description='Repository to create a pint-importabile historical memory of prices, heat powers, density of commodities.',
    url='https://github.com/eNextHub/LUCA',
)