# Use the following command to build the image:
# sudo docker build -t kgrid/pythonruntime .

# Use the following command to run the image on Linux:
# sudo docker run --network host kgrid/pythonruntime

# Use the following command to run the image on Windows:
# docker run -it -p :5000:5000 -e KGRID_PROXY_ADAPTER_URL=http://host.docker.internal:8080 kgrid/pythonruntime

FROM python:3.9.4-alpine3.13
MAINTAINER kgrid (kgrid-developers@umich.edu)

RUN ["python", "-m", "pip", "install", "--upgrade", "--no-cache-dir", "kgrid-python-runtime"]

CMD ["python", "-m", "kgrid_python_runtime"]
