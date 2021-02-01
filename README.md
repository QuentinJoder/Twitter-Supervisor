# Twitter-Supervisor
> "I made this program to learn about Python and to know who stop following me on Twitter." - Quentin JODER 

Twitter Supervisor informs you (via direct message) when someone follows or unfollows you. You can set it up to delete
your old tweets, retweets and favorites.

Important: currently, Twitter Supervisor cannot work if your account has more than 5000 followers. Compatibility with
"bigger" accounts might be added in the future.

Twitter-Supervisor is a [Flask](https://flask.palletsprojects.com/) app using [tweepy](https://www.tweepy.org/) to access the Twitter API. It uses [Flask-APScheduler](https://github.com/viniciuschiele/flask-apscheduler)
to manage periodic tasks.

![Build and Test](https://github.com/QuentinJoder/Twitter-Supervisor/workflows/build-and-test/badge.svg?branch=master)

## Requirements
* **Python 3.7 to 3.9** (and **pip**): older versions are not tested and don't work because the app uses
[dataclasses](https://docs.python.org/fr/3/library/dataclasses.html), a feature introduced in Python 3.7.

* **A Twitter developer account** (a Standard one is good enough), you can apply [here](https://developer.twitter.com/en/apply-for-access).


## How to run the app ?

### Twitter Developer Portal
* Create a **Standalone app** in the [developer portal](https://developer.twitter.com/en/portal/projects-and-apps)
(the app uses Standard v1.1 endpoints )

* Save the app **consumer key** and **consumer secret** and get an **access token** and **access token secret** for yourself.

* Activate the **Enable 3-legged OAuth** option. ("Request email address from users" is useless)

* Set `http://127.0.0.1:5000/auth/callback` and `http://localhost/auth/callback` as **callback URLs** to be able to run and test the app locally.

* Give it the **'Read + Write + Direct Messages'** permissions. 

### Installation
* Clone the project repository on your machine: `git clone https://github.com/QuentinJoder/Twitter-Supervisor.git`

* Open a terminal in the project folder and create a [virtual environment](https://flask.palletsprojects.com/en/1.1.x/installation/#virtual-environments).

* Run `$ pip install -Ur requirements.txt` in the virtual environment to install dependencies.

### Configuration
There are two ways to give to the app its configuration:

1) Use a `config.cfg` file where you put the config keys:

    There is already a skeleton called `config.cfg.sample` in the `/instance` folder that you can fill and rename.
    
    By default, the app will look in this folder to get `config.cfg`, but you can put it elsewhere and tell Twitter-Supervisor
    where tho find it with `$ export FLASK_INSTANCE_PATH=/path/to/instance/folder`
  
2) Or define all the config parameters as environment variables with `export` in Linux (`SET` in Windows) before you run
or test the app:

    ```shell script
    $ export DEFAULT_USER=JohnSmith
    $ export DEFAULT_ACCESS_TOKEN=pEeIsStOrEdInThEbAlLs
    $ ...
    ```

You can now run [tests](#Tests) to check if everything works and run the app !

### Run the app
Like a regular Flask application, launch Twitter-Supervisor with:
```shell script
$ export FLASK_APP=twittersupervisor
$ flask run
```
There is a `flask_run.sh` script in the project files which does that, and if you want to launch the live server in
[Debug Mode](https://flask.palletsprojects.com/en/1.1.x/quickstart/#debug-mode), run: `$ ./flask_run.sh development`
    
### Tests
in the project directory, simply run: 
```shell script
$ pytest
``` 
and if you want to test if the methods calling the Twitter API work too:
```shell script
$ pytest --allow_api_call
```

## Limitations of the Twitter API
The Twitter API has limitations which can restrain your ability to delete your statuses and favorites in 
mass with this tool. With a standard developer account you can:

- only get (and therefore delete) the 3200 last tweets of your own timeline.
- theoretically delete no more than 15 statuses and 15 favorites per 15 minutes window.
