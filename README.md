# Swift Version API

API for [swiftenv](https://swiftenv.fuller.li/) to return the available
versions of Swift.

An instance of the API is deployed at https://swiftenv-api.fuller.li/.

## Versions [/versions{snapshots,platform}]

Returns the available versions of Swift.

+ Parameters
    + snapshots: false (boolean) - Used to filter for snapshot versions.
    + platform: osx - Filter for versions that have binary releases for the given platform.

+ Response 200 (text/plain)

        2.2
        2.2.1

## Development Environment

You can configure a development environment with the following:

**NOTE**: *These steps assume you have Python 3.6 installed.*

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r dev-requirements.txt
```

### Running the tests

```shell
$ python -m unittest
```

### Running the development server

```shell
$ python api.py
```

### Updating versions

```shell
$ python extract.py
```
