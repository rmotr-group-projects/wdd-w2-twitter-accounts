#!/usr/bin/env bash

function usage {
  echo "Usage: ./setup_venv PROJECT_NAME"
}

if [ -z "$1" ]; then
    echo "Error: You need to provide your project's name"
    usage
    exit 1
fi
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: There's no active virtualenv"
    usage
    exit 1
fi

project_name=$1

ACTIVATE_PATH=$VIRTUAL_ENV/bin/postactivate
DEACTIVATE_PATH=$VIRTUAL_ENV/bin/postdeactivate

# Postactivate
echo "export OLD_PYTHONPATH=\${PYTHONPATH}" >> $ACTIVATE_PATH
echo "export PYTHONPATH=${project_name}:\${PYTHONPATH}" >> $ACTIVATE_PATH
echo "export DJANGO_SETTINGS_MODULE=${project_name}.settings" >> $ACTIVATE_PATH

# Postdeactivate
echo "unset DJANGO_SETTINGS_MODULE" >> $DEACTIVATE_PATH
echo "export PYTHONPATH=\${OLD_PYTHONPATH}" >> $DEACTIVATE_PATH
echo "unset OLD_PYTHONPATH" >> $DEACTIVATE_PATH
