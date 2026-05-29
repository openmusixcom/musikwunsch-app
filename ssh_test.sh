#!/bin/bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@187.124.20.215 << 'ENDSSH'
docker ps
echo "---"
docker logs musikwunsch-api 2>&1 | tail -20
ENDSSH
