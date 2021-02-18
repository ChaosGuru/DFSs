from setuptools import setup

setup(
    name='client_kun',
    version='0.1',
    py_modules=['client_kun'],
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        client-kun=client_kun:dfs
    '''
)