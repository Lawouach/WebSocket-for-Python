#!/bin/bash

sudo apt-get install python-dev libevent-dev cython sed

if [ ${TRAVIS_PYTHON_VERSION:0:1} == '3' ]; then
    sed -i -e 's/.*gevent*/#/' requirements.txt;
fi

if [ ${TRAVIS_PYTHON_VERSION}    == '3.3' ]; then
    sed -i -e 's/.*wsgiref.*/#/' requirements.txt;

fi

cat requirements.txt

# 3.3 kicks up a warning about cherrypy 3.2.3, but the install works
pip install -r requirements.txt
