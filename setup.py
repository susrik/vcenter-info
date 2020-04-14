from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name='vcenter-info',
    version="0.0.4",
    author='Erik Reid',
    author_email='nobody@nowhere.org',
    description='Simple view of vCenter data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/susrik/vcenter-info',
    packages=find_packages(),
    install_requires=[
        'pyvmomi',
        'jinja2',
        'jsonschema',
        'flask',
        'click'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'check-vcenter-vms=vcenter_info.cli:cli'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta'
    ],
    python_requires='>=3.6'
)

