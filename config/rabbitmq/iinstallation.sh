helm install my-rabbitmq bitnami/rabbitmq \
  --set persistence.existingClaim=rabbitmq-pvc \
  --set persistence.size=1Gi \
  --set auth.username=admin \
  --set auth.password=adminpassword \
  --set service.type=LoadBalancer \
  --set metrics.enabled=true \
  --set metrics.serviceMonitor.enabled=true \
  -n rabbitmq