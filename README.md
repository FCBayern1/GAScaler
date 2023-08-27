# GAScaler
GAScaler used the genetic algorithm to get the pod numbers to scale



### Pack autoscaler 

**Remember modify the Dockerfile and change the account name and address**

```bash
kubectl apply -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/v1.1.0/cluster.yaml

chmod +x push.sh

./push.sh
```



### Set up the experiments

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
cd exp_test_pi
chmod +x push.sh
./push.sh

```

**Apply the code to your K8s cluster**

```shell
kubectl apply -f exp_test_statefulset.yaml             
kubectl apply -f exp_test_servicemonitor.yaml
```



**Apply the GAScaler to the application**

```shell
cd ..
kubectl apply -f cpa.yaml
```



**Run**

Port-forward

```bash
kubectl port-forward svc/exp-test-service 8085:8085
```



The parameter is modifiable

```bash
curl -X POST -H "Content-Type: application/json" -d '{"action": "increase","parameter":1024}' http://localhost:8085/trigger

curl -X POST -H "Content-Type: application/json" -d '{"action": "decrease","parameter":1024}' http://localhost:8085/trigger
```

