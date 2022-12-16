#!/bin/bash

set -e 

# The lambda runtime is Python 3.9, so we require a build that
# uses that version.
REQUIRED_PY_VERSION="3.9"
PY_VERSION=$(python3 -c "import sys; v=sys.version_info;print(f'{v.major}.{v.minor}')")
if [ $PY_VERSION != $REQUIRED_PY_VERSION ]; then
    echo "We require Python 3.9. You have $PY_VERSION"
    exit 1;
fi

mkdir lambda_distribution
cp -r ../application/* lambda_distribution/  
cd lambda_distribution

# Create a python virtual environment,
# activate it, and install the dependencies
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Now deactivate the virtualenv
deactivate

# zip the packages:
cd venv/lib/python3.9/site-packages
zip -r ../../../../lambda.zip .

# move up to the lambda_distribution root:
cd ../../../../
zip -rg lambda.zip \
    aws_lambda_handler.py \
    trut_main.py \
    testosterone_model_spec.json \
    src

# move the archive out of the lambda_distribution directory 
# and return to the terraform folder (where this script lives)
mv lambda.zip ../
cd ..

# clean up
rm -rf lambda_distribution
