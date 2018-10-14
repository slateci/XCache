SERV="http://localhost:80"
SERV="http://192.170.227.234:80"

# path/filename/client/origin
curl -X GET "$SERV/path/AOD.root/MWT2/BNL"
curl -X GET "$SERV/path/AOD.root/AGLT2/BNL"
curl -X GET "$SERV/path/AOD.root/MWT2/CERN"


echo "delete server."
curl   -X DELETE "$SERV/server/xc_MWT2_0" 

echo "create server."
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @server_0.json

echo "update server."
curl  --header "Content-Type: application/json" -X POST "$SERV/update_server" -d @server_1.json


echo "delete server."
curl   -X DELETE "$SERV/server/xc_test_123" 

echo "making server tree"
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_MWT2_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_MWT2_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_MWT2_2.json


curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_AGLT2_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_AGLT2_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_AGLT2_2.json


curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_MW_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_MW_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_MW_2.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_MW_3.json

curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_BNL_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_BNL_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_BNL_2.json

curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_SWT2_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_SWT2_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_SWT2_2.json

curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_SW_0.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_Sw_1.json
curl  --header "Content-Type: application/json" -X POST "$SERV/add_server" -d @xc_Int2T_SW_2.json