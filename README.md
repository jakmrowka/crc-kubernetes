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
Także mamy jedno miejsce gdzie jest baza danych i mozemy z wielu podów tam zapisywać jak i odczytywać.

## Single Pod - stateless
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-singlepod/deployment-warzywniak.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-singlepod/service-warzywniak.yaml
```
Tutaj mamy skompresowane do 1 Poda w którym siedzi zarówno zapis jak i odczyt. Ale jeżeli pod się wywróci tracimy dane. Do tego każda baza żyje swoim życiem w przypadku replik>1. Nie ma synchronizacji.

## Statefull
```bash
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-statefull/warzywniak-statefulset.yaml
kubectl --kubeconfig=.\student0-kubeconfig.yaml apply -f warzywniak/k8s-statefull/service-warzywniak.yaml
```
Tutaj mamy to samo co w Single pod, ale mamy tworzenie automatycznego PVC, ale każdy pod ma własny PVC. Jakie są róznice względem deplyoment + PVC:
* Nazewnictwo:
  * Deployment ma losowe: `app-gjdfngfnh` 
  * StatefulSet ma narastajace: `app-0`
* PVC:
  * Deployment: robimy manualnie
  * StatefulSet: automatycznie przez `volumeClaimTemplates`
* Użycie PV:
  * Deployment: sharuje jeden na wszystkie
  * StatefulSet: osobny per pod
* volumeClaimTemplates:
  * Deployment: zmieniasz jak chcesz
  * StatefulSet: Nie możesz zmienić po utworzeniu StatefulSeta
* usuwanie danych(wartości defaultowe):
  * Deployment: `ReclcaimPolicy: Retain` nawet jak usuniesz PV to dane zostają, trzeba manualnie usunąć dane
  * StatefulSet: `ReclcaimPolicy: Delete` dane giną po usunięciu PVC

# Helm
zarządzanie deplyomentem:
```bash
kubectl apply -f warzywniak/k8s/ --kubeconfig=./student0-kubeconfig.yaml
```
```bash
kubectl delete -f warzywniak/k8s/ --kubeconfig=./student0-kubeconfig.yaml
```
W taki sposób możemy tworzyc i usuwać "złożone" wdrożenia, ale:
* jeżeli mamy cokolwiek zmienić np port to trzeba wiedzieć gdzie to zmienić
* jeżeli chcesz powielić to samo ale np na innyp adresie to musisz zmieniać metadata
* dodać zależności
To trzeba się sporo napracować, albo można użyć Helm i problemy powyższe zostaną rozwiązane przez:
* `values.yaml`
* `helm install NAZWA` poprzez `{{ .Release.Name }}`
* `dependencies`

Budujemy obraz
```bash
docker build -t gadzina13/frontend-secret-viewer:latest ./helm/src
```
Instalujemy
```bash
helm install viewer ./helm/helm-secret-viewer --kubeconfig=./student0-kubeconfig.yaml
```
Odinstalowujemy
```bash
helm uninstall viewer --kubeconfig=./student0-kubeconfig.yaml
```
Zmieniamy
```bash
helm upgrade viewer ./helm/helm-secret-viewer --kubeconfig=./student0-kubeconfig.yaml
```

# Cron
```bash
kubectl apply -f ./crony/cron.yaml --kubeconfig=./student0-kubeconfig.yaml
```