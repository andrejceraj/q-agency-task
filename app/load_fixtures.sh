#!/bin/bash

#Insert fixtures
echo "Loading fixtures into db"
python manage.py loaddata ./products/fixtures/*
