from setuptools import setup, find_packages

setup(
    name='fta',
    version='0.1.0',
    author='Charlie Brown',
    author_email='stieizc.33@gmail.com',
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        fta=fta.cli:main
    ''',
    # url='',
    # license='',
    description='Block trace analyser',
    # long_description=open('README.txt').read(),
    install_requires=[
        'Click',
        'regex'
    ],
)
