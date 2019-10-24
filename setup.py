import setuptools

setuptools.setup(
    name='r2c_flake8_requests',
    version='0.0.1',
    description='r2c checks for requests',
    author='grayson',
    author_email='grayson@r2c.dev',
    package_dir={'': 'src/'},
    packages=['r2c_flake8_requests'],
    entry_points={
        'flake8.extension': [
            'R2C701=r2c_flake8_requests.no_auth_over_http:NoAuthOverHttp',
            'R2C702=r2c_flake8_requests.use_timeout:UseTimeout',
            'R2C703=r2c_flake8_requests.use_scheme:UseScheme',
        ],
    },
)