k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/pv.yaml
k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/pvc.yaml
helm upgrade --install consul hashicorp/consul -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/values.yaml -n consul
k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/consul/consul-mesh-gateway.yaml