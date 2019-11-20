import setuptools

setuptools.setup(
    name='flake8_requests',
    version='0.1.0',
    description='r2c checks for requests',
    author='grayson',
    author_email='grayson@r2c.dev',
    package_dir={'': 'src/'},
    packages=['flake8_requests'],
    entry_points={
        'flake8.extension': [
            'R2C701=flake8_requests.no_auth_over_http:NoAuthOverHttp',
            'R2C702=flake8_requests.use_timeout:UseTimeout',
            'R2C703=flake8_requests.use_scheme:UseScheme',
        ],
    },
)