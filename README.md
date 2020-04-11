# vcenter-info - Simple view of vCenter data

* [Overview](#overview)
* [Package-based Installation](#package-based-installation)
  * [From PyPI](#from-pypi)
  * [From Source](#from-source)
* [Running](#running)
  * [Configuration](#configuration)
  * [Starting the Server](#starting-the-server)
* [Development Environment](#development-environment)
  * [Setup](#setup)
  * [Generate Javascript Bundle](#generate-javascript-bundle)

## Overview

This project is used for making some simple
queries to one or more vCenter host and rendering
the results in a simple way.  It's also a
sample project for serving a npm-managed React
app with Flask.
 
## Package-based installation

Create a (python 3) virtualenv and
install using one of the following methods:

### From PyPi

```bash
$ pip install vcenter-info
```

### From Source

```bash
$ python setup.py sdist
$ pip install dist/vcenter-info-x.y.z.tar.gz
```

# Running

## Configuration

Use `config-example.json` as a template to
create a configuration file.
When running the server an environment variable called
`CONFIG_FILENAME` and containing the path to this
configuration file must be present.

## Starting the Server

```bash
CONFIG_FILENAME=config.json FLASK_APP=vcenter_info flask run
```

Note: if you are running from a source distribution
and didn't install it in your virtualenv, you should
execute the above from the top-level folder.

Alternatively, using the provided `app.py`
might sometimes be convenient when developing:

```bash
CONFIG_FILENAME=config.json python vcenter_info/app.py
```

or:

```bash
CONFIG_FILENAME=config.json python -m vcenter_info.app
```


## Development Environment

These notes are for setting up a development environment.

### Setup

Create a (python 3) virtualenv and install the requirements:

```bash
$ pip install -e .
```

... and, to install additional libraries used by the test scripts:

```bash
$ pip install -r requirements.txt
```

Set up the node environment:

```bash
npm install
```

### Generate Javascript Bundle

In a fresh environment, or whenever the ui
sources are changed:

```bash
npm run build
```

