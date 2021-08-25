from setuptools import find_packages
from setuptools import setup


setup(
    name='offpolicy',
    description='Off-Policy Reinforcement Learning Algorithms',
    license='MIT',
    version='0.1',
    zip_safe=True,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'tensorflow==2.5.1',
        'tensorflow-probability==0.10',
        'gym[mujoco]',
        'ray[tune]',
        'pandas',
        'matplotlib',
        'seaborn',
        'click',
        'dm-tree'])
