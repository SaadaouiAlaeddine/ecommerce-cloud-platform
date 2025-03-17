k apply -f /Users/alaeddinesaadaoui/PycharmProjects/ecommerce-cloud-platform/config/mongodb
kubectl exec -it mongodb-0 -n mongo -- mongosh

#inside the mongo pod, run the following commands
rs.initiate()
rs.reconfig({
  _id: "rs0",
  members: [
    { _id: 0, host: "192.168.97.206:27017" },
    { _id: 1, host: "192.168.97.207:27017" }
  ]
}, {force: true})
#to check the status of the replica sett
rs.status()