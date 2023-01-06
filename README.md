# Helpful Scripts

## About
This repo contains scripts used to perform ad-hoc tasks relating to JIRA tickets. 

The ``/api_utils`` folder contains classes and functions interact with the apis of tools that data platform use regularly. Currently, there are classes to interact with the ``snowflake`` and ``lenses`` apis.

## Using this repo
##### 1) Clone this repo
Find the location you want to clone this repo to, and in the terminal run: 
``git clone https://github.com/richa-lad-cko/helpful-scripts.git``

##### 2) In the root folder, make a .env file with the following variables:
- ``LENSES_USERNAME="<YOUR_LENSES_USERNAME>"``: case sensitive, this can be found in lastpass or you can create a new user in the lenses UI and use these credentials instead
- ``LENSES_PASSWORD="<YOUR_LENSES_PASSWORD>"``: case sensitive, this can be found in lastpass or you can create a new user in the lenses UI and use these credentials instead
- ``ENVIRONMENT="<CHOSEN_ENVIRONMENT>"``: lower case, the environment you are working in. Can be any one of ``dev``, ``qa``, ``sbox`` or ``prod``.
- ``CLUSTER_ALIAS="<KAFKA_CLUSTER_ALIAS>"``: case sensitive, the alias of the kafka cluster you are connecting to. 
- ``SNOWFLAKE_ACCOUNT=<SNOWFLAKE_ACCOUNT>``: case sensitive, the name of the snowflake account you are using. E.g. ``checkout-checkout.privatelink``
- ``SNOWFLAKE_USER=<YOUR_SNOWFLAKE_USERNAME>``: upper case, the username you use when working in snowflake

NOTE: if you are only using one api, then you only need to create the variables relating to this api e.g. if you only wish to use the snowflake api, you only need to set ``SNOWFLAKE_ACCOUNT`` and ``SNOWFLAKE_USER``.

Once this file has been created, run the following commands in the terminal to set them:
```
set -a
source .env
set +a
```

##### 3) Create a virtual environment
Assuming you have virtualenv, run the following command in the terminal to create a virtual environment called 'venv' and then activate it:
```
virtualenv venv
source venv/bin/activate
```

##### 4) Install the requirements
Once your virtual environment is created, install the requirements by running the following command in the terminal:
``pip install -r requirements.txt``
