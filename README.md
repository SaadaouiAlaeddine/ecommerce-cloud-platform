# Smart AI-based Order Management Platform

This project is a prototype using Kubernetes as platform to integrate and orchestrate all the required components to speed up orders processing and filter orders for validations using AI jobs.
## Architecture
The Lucidchart diagram is a high level picture of the different Kubernetes components organised by namespaces to separate concerns, management and enable required network policies and RBAC roles
- [@Lucidchart Diagram](https://lucid.app/lucidchart/1618b1ea-59a5-49a4-bc73-977a88aedf63/edit?viewport_loc=-1976%2C-774%2C3542%2C2093%2C0_0&invitationId=inv_d43c0486-bf91-4c1d-88d7-0739d1c7a01f) <br/>
Click on the image to open it in new tab and zoom in
![ecommerce diagram (2)](https://github.com/user-attachments/assets/8bd35352-e029-483e-b139-d5e4127e047a)
## Installation
**k is an alias for kubectl**<br/>
1) **install kind:**<br/>
   kind create cluster --config /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/kind/clusters-def.yaml
2) **install metallb**<br/>
  k create namespacemetallb-system<br/> 
  helm install metallb metallb/metallb -n metallb-system<br/> 
  **use the range from this output:**<br/>
  docker network inspect kind | grep Subnet<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/metallb/metallb-config.yaml<br/>
  **verify installation**<br/>
  kubectl get ipaddresspool -n metallb-system<br/>
  kubectl get l2advertisement -n metallb-system<br/>
3) **install nginx**
  k create namespace nginx<br/>
  k create deployment nginx --image=nginx -n nginx<br/>
  kubectl expose deployment nginx --type=LoadBalancer --port=80 --target-port=80 -n nginx<br/>

4) **install prometheus + grafana**
  k create namespace prometheus<br/>
  helm install prometheus prometheus-community/kube-prometheus-stack --namespace prometheus --set prometheus.prometheusSpec.service.type=LoadBalancer<br/>
  k patch svc prometheus-kube-prometheus-prometheus -n prometheus --type='json' -p '[{"op": "replace", "path": "/spec/type", "value": "LoadBalancer"}]'<br/>

5) **install  rabbitmq**<br/>
  helm install my-rabbitmq bitnami/rabbitmq \                                                                                                      
    --set persistence.existingClaim=rabbitmq-pvc \
    --set persistence.size=1Gi \
    --set auth.username=admin \
    --set auth.password=adminpassword \
    --set service.type=LoadBalancer \
    --set metrics.enabled=true \
    --set metrics.serviceMonitor.enabled=true \
    -n rabbitmq

6) **install cert-manager**<br/>
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

7) **install consul**<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/pv.yaml   
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/pvc.yaml  
  helm upgrade --install consul hashicorp/consul -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/values.yaml -n consul 
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/consul-mesh-gateway.yaml 

8) **install mongo**<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/mongodb
  kubectl exec -it mongodb-0 -n mongo -- mongosh
  rs.reconfig({
    _id: "rs0",
    members: [
      { _id: 0, host: "192.168.97.206:27017" },
      { _id: 1, host: "192.168.97.207:27017" }
    ]
  }, {force: true})

9) **install postgres**<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/postgres

10) **install vault**<br/>
  helm install vault hashicorp/vault \
    --namespace vault \
    --set "server.service.type=LoadBalancer" \
    --set "server.ha.enabled=false" \
    --set "server.ha.raft.enabled=false" \
    --set "server.dataStorage.enabled=true" \
    --set "server.dataStorage.size=1Gi" \
    --set "server.dataStorage.storageClass=standard" \
    --set "server.dataStorage.persistentVolumeReclaimPolicy=Delete"
  k cp key1.asc vault-0:/tmp/key1.asc -n vault
  k exec -it vault-0 -n vault -- vault operator init -key-shares=1 -key-threshold=1 -pgp-keys="/tmp/key1.asc"
  echo "encrypted unsealed key " | base64 --decode | keybase pgp decrypt
  update the bach file with VAULT_TOKEN and VAULT_ADDR
  vault operator unseal unseal_key

11) **install registry**<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/registry

12) **install redis**<br/>
  k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/redis/redis-deployment.yaml

13) **install kafka**<br/>
   helm install kafka bitnami/kafka --namespace kafka \
    --set persistence.enabled=true \
    --set persistence.size=1Gi \
    --set persistence.storageClass=manual \
    --set replicaCount=1 \
    --set service.type=LoadBalancer \
    --set externalAccess.enabled=true \
    --set externalAccess.service.type=LoadBalancer \
    --set externalAccess.service.port=9094 \
    --set externalAccess.autoDiscovery.enabled=true \
    --set rbac.create=true \
    --set controller.automountServiceAccountToken=true \
    --set broker.automountServiceAccountToken=true
  **install kafka ui:**<br/>
  docker compose up -d path-to-file

14) **install spark**<br/>
  helm install spark bitnami/spark --set service.type=LoadBalancer --namespace spark                   
  k edit statefulset spark-worker -n spark to increase cores, mem….
  retrieve the password: "$(kubectl get secret kafka-user-passwords --namespace kafka -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";

15) **install keycloak**<br/>
  helm install keycloak bitnami/keycloak -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/keycloak/values.yaml -n keycloak
  get user passsword: kubectl get secret --namespace keycloak keycloak -o jsonpath="{.data.admin-password}" | base64 --decode
  postgress passwords: kubectl get secret keycloak-postgresql -n keycloak -o yaml

16) **install install airflow**<br/>
  helm install airflow apache-airflow/airflow \
    --namespace airflow \
    --values /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/airflow/values.yaml
## Authors

- [@alaeddine saadaoui](https://github.com/SaadaouiAlaeddine)
