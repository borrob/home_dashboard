#!/bin/bash

pushd home_dashboard
coverage run --source=./ --branch --omit=manage.py,home_dashboard/*.py manage.py test
coverage report -m
popd
