# Catalog Web Application - Udacity 5th Project
Flask driven Catalog App for Udacity's 5th project.

### Some of the features:
- oAuth2.0 Google and FB login system
- SQLAlchemy handling of DB
- Flask framework
- Bootstraps

### Files and directories:
1. Static directory - for .css and .js 
2. Templates directory - for .html files
3. JSON files - for Google and FB authentication
4. db_setup.py, db_populate.py - for creating and populating DB
5. itemscatalog.db - file representing the DB
6. application.py for running the app


# RUNNING
In order for everyone to simulate the same environment we use vagrant and virtual box.

## INSTALLATION 
  1. Download Vagrant and Virtual Box
  2. Download or clone Github Repo
  3. Python has to be installed on your computer. For details visit https://www.python.org/downloads/. 
    3.1. This project uses Python 2.7
  
## Executing the program
1. Navigate to the vagrant environment with this project already included

2. Run vagrant up and then vagrant ssh

3. Inside the project folder, run database.py to create the database using python database.py

4. (Optional, if you want to start from scratch, remove itemscatalog.db) Populate the database with categories by running db_populate.py 

5. Run application.py and navigate to localhost:8000 in your browser

## To-Do 
1. Finish placement of the sign/in FB/Google buttons.
2. Re-do the login check according to reviewer's comments:
  It is good that your are checking for User Authentication in all your CRUD function. However, you would have noticed that you are repeating this line of code in all your CRUD functions.

> You can create a decorator function that you can use to check for user login status without having to repeat the same line of code in > areas that need to check for the login status. Decorators help you avoid DRY (Do Not Repeat Yourself) situations, makes your code less > bulky, and more attractive. Interestingly, we have the [Flask Login decorator](http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/). Please check that out.

3. Front-End styling needs more work.
4. Remodel the forms using flask_wtf FORMs - more info at [.TeamTreeHouse](https://teamtreehouse.com/library/build-a-social-network-with-flask/takin-names/registration-view).

## Contact
For any questions please feel free to contact me:<br />
mikael.janek@gmail.com
