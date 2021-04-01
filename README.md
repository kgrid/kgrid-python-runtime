# KGrid Python Runtime
A KGrid runtime for Knowledge Objects in a native python environment that connects to an activator using the proxy adapter.

## Prerequisites:
- [Python](https://www.python.org/downloads/) 3.8 or higher
- [pip](https://pip.pypa.io/en/stable/installing/)

## Installation:
- Run `python -m pip install kgrid-python-runtime` to download the latest package
- Create a directory called `pyshelf` in the directory the runtime will be running from.
- Run `python -m kgrid_python_runtime` to start the runtime
  
## Configuration:
Set these environment variables to customize your runtime's settings.

###`KGRID_PYTHON_ENV_URL`
- The address of this environment that the activator will use to communicate with it. 
- Default value: `http://localhost`
  
###`KGRID_PYTHON_ENV_PORT`
- The port this environment is available on.
- Default value:`5000`

###`KGRID_PROXY_ADAPTER_URL`
- The url of the adapter this runtime will communicate with 
- Default value:`http://localhost:8080`

- By default, the python runtime will tell the Kgrid Activator that it is started at `http://localhost:5000`.

  
###`KGRID_PYTHON_CACHE_STRATEGY`
- The caching strategy of this runtime. It can take three values: `never`, `always`, or `use_checksum`
    - `never` - existing objects from the activator are overwritten on every activation call.
    - `always` - existing objects stored in the runtime will never be re-downloaded from the activator and the local pyshelf and context.json files must be deleted and the runtime restarted for the objects to be replaced.
    - `use_checksum` - objects will look for a checksum in the deployment descriptor sent over during activation and only re-download the object if that checksum has changed.
- Default value: `never`

###`KGRID_PROXY_HEARTBEAT_INTERVAL`
- The frequency (in seconds) at which the runtime will ping the activator and attempt to reconnect if the connection has been broken. Can be set to any value above 5 seconds or 0 to disable the heartbeat.
- Default value:`30`

### `DEBUG`
- Changes the logging level to debug, takes a boolean `true`/`false`
- Default: `false`

## Creating a python Knowledge Object:
Just like other knowledge objects, python objects have 4 basic parts: 
service.yaml, deployment.yaml, metadata.txt, 
and a payload that can be any number of python files.

The packaging spec for knowledge objects can be found [here](https://kgrid.org/specs/packaging.html).

If your python package requires other python packages, 
simply specify them in a file called `requirements.txt` 
at the root of your object:
```
package-name=0.1.5
other-package-name=1.3.5
third-package-name=1.5.4
```

That's it! as long as the payload is written in valid python, 
and the object is built to the spec, you're ready to go.
An example python object can be found in the example collection:
[python/simple/v1.0](https://github.com/kgrid-objects/example-collection/releases/latest/download/python-simple-v1.0.zip)


# For Developers
## To run the app:
Clone this project and set the environment variable: `PYTHONPATH` to the project root.

Example (Ubuntu): `export PYTHONPATH=~/Projects/kgrid-python-runtime`

Run `python kgrid_python_runtime/app.py runserver` from the top level of the project.

    
## Important Notes
- Editing the cache directly from the runtime's shelf will
not propagate changes to the endpoints in the runtime. New
KOs must come from the activator.

- The runtime will attempt to load any Knowledge Objects that 
were previously loaded onto its shelf before registering with 
the activator and acquiring its objects. The shelf directory can 
be deleted if there is a need to get all objects fresh from the activator.