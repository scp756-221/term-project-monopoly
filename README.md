# Monopoly distributed service directory

## Directory structure

cluster: Config files of the cluster

s1: User service

s2: Music service

s3: Playlist service

db: database service

logs: where logs files are stored

loader: loader service is to insert fake data into the DynamoDB service

gatling: used to simulate various users for load test

tools: For quick scripts that are useful in make-files

## Getting started

### 1. Install Gatling

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

To generate test load on all three microservices, run:

~~~
$ ./gatling-all.sh <Number_of_service_objects> <delay_between_each_request>
~~~

For example:

~~~
$ ./gatling-all.sh 1000 300
~~~

will send 1000 requests to each of the services with a 300 ms delay. 

### 2. Adjust cluster nodes number, microservice replicas, and Dynamodb read/write capacity

The initial cluster nodes number is 2 (max 16). To adjust cluster nodes number, running:

~~~
$ eksctl scale nodegroup --name=worker-nodes --cluster aws756 --nodes <desired_nodes_number>
~~~

The initial service replicas is 1. To adjust replicas number, running:

~~~
$ kubectl scale deployment/cmpt756db --replicas=<desired_replicas_number>
$ kubectl scale deployment/cmpt756s1 --replicas=<desired_replicas_number>
$ kubectl scale deployment/cmpt756s2-v1 --replicas=<desired_replicas_number>
$ kubectl scale deployment/cmpt756s3 --replicas=<desired_replicas_number>
~~~

The initial Dynamodb capacity is 5 units, to adjust capacity, running:
~~~
$ aws dynamodb update-table --table-name <your_table_name> --provisioned-throughput ReadCapacityUnits=100,WriteC
apacityUnits=100
~~~


### 3. Stopping gatling

~~~
$ tools/kill-gatling.sh
~~~

## Kill the cluster

~~~
$ make -f eks.mak stop
~~~
