#!/bin/bash

popd home_dashboard
coverage run --source=./ --branch --omit=manage.py,home_dashboard/*.py manage.py test
coverage report -m
pushd
