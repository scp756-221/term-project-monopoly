# Monopoly distributed service directory

## Directory structure
Cluster: Config files of the cluster
s1: User service
s2: Music service
s3: Playlist service
db: database service
mcli: music service cli
logs: where logs files are stored
loader: loader service is to insert fake data into the DynamoDB service
gatling: used to simulate various users for load test
tools: For quick scripts that are useful in make-files

## Getting started

### 1. Install dependencies
Gatling: (https://gatling.io/open-source/start-testing/)

### 2. Instantiate the template files

Fill in all the required values in `tpl-vars-tpl.txt` and save it as `tpl-vars.txt`.

### 3. Instantiate the templates

Once you have filled in all the details, run

~~~
$ make -f k8s-tpl.mak templates
~~~

### 4. Login the container

~~~
$ tools/shell.sh
~~~

## Deployments

This section assumes that all steps in the getting started section has been complete.

### 1. Set up EKS Cluster

Create a cluster with 2 nodes:

~~~
$ make -f eks.mak start
~~~

You could view the cluster with:

~~~
$ kubectl config get-contexts
~~~

### 2. Create namespace for the cluster

~~~
$ kubectl create ns c756ns
$ kubectl config set-context aws756 --namespace=c756ns
~~~

### 3. Provision the cluster

~~~
$ make -f k8s.mak provision
~~~

### 4. Load the fake table to Dynamodb

~~~
$ make -f k8s.mak loader
~~~

This inserts data that exists in gatling/resources/*.csv into their respective tables

### 5. Ensure AWS DynamoDB is accessible/running

Check that you have the necessary tables installed by running

~~~
$ aws dynamodb list-tables
~~~

The resulting output should include tables `User`, `Music`, and `Playlist`.

## Monitoring tools

### 1. Grafana

To print the grafana URL, run:

~~~
$ make -f k8s.mak grafana-url
~~~

Click the URL and you could login Grafana with 
username: admin
password: prom-operator

Select “Browse” from the left menu. This will bring up a list of dashboards. Click on c756 transactions and you could see the dashboard like below:
![image](https://user-images.githubusercontent.com/97763994/162276198-5b012d89-bc0d-44d0-98ec-c925e3ee571b.png)


### 2. Kiali

To print the Kiali URL, run:

~~~
$ make -f k8s.mak kiali-url
~~~

### 3. Prometheus

To print the Prometheus URL, run:

~~~
$ make -f k8s.mak prometheus-url
~~~

## Gatling load test 

### 1. Simulate load

To generate test load on all three applications, run:

~~~
$ ./gatling-all.sh <Number_of_service_objects> <delay_between_each_request>
~~~

For example:

~~~
$ ./gatling-all.sh 1000 300
~~~

will send 1000 requests to each of the services with a 300 ms delay. 

### 2. Stopping gatling

~~~
$ tools/kill-gatling.sh
~~~

## Kill the cluster

~~~
$ make -f eks.mak stop
~~~

---

## Reference

This is the tree of this repo. 


The CI material at `ci` and `.github/workflows` are presently designed for Assignment 7 and the course's operation. They're not useable for you and should be removed. If you are ambitious or familiar with GitHub action, the one flow that may be _illustrative_ is `ci-to-dockerhub.yaml`. **It is not directly useable as you team repo will not use templates.**
```
├── ./.github
│   └── ./.github/workflows
│       ├── ./.github/workflows/ci-a1.yaml
│       ├── ./.github/workflows/ci-a2.yaml
│       ├── ./.github/workflows/ci-a3.yaml
│       ├── ./.github/workflows/ci-mk-test.yaml
│       ├── ./.github/workflows/ci-system-v1.1.yaml
│       ├── ./.github/workflows/ci-system-v1.yaml
│       └── ./.github/workflows/ci-to-dockerhub.yaml
├── ./ci
│   ├── ./ci/v1
│   └── ./ci/v1.1
```

Be careful to only commit files without any secrets (AWS keys). 
```
├── ./cluster
```

These are templates for the course and should be removed.
```
├── ./allclouds-tpl.mak
├── ./api-tpl.mak
├── ./az-tpl.mak
│   ├── ./ci/create-local-tables-tpl.sh
│   │   ├── ./ci/v1/compose-tpl.yaml
│       ├── ./ci/v1.1/compose-tpl.yaml
│   ├── ./cluster/awscred-tpl.yaml
│   ├── ./cluster/cloudformationdynamodb-tpl.json
│   ├── ./cluster/db-nohealth-tpl.yaml
│   ├── ./cluster/db-tpl.yaml
│   ├── ./cluster/dynamodb-service-entry-tpl.yaml
│   ├── ./cluster/loader-tpl.yaml
│   ├── ./cluster/s1-nohealth-tpl.yaml
│   ├── ./cluster/s1-tpl.yaml
│   ├── ./cluster/s2-dpl-v1-tpl.yaml
│   ├── ./cluster/s2-dpl-v2-tpl.yaml
│   ├── ./cluster/s2-nohealth-tpl.yaml
│   ├── ./cluster/tpl-vars-blank.txt
│   ├── ./db/app-tpl.py
├── ./eks-tpl.mak
│   ├── ./gcloud/gcloud-build-tpl.sh
│   └── ./gcloud/shell-tpl.sh
├── ./gcp-tpl.mak
├── ./k8s-tpl.mak
├── ./mk-tpl.mak
│   │   ├── ./s2/standalone/README-tpl.md
│   │   └── ./s2/standalone/unique_code-tpl.py
│   │   └── ./s2/v1/unique_code-tpl.py
```

Support material for using this repo in the CSIL lab.
```
├── ./csil-build
```

The core of the microservices. `s2/v1.1`, `s2/v2`, and `s2/standalone`  are for use with Assignments. For your term project, work and/or derive from the `v1` version.
```
├── ./db
├── ./s1
├── ./s2
│   ├── ./s2/standalone
│   │   ├── ./s2/standalone/__pycache__
│   │   └── ./s2/standalone/odd
│   ├── ./s2/test
│   ├── ./s2/v1
│   ├── ./s2/v1.1
│   └── ./s2/v2
```

`results` and `target` need to be created but they are ephemeral and do not need to be saved/committed.
```
├── ./gatling
│   ├── ./gatling/resources
│   ├── ./gatling/results
│   │   ├── ./gatling/results/readmusicsim-20220204210034251
│   │   └── ./gatling/results/readusersim-20220311171600548
│   ├── ./gatling/simulations
│   │   └── ./gatling/simulations/proj756
│   └── ./gatling/target
│       └── ./gatling/target/test-classes
│           ├── ./gatling/target/test-classes/computerdatabase
│           └── ./gatling/target/test-classes/proj756
```

Support material for using this repo with GCP (GKE).
```
├── ./gcloud
```

A small job for loading DynamoDB with some fixtures.
```
├── ./loader
```

Logs files are saved here to reduce clutter.
```
├── ./logs
```

Assignment 4's CLI for the Music service. It's non-core to the Music microservices. At present, it is only useable for the Intel architecture. If you are working from an M1 Mac, you will not be able to build/use this. The workaround is to build/run from an (Intel) EC2 instance.
```
├── ./mcli
```

Deprecated material for operating the API via Postman.
```
├── ./postman
```

Redundant copies of the AWS macros for the tool container. You should use the copy at [https://github.com/overcoil/c756-quickies](https://github.com/overcoil/c756-quickies) instead.
```
├── ./profiles
```

Reference material for istio and Prometheus.
```
├── ./reference
```

Assorted scripts that you can pick and choose from:
```
└── ./tools
```
