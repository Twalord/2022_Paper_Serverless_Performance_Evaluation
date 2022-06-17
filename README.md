# Performance Evaluation of Open-Source Serverless Platforms for Kubernetes (2022)

This repository contains the source code for a performance evaluation of Open-Source Serverless Platforms.
To be precise the platforms OpenFaaS (https://www.openfaas.com/) and Nuclio (https://nuclio.io/) were studied and evaluated.
Here included is the source code for two sample workloads that mimic real world use-cases.
Furthermore, it holds code for systematically running and benchmarking these workloads.

## Repository Structure

The `Function-Director` folder contains the source code for a Python program that can coordinate the invocation of
the workload on a remote Kubernetes cluster and systematically benchmark the individual runs.

The `Functions` folder contains the source code and configurations for the OpenFaaS and Nuclio functions in separate folders.
Additionally, the `baseline` folder contains the source code for a version of one of the workloads that can be executed locally 
to get comparative data for the remote tests.

The two sample workloads are an image processing task that applies a set of transformations to image files
and bytes reversal workload that reverses the order of sets of random bytes.
The image processing is commonly referred to as *magick* in the code as it uses the ImageMagick (https://imagemagick.org) library.
The bytes reversal workload is commonly referred to as *dummy* in the code.

## Related Publications

```
@mastersthesis{deckerPotentialServerlessKubernetesBased2022,
  title = {The {{Potential}} of {{Serverless Kubernetes-Based FaaS Platforms}} for {{Scientific Computing Workloads}}},
  author = {Decker, Jonathan},
  date = {2022-02-28},
  publisher = {{Göttingen Research Online / Data}},
  doi = {10.25625/6GSJSE},
  url = {https://data.goettingen-research-online.de/dataset.xhtml?persistentId=doi:10.25625/6GSJSE},
  year = 2022,
  school = {Georg-August-Universität Göttingen}
}
```

## Running the tests

### Image Test Set

The original tests used sampling images from: https://testimages.org/
The test set consisted of 960 800x800 images and 40 600x600 images from the 16BIT sampling sets:
https://sourceforge.net/projects/testimages/files/SAMPLING/16BIT/RGB/

### Baseline test

#### Building 
Requires OpenMP and ImageMagick dev to be installed.

```bash
cd Functions
cmake .
cmake --build .
```

#### Running
Place 1000 image files into the directory specified as input.

```bash
for i in {1..10}; do OMP_NUM_THREADS=16 ./baseline_test ./input/; done
```

### Platform Setup

The platform tests are coordinated by the Function-Director.

The Function-Director can test OpenFaaS and Nuclio platforms.
What platforms and what tests should be run can be configured in `Function-Director/TestRunSettings.py`.

Each platform should be deployed to a Kubernetes cluster and expose an endpoint that can be reached by
the machine running the Function-Director. The endpoint of the Kubernetes API must also be reachable by the Function-Director.

Furthermore, a container registry is required where the function images can be stored and retrieved by the respective serverless platforms.
If the container registry requires authentication, a registry secret must be created in the namespace where the serverless platform is installed.

You also need Docker to build the function images.

#### OpenFaaS

Follow the official documentation to deploy OpenFaaS in a Kubernetes cluster.
https://docs.openfaas.com/deployment/kubernetes/

The endpoint must be given in the function configurations and in the Function-Director.

Set the URL of the OpenFaaS endpoint and/or the registry url in 
```
Function-Director/Models.py
Functions/openfaas/makefile
Functions/openfaas/magick-example.yml
Functions/openfaas/magick-example-dummy.yml
Functions/openfaas/magick-example-no-processing.yml
```

Install the OpenFaaS CLI tool and make it callable as `faas`.

The kubeconfig file for the OpenFaaS Kubernetes cluster should be placed on the system as `~/.kube/config`.

To build and deploy the function images run:
```
cd Functions/openfaas
make all
```

#### Nuclio

Follow the official documentation to deploy Nuclio in a Kubernetes cluster.
https://nuclio.io/docs/latest/setup/k8s/getting-started-k8s/

Nuclio does not automatically deploy an ingress controller to allow external calls to the function endpoints so one must be added afterwards.
Follow the docs for this to deploy Traefik: https://nuclio.io/docs/latest/concepts/k8s/function-ingress/

The endpoint must be given in the function configurations and in the Function-Director.

Set the URL of the OpenFaaS endpoint and/or the registry url in 
```
Function-Director/Models.py
Functions/nuclio/Dummy/makefile
Functions/Dummy-Go/makefile
Functions/Magick/makefile
Functions/Magick-NP/makefile
```

Make sure to docker login to the target registry.
Then run this to build and push all images.
```
cd Functions/nuclio
make all
```

Note that the Nuclio Onbuild image uses the docker `onbuild` directive which triggers every time another image tries to build from it.
The directive tries to compile a Go program, however, the functions are written in C++, except for Dummy-Go.
To still allow the build to go through, the code for a hello-world program in Go is placed in each folder that gets compiled.
Later in the Dockerfile, the actual function is compiled and replaces the Go program.

The Nuclio command line tool does not correctly support updating function images.
To still allow the Function-Director to test all configurations of each function in terms of function instances,
each configuration must be deployed separately.

Deploy the functions via the Nuclio web interface.

Port-forward the interface to http://localhost:8070 via:
```bash
kubectl port-forward -n nuclio $(kubectl get pods -n nuclio -l nuclio.io/app=dashboard -o jsonpath='{.items[0].metadata.name}') 8070:8070
```

Navigate the web interface and create the functions for Nuclio.
For each entry in `Function-Director/Models.py` under `nuclio_function_dic` there should be one function.

Create the following functions:

```
image: Your Repository URL/nuclio-magick
name: magick
min-replicas: 1
max-replicas: 1
handler: ./source
```

```
image: Your Repository URL/nuclio-magick
name: magick-2
min-replicas: 2
max-replicas: 2
handler: ./source
```

And so on for magick-4, magick-8 and magick-16.

```
image: Your Repository URL/nuclio-magick-np
name: magick-np
min-replicas: 1
max-replicas: 1
handler: ./source
```

```
image: Your Repository URL/nuclio-magick-np
name: magick-np-2
min-replicas: 2
max-replicas: 2
handler: ./source
```

And so on for magick-np-4, magick-np-8, magick-np-16.

```
image: Your Repository URL/nuclio-dummy
name: dummy
min-replicas: 1
max-replicas: 1
handler: ./source
```

```
image: Your Repository URL/nuclio-dummy
name: dummy-2
min-replicas: 2
max-replicas: 2
handler: ./source
```

And so on for dummy-4, dummy-8, dummy-16.

```
image: Your Repository URL/nuclio-dummy-go
name: dummy-go
min-replicas: 1
max-replicas: 1
handler: ./handler.so
```

```
image: Your Repository URL/nuclio-dummy-go
name: dummy-go-2
min-replicas: 2
max-replicas: 2
handler: ./handler.so
```

And so on for dummy-go-4, dummy-go-8, dummy-go-16.


### Function-Director setup

The Function-Director requires the endpoints of the serverless platforms it should test to be set in 
`Function-Director/Models.py`. 

The Function-Director is run as a container that uses a volume for inputs and outputs.

The file paths for the input and outputs of every test run can be set in
`Function-Director/TestRunSettings.py`.

The volume can be created via:
`sudo docker volume create function_director_shared`

And its mount point can be found via:
`sudo docker volume inspect function_director_shared`

These are the folders used within the volume:
```
input/1kinput # For the 1000 image files
output/1koutput # Output of the same
input/8images # Small test set with 8 image files
output/8images # Output of the same
logs # Function director logs
results # Function director results
```
These directories should be created by hand and the image directories filled with image files.

Prepare the container with these commands:
```
cd Function-Director
make build
make config
```
The `make config` command moves the kubeconfig file into the container volume so 
the director can adjust the number of active function instances for OpenFaaS.

Now start the container and tests either via 
`make run` or `make start`.

After every change to the Function-Director, the container must be built again.
