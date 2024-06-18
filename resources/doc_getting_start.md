# Personal Healthcare Management System (PHMS)

PHMS written in xx. Use Bootstrap CSS.

# IMPORTANT

Important files to get started:
- `.env` file that contains API keys and passwords to database
- Currently support up to `python-3.10.11`
- Please turn off your code formatter (eg. Prettier) as it will mess up the Jinja2 code

## Setting up your repo
```
git clone
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask run --reload
```

## Start project in localhost
```
venv\Scripts\activate
flask run --reload
```

## To start EC2 server
- Run AWS
- ssh into the 'phms_ubuntu_2204'
- cd PHMS
- source venv/bin/activate
- flask run --reload --host 0.0.0.0
- at browser, go to 'http://44.207.83.243:5000/'

## To deploy changes in EC2 Server
- Run AWS Learner Lab
- cd PHMS
- git pull (to get the latest git repository)
- flask run --reload --host 0.0.0.0

## Update dependencies (when new package is added)

```
pip freeze > requirements.txt
```

## DANGER
to delete all data from postgreql
```
select 'drop table "' || tablename || '" cascade;' from pg_tables;
```

## To add a recommendations type into PHMS
1. go to PHMS\integrations\nlg\insight_types.py
2. name a type of recommendations, put in data needed, and prompts