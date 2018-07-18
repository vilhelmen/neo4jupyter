from setuptools import setup

setup(
    name='neo4jupyter',
    version='0.1.1',
    keywords='jupyter neo4j graphdb',
    url='https://github.com/merqurio/neo4jupyter',
    license='MIT',
    author='Gabriel de Maeztu',
    author_email='gabriel.maeztu@gmail.com',
    packages=['neo4jupyter'],
    package_dir={'neo4jupyter': '.'},
    description='A neo4j visualizer for Jupyter',
    long_description='To be done',
    install_requires=[
        'IPython >= 4.0.0',
        'ipython-cypher >= 0.2.4',
        'py2neo'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
