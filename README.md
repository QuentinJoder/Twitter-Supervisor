# Twitter-Supervisor
> "I made this program to learn about Python and to know who stop following me on Twitter." - Quentin JODER 

Twitter Supervisor informs you (via direct message) when someone follows or unfollows you. You can set it up to delete
your old tweets, retweets and favorites.

Twitter-Supervisor is a [Flask](https://flask.palletsprojects.com/) app using [tweepy](https://www.tweepy.org/) and 
[python-twitter](https://python-twitter.readthedocs.io/en/latest/) to access the Twitter API.

![Build and Test](https://github.com/QuentinJoder/Twitter-Supervisor/workflows/build-and-test/badge.svg?branch=master)

## Requirements
* **Python 3.4 or more** (older versions are not tested) and **pip**

* **A Twitter developer account** (a Standard one is good enough), you can apply [here](https://developer.twitter.com/en/apply-for-access).

## How to run the app

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

* There are two ways to give to the app the Twitter API credentials you created and other config parameters:
    1) Create a `config.cfg` file in the `/instance` folder where you put the config keys. There is already a skeleton 
    called `config.cfg.sample` in the aforementioned folder that you can fill and rename.

        ```properties
        ## MANDATORY
        # Required by flask.session, run `$ python -c 'import os; print(os.urandom(16))'` to get one
        SECRET_KEY= b'...'
        
        # TWITTER API
        APP_CONSUMER_KEY='aConsumerKey'
        APP_CONSUMER_SECRET='aConsumerSecret'
        
        # DATABASE (Twitter Supervisor uses an SQLite database)
        DATABASE_FILE='instance/twittersupervisor.db'
        
        ## OPTIONAL
        # TWITTER CREDENTIALS (Needed if you want to run tests)
        DEFAULT_ACCESS_TOKEN='aUserAccessToken'
        DEFAULT_ACCESS_TOKEN_SECRET='aUserAccessTokenSecret'
        DEFAULT_USER='aUser'
        
        # LOGGING
        LOG_LEVEL='WARNING'
        LOG_FILE='twitter_supervisor.log'
        ```
  
    2) Or define all the parameters above as environment variables with `export` in Linux (`SET` in Windows) before you run
     or test the app:
        ```shell script
        $ export DEFAULT_USER=JohnSmith
        $ export DEFAULT_ACCESS_TOKEN=pEeIsStOrEdInThEbAlLs
        $ ...
        ```
* You can now run [tests](#Tests) to check if everything works and run the app !

### Run the app
Like any Flask application, launch Twitter-Supervisor with:
```shell script
$ export FLASK_APP=twittersupervisor
$ flask run
```
There is a `flask_run.sh` script in the project files which does that.

`$ ./flask_run.sh development`  launch the live server in [Debug Mode](https://flask.palletsprojects.com/en/1.1.x/quickstart/#debug-mode).

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
