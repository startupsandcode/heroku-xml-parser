# XML Parser for IRS Documents

To install locally:

* clone this repo
* setup a virtualenv and activate it
```
python3 -m venv venv
source venv/bin/activate
```
* Install requirements.txt
```
pip install -r requirements.txt
```
* Setup DB (I am using postgres on this one)

* Flask you DB (I love that term)
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

You will need to setup your own .env, I have included a sample.


## To Deploy to Heroku

```
heroku login
heroku create your-app
heroku config:set APP_SETTINGS=config.ProductionConfig --remote heroku
git push heroku main
```

*Note: I changed the DB to POST_DB because of an issue with Heroku, it sets up the db config url incorrectly and does not allow you to change it.
It uses a prefix of postgres rather than postgresql, simple typo, but will break your entire database. You will need to create a new environment variable on heroku for this to use the POST_DB*
