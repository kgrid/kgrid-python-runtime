# kgrid-python-runtime
KGrid runtime for Knowledge Objects in python


## Getting started:
- Install [Python 3.8](https://www.python.org/downloads/) or higher
- Install pip
- Run `python -m pip install kgrid-python-runtime` to download the latest package
- Create a directory called `pyshelf` in the directory the runtime will be running from.
- To start the server run `python -m kgrid_python_runtime`
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
    
- To have the runtime cache objects and only reload them from the activator if the checksum generated during packaging changes set `KGRID_PYTHON_CACHE_OBJECTS` to `true`
    
## To run the tests:
`python -m unittest discover -s tests`
    
##Creating a python Knowledge-Object:
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
