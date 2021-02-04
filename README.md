# kgrid-python-runtime
KGrid runtime for Knowledge Objects in python


## Getting started:
- Install [Python 3.8](https://www.python.org/downloads/) or higher
- Install pip
- Run `python -m pip install kgrid-python-runtime` to download the latest package
- Create a directory called `pyshelf` in the directory the runtime will be running from.
- To start the server run `python -m kgrid_python_runtime`
  
### Configuration
- If this runtime will not be running locally, you must specify the address with `KGRID_PYTHON_ENV_URL`. 
This will be the address given to the Kgrid Activator upon activation.
- The runtime starts on port 5000, but can be specified with `KGRID_PYTHON_ENV_PORT`
- By default, the python runtime points to a Kgrid activator at url: 
    `http://localhost:8080`.
    
    This can be customized by setting the environment variable:
    `KGRID_PROXY_ADAPTER_URL`
- By default, the python runtime will tell the Kgrid Activator that it is started at `http://localhost:5000`.
    
    If you're starting the runtime at a different address, that url must be specified by setting the environment variable:
    `KGRID_PYTHON_ENV_URL`
  
- The `KGRID_PYTHON_CACHE_STRATEGY` can take three values: `never`, `always`, or `use_checksum`

    - `never` or if no value is set means that existing objects will be overwritten whenever objects are re-downloaded from the activator.
    - `always` means that existing objects stored in the python runtime will never be re-downloaded from the activator and the local pyshelf and context.json files must be deleted and the runtime restarted for the objects to be replaced.
    - `use_checksum` means that objects will look for a checksum in the deployment descriptor sent over during activation and only re-download the object if that checksum has changed.
- To enable automatic discovery and registration with the activator, set `KGRID_PROXY_HEARTBEAT_INTERVAL` to a value greater than 5.

## Creating a python Knowledge-Object:
Just like other knowledge objects, python objects have 4 basic parts: 
service.yaml, deployment.yaml, metadata.txt, 
and a payload that can be any number of python files.

The packaging spec for knowledge objects can be found [here](https://kgrid.org/specs/packaging.html).

If your python package requires other python packages, 
simply specify them in a file called `requirements.txt` 
at the root of your object thusly:
```
package-name=0.1.5
other-package-name=1.3.5
third-package-name=1.5.4
```

That's it! as long as the payload is written in valid python, 
and the object is built to the spec, you're ready to go.
An example python object can be found in the 
[example collection](https://github.com/kgrid-objects/example-collection/releases/download/4.0.0/python-simple-v1.0.zip)


# For Developers
## To run the app:
Run `python kgrid_python_runtime/app.py runserver` from the top level of the project.
## To run the tests:
`python -m unittest discover -s tests`
    
## Important Notes
- Editing the cache directly from the runtime's shelf will
not propagate changes to the endpoints in the runtime. New
KOs must come from the activator.

- The runtime will attempt to load any Knowledge Objects that 
were previously loaded onto its shelf before registering with 
the activator and acquiring its objects. The shelf directory can 
be deleted if there is a need to get all objects fresh from the activator.