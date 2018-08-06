#!/bin/bash

version=$(git describe --long --always)
sed -i 'bak' "s/VERSION = .*$/VERSION = '${version}'/" home_dashboard/home_dashboard/settings.py
rm -f home_dashboard/home_dashboard/settings.pybak
