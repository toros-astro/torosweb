# TOROS website

---

# Dependencies

This website is tested for python 3.6 and Django v1.11.7.

# Initial setup for local demo

### Clone the repository
```
$ git clone git@github.com:toros-astro/torosweb.git
```

### Install the requirements, optionally on a virtual environment

    $ mkvirtualenv torosweb -p python3
    $ pip install -r requirements.txt

### Run the migrations

If you want to run the demo on a sqlite server, you can override the settings file with a local_settings module. We provide an example file in config folder:

    cp config/local_settings_debug.py config/local_settings.py

After that, migrate:

    $ ./manage.py migrate


## Create some users

Create a superuser to access the admin page

    $ ./manage.py createsuperuser
    
### Permissions:


To allow users to log in into broker you need to add them to either `broker_admins` or `telescope_operators` groups.

To allow users to be able to edit the wiki you need to add them to the `wiki_editors` group.

(These groups are created during migrations).

---
Copyright TOROS Dev team, 2017

