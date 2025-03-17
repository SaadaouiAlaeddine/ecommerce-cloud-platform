helm install prometheus prometheus-community/kube-prometheus-stack --namespace prometheus --set prometheus.prometheusSpec.service.type=LoadBalancer

kubectl patch svc prometheus-kube-prometheus-prometheus -n prometheus --type='json' -p '[{"op": "replace", "path": "/spec/type", "value": "LoadBalancer"}]'