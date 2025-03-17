 helm install spark bitnami/spark --set service.type=LoadBalancer --namespace spark
 kubectl edit statefulset spark-worker -n spark to increase cores, mem….
password: "$(kubectl get secret kafka-user-passwords --namespace kafka -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";