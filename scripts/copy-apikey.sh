#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json recommendations:/home/vscode 
docker exec recommendations sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"
