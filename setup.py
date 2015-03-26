from setuptools import setup, find_packages

setup(
    name='bta',
    version='0.1.0',
    entry_points='''
        [console_scripts]
        bta=main:main
    ''',
    author='Charlie Brown',
    author_email='stieizc.33@gmail.com',
    packages=find_packages(),
    # url='',
    # license='',
    description='Block trace analyser',
    # long_description=open('README.txt').read(),
    install_requires=[
        'Click',
        'regex'
    ],
)
