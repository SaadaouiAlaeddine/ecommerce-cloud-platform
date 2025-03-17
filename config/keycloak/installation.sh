helm install keycloak bitnami/keycloak -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/keycloak/values.yaml -n keycloak
get user passsword: kubectl get secret --namespace keycloak keycloak -o jsonpath="{.data.admin-password}" | base64 --decode
postgress passwords: kubectl get secret keycloak-postgresql -n keycloak -o yaml