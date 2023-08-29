# Code for project



## autoscaler setup

***

**Noted: The PPA SHOWAR and LOTUS are not my work. I use the code that from their paper works. I have cited their paper in the dissertation.**

***

### GAScaler preparation

**Remember modify the Dockerfile and change the account name and address**

```bash
kubectl apply -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.1.0/cluster.yaml

chmod +x push.sh

./push.sh
```

**Apply the GAScaler to the application**

```shell
kubectl apply -f cpa.yaml
```



### SHOWAR preparation

1. **modify the config.yaml**

   in my case, I setup the experiment code on raspberry pi but I run the autoscaler on my laptop, so I used port-forward, the Kubernetes api server is localhost:8090, while you should modify to your own server url (where runs the experiment code).

2. **Remember to modify** the exp_test_deployment.yaml, you should modify these configuration which is compatible to your experiment code's configuration.

3. **Then run main.py**



### LOTUS

Set up Configuration and Deployments on Raspberry Pi

You will need to get the raw configuration file and save this in the filepath directory otherwise we will not be allowed to connect to the cluster. 

**I changed the defined linear regression model in the source code into a customized simplenn network**

And change the configuration information in the custom_controller.py and run it.

The result is printed on the workbench.

### PPA

**Remember modify the Dockerfile and change the account name and address**

```bash
chmod +x push.sh

./push.sh
```

**Apply the LOTUS to the application**

```
kubectl apply -f cpa.yaml
```



### HPA

just directly run this command to deploy hpa to statefulset

```bash
kubectl autoscale statefulset exp-test-statefulset --cpu-percent=80 --min=1 --max=10
```



## Set up the experiments

**Download this code to your environment**

https://github.com/marcel-dempers/docker-development-youtube-series

Go to the directory which includes this source code.

**Set up Prometheus**

```bash
cd monitoring\prometheus\kubernetes\1.23

kind create cluster --name monitoring --image kindest/node:v1.23.6 --config kind.yaml
kind delete cluster --name monitoring
```

```bash
docker run -it -v ${PWD}:/work -w /work alpine sh

apk add git

# clone
git clone --depth 1 https://github.com/prometheus-operator/kube-prometheus.git -b release-0.10 /tmp/

# view the files
ls /tmp/ -l

# we are interested in the "manifests" folder
ls /tmp/manifests -l

# let's grab it by coping it out the container
cp -R /tmp/manifests .

exit
```



```bash
kubectl create -f ./manifests/setup/

kubectl create -f ./manifests/

kubectl -n monitoring port-forward svc/prometheus-operated 9090
```





**Push code to docker hub**

Remember to modify the credential of K8s (the one runs your code no matter on your laptop or Raspberry Pi in this paper) to your own credential, you can check your credential and configuration information by this command.

```shell
kubectl config view --raw
```

```bash
## remember to modify the docker account
docker build -t joshuaissb/exp_test:latest .
docker push joshuaissb/exp_test:latest

```

**Apply the code to your K8s cluster**

```shell
kubectl apply -f exp_test_statefulset.yaml             
kubectl apply -f exp_test_servicemonitor.yaml
```



**Run**

Port-forward

```bash
kubectl port-forward svc/exp-test-service 8085:8085
```



**The parameter is modifiable**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"action": "increase","parameter":2048}' http://localhost:8085/trigger

curl -X POST -H "Content-Type: application/json" -d '{"action": "decrease","parameter":2048}' http://localhost:8085/trigger
```



**You can find the experiment result by doing so:**

```bash
kubectl get pods



kubectl exec -it your-experiment-pod-id -- /bin/bash

 

cat ./data/avg_rtt_history.txt
```

