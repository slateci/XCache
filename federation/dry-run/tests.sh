# path/filename/client/origin
curl -X GET "localhost:8080/path/AOD.root/MWT2/BNL"
curl -X GET "localhost:8080/path/AOD.root/AGLT2/BNL"
curl -X GET "localhost:8080/path/AOD.root/MWT2/CERN"


echo "delete server."
curl   -X DELETE "localhost:8080/server/xc_MWT2_0" 

echo "create server."
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @server_0.json

echo "update server."
curl  --header "Content-Type: application/json" -X POST "localhost:8080/update_server" -d @server_1.json

echo "making server tree"
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_MWT2_0.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_MWT2_1.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_MWT2_2.json


curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_AGLT2_0.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_AGLT2_1.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_AGLT2_2.json


curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_Int2T_MW_0.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_Int2T_MW_1.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_Int2T_MW_2.json
curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_Int2T_MW_3.json

curl  --header "Content-Type: application/json" -X POST "localhost:8080/add_server" -d @xc_BNL_0.json