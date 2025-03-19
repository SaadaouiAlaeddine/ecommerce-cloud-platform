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
## Components

### $${\color{red}Consul}$$ <br/>
- Consul is deployed to enable service discoverability
<img width="1231" alt="Screenshot 2025-03-19 at 7 37 27 AM" src="https://github.com/user-attachments/assets/ea7ef003-e50b-49b0-bdc6-2c31554ca0a3" /><br/>
- Intentions are created to define access between microservices
<img width="1237" alt="Screenshot 2025-03-19 at 7 42 23 AM" src="https://github.com/user-attachments/assets/f18b2221-c65b-430d-916b-2e661b176080" />

### $${\color{red}Keycloak}$$ <br/>
- Keycloak is installed to define an identity layer for microservices to enable authentication and authorization features
<img width="1249" alt="Screenshot 2025-03-19 at 8 09 41 AM" src="https://github.com/user-attachments/assets/b6e069a6-5ddf-40ed-8d3a-b19146f776c1" />
<img width="1046" alt="Screenshot 2025-03-19 at 8 09 49 AM" src="https://github.com/user-attachments/assets/e838bd33-dbfc-445e-b1aa-812185d4a440" /><br/>

- Scopes are required to define the required jwt entries, in this case the audience and roles are required to connect later on with vault
<img width="1255" alt="Screenshot 2025-03-19 at 8 10 18 AM" src="https://github.com/user-attachments/assets/0005ab62-f14f-45d9-a792-d8a146313557" />
<img width="1271" alt="Screenshot 2025-03-19 at 8 10 30 AM" src="https://github.com/user-attachments/assets/3995d5a2-fd62-4f1c-8a5e-7d0f09311d1e" /><br/>

- Realm Roles with associated Client Roles are required to define the resource_access section in jwt
<img width="1271" alt="Screenshot 2025-03-19 at 8 10 56 AM" src="https://github.com/user-attachments/assets/5e5295ec-a2b7-4eae-b897-0fa58d4f0827" />
<img width="1258" alt="Screenshot 2025-03-19 at 8 11 04 AM" src="https://github.com/user-attachments/assets/ff0a8b1d-8763-4abc-b488-5cc5036c827c" /><br/>

- The generated JWT contains the client scope and access_token using the client's credentials
<img width="936" alt="Screenshot 2025-03-19 at 8 12 10 AM" src="https://github.com/user-attachments/assets/252f98c1-4c7b-4f3b-977b-a1a12a21fbaa" /><br/>

- The decoded access token contains aud, resources_access and scope entries passed to vault to access microservice secrets
<img width="579" alt="Screenshot 2025-03-19 at 10 15 32 AM" src="https://github.com/user-attachments/assets/90156fbf-f839-4a58-b21d-3c9d5b410b72" /><br/>

- The generated JWT is signed using R256 algorithm, the kid entry will be used to fetch the public key from the keycloak certification entries<br/>
<img width="569" alt="Screenshot 2025-03-19 at 10 16 11 AM" src="https://github.com/user-attachments/assets/fd894148-612d-4584-ac14-8d29efa61038" /><br/>

- To enable JWT signature, a provided was added to the Keycloak realm with a generated certificate and private key
<img width="1254" alt="Screenshot 2025-03-19 at 8 24 52 AM" src="https://github.com/user-attachments/assets/db8d0831-4103-4e41-baeb-7ec3aa1743dd" /><br/>

- Using the same certificate and private key, we can verify the signature of JWT using jwt.io
<img width="1224" alt="Screenshot 2025-03-19 at 8 27 12 AM" src="https://github.com/user-attachments/assets/7b95fa7b-3510-4100-95f8-1afd811f74ee" /><br/>

- At the code level, the kid entry will be used to fetch the public key from the Keycloak certs page
<img width="565" alt="Screenshot 2025-03-19 at 8 40 43 AM" src="https://github.com/user-attachments/assets/32c3f2ce-6c35-4fd1-92f7-720e1ca54fdf" />
<img width="1559" alt="Screenshot 2025-03-19 at 8 43 13 AM" src="https://github.com/user-attachments/assets/84cea0b6-2662-429e-a1d0-af8d1f6558e7" /><br/>

## Authors

- [@alaeddine saadaoui](https://github.com/SaadaouiAlaeddine)
