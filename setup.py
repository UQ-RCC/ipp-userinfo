import os
from setuptools import setup, find_packages

setup(
    name='ipp-userinfo',
    version='0.1',
    description='IPP userinfo resource server',
    author='Hoang Anh Nguyen',
    author_email='uqhngu36@uq.edu.au',
    url='https://github.com/UQ-RCC/ipp-userinfo',
    packages=find_packages(exclude=["test*"]),
    # data_files=[
        # ('conf', ['conf/ippuserinfo.conf'])
    # ],
    zip_safe=False,
    install_requires=[
            "fastapi==0.109.1",
            "uvicorn==0.12.2",
            "python-keycloak-client==0.2.3",
            "cowsay==3.0",
            "psycopg2-binary==2.8.6",
            "sqlalchemy==1.3.20",
            "sqlalchemy_json==0.4.0",
            "shortuuid==1.0.1",
            "python-multipart"
    ]
)
