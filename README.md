# Project:  Catalog App

Catalog App project, part of the Udacity [Full Stack Web Developer
Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## Description
The Catalog App provides a list of items (Applications) within a variety of categories (Application Categories). The categories are based on application categories from the [Google Play Store](https://play.google.com/store/apps).

A set of API endpoints are provided with JSON formatted responses. See the API endpoint table for more information.

Users can add, update and delete items once authenticated through Googles authentication system. * Note a user can only perform these actions on items they own.

## Required

- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

## How to setup and run the project
1. Download and install Vagrant and VirtualBox.
1. Download this preconfigured virtual machine [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm/archive/master.zip)
1. After unziping the virtual machine, move this directory under the /vagrant directory (like: /vagrant/catalog).

Launch the Vagrant VM from inside the `/vagrant` folder with:

```bash
$ vagrant up
```

Once Vagrant installs the necessary files, execute the following to access the VM.
```bash
$ vagrant ssh
```

Then move to the catalog folder. 

```bash
$ cd /vagrant/catalog
```

Create the database
```bash
$ python database_setup.py
```

Populate the database with some initial data
```bash
$ python init_data.py
```
Run the application.
```bash
$ python application.py
```

Open your web browser to this URL: http://localhost:8000

----

## Resources
- [Python](https://www.python.org/)
- [Flask](http://flask.pocoo.org) 
- [SQLAlchemy](http://www.sqlalchemy.org)
- [Google OAuth2](https://developers.google.com/identity/protocols/OAuth2)
- [Bootstrap](https://getbootstrap.com/)
- [jQuery](https://jquery.com/)

## API endpoints
| Request | Methods | What you get | 
| ------------- |-------------|---------|
| /catalog.json | GET | All categories with their items. |
| /api/v1/catalog | GET | All categories with their items. |
| /api/v1/categories | GET | All categories. |
| /api/v1/category/*<category_id>* | GET | All items in a specific category. |
| /api/v1/item/*<item_id>* | GET | A specific item. |