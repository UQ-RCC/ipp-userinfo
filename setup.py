import os
from setuptools import setup

setup(
    name='ipp-userinfo',
    version='0.1',
    description='IPP userinfo resource server',
    author='Hoang Anh Nguyen',
    author_email='uqhngu36@uq.edu.au',
    url='https://github.com/UQ-RCC/ipp-userinfo',
    packages=[
        'userinfo',
        'userinfo.routers',
    ],
    data_files=[
        ('/etc/ipp/conf/ippuserinfo.conf', ['conf/ippuserinfo.conf'])
    ],
    zip_safe=False,
    install_requires=[
            "fastapi==0.61.2",
            "uvicorn==0.12.2",
            "python-keycloak-client==0.2.3",
            "cowsay==2.0.3"
    ]
)
