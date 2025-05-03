# Wstęp 
Poniższe przykłady są uzupełnieniem materiałów do kursu w ramach CRC.
Są one przykładami do omawiania tworzenia różnych zasobów na kuberenetesie.

# Intro
## Pod najbardziej podstawowa jednostka
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\pod.yaml 
```
## ReplicationController(old)
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\ReplicaController.yaml 
```
## ReplicaSet
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\ReplicaSet.yaml 
```

### Zmiana z pliku yaml
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml replace -f .\intro\ReplicaSet.yaml 
```
### scalling z pliku
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml scale --replicas=4 -f .\intro\ReplicaSet.yaml 
```
### Scalling z nazwy
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml scale --replicas=3 replicaset simple-nginx-rs
```
## Deployment
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\Deployment.yaml 
```
### Zmiana deploymentu z pliku
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml replace -f .\intro\Deployment.yaml 
```
### Poprzednia replika
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml rollout undo deployment/simple-nginx-deployment
```
### Historia Rolloutów
```bash
 kubectl --kubeconfig=.\student0-kubeconfig.yaml rollout history deployment/simple-nginx-deployment
```

## Service
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\NodePort-svc.yaml 
```

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\ClusterIP-svc.yaml 
```

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\LB-svc.yaml 
```

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\intro\Ingress.yaml 
```

# Applikacja(config+secret+mount)
```bash

kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\appka\Deployment.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\appka\NodePort-svc.yaml
```

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml replace -f .\appka\Deployment.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\appka\ConfigMap.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f .\appka\Secret.yaml
```

# Warzywniak
Mamy pseudo symulację sklepu spożywczego.
Mamy API które może zapisywać zmiany magazynowe oraz drugie, które może odczytywać.
Dane trzymamy w db SQL.

Budujemy obrazy
```bash
docker build -t gadzina13/warzywniak-insert:v1 ./warzywniak/kasa
docker build -t gadzina13/warzywniak-list:v1 ./warzywniak/magazyn
```

## Deployment+PV+PVC
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/pv.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/pvc.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/deployment-kasa.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/deployment-magazyn.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/service-kasa.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s/service-magazyn.yaml
```
Stworzyliśmy sharowany dysk na którym siedzą dane.
Warto zwrócić uwagę na:
```yaml
  storageClassName: manual
  accessModes:
    - ReadWriteMany
```
`storageClassName: manual` oznacza, że sami musimy się zatroszczyc o stworzenie zasobu. Możemy zostawić puste i wtedy zostanie domyślnie utworzony(na microk8s trzeba zrobić `microk8s enable hostpath-storage`)

`accessModes` mamy opcje: `ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany` i od 1.29 `ReadWriteOncePod`

Z uwagi na to, że chcemy zapisywać pewne rzeczy to wybieramy `ReadWriteMany`. Także zarówno `PVC` jak i `PV` utworzymy jako `ReadWriteMany`. Ale nasz magazym będzie tylko odczytywał także należy odebrać mu prawa zapisu co realizujemy porpzez:

```yaml
        volumeMounts:
        - mountPath: "/data"
          name: fruits-storage
          readOnly: true
```
To `readOnly: true` załatwi sprawę.

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-singlepod/deployment-warzywniak.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-singlepod/service-warzywniak.yaml
```

```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-statefull/warzywniak-statefulset.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-statefull/service-warzywniak.yaml
```