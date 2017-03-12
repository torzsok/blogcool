from setuptools import setup

setup(
    name='blogcool',
    packages=['blogcool'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-restful',
        'peewee',
        'flask_jsonpify'
    ]
)
