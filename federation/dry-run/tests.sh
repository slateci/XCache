# path/filename/client/origin
curl -X GET "localhost:8080/path/AOD.root/MWT2/BNL"
curl -X GET "localhost:8080/path/AOD.root/AGLT2/BNL"
curl -X GET "localhost:8080/path/AOD.root/MWT2/CERN"


echo "delete server."
curl   -X DELETE "localhost:8080/server/xc_MWT2_0" 

echo "create server."
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @server.json

echo "update server."
curl  --header "Content-Type: application/json" -X POST "localhost:8080/update_server" -d @server1.json

