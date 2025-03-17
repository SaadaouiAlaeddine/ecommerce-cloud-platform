#metallb
helm install metallb metallb/metallb -n metallb-system
k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/metallb/metallb-config.yaml