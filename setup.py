from setuptools import find_packages, setup

setup(
    name='hotel-california-slack',
    version='0.1',
    description='Welcome to the Hotel California. '
                'You can check out any time you like, but you can never leave!',
    license='MIT',
    install_requires=[
        'slackclient'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hotel-california-slack=hotel_california_slack:main',
        ],
    }
)
