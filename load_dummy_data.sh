#!/bin/bash

#Insert fixtures
echo "Executing load_fixtures.sh in docker container"
docker exec q-task-django-api sh load_fixtures.sh
