# kgrid-python-runtime
KGrid runtime for Knowledge Objects in python

Getting started:
- Install Python 3.8 or higher
- Install pip
- Download Kgrid Python Runtime from github
- Navigate to the folder containing `app.py`
- In a terminal, install the required dependencies with:

    `pip install -r requirements.txt`
- To start the Python runtime:

    `python app.py runserver`
    
- The runtime starts on port 5000, but can be specified with ___________
- By default, the python runtime points to a Kgrid activator at url: 
    `http://localhost:8080`
    
    This can be customized by setting the environment variable:
    `KGRID_ADAPTER_PROXY_URL`
- By default, the python runtime will tell the Kgrid Activator that it is started at `http://localhost:5000`.
    
    If you're starting the runtime at a different address, that url must be specified by setting the environment variable:
    `ENVIRONMENT_SELF_URL`