# Twitter Supervisor
> "I made this program to learn about Python and to know who stop following me on Twitter." - Quentin JODER 

Twitter Supervisor informs you (via direct message) when someone follows or unfollows you. It can also destroy your old
tweets and favorites but with some limitations (for details read the [related paragraph](#Limitations of the Twitter API)).

Additional features might be added in the (near) future: keeping track of the "betrayals", trends detection 
in your friends (people you are following) tweets...

[![Build Status](https://travis-ci.com/QuentinJoder/Twitter-Supervisor.svg?branch=master)](https://travis-ci.com/QuentinJoder/Twitter-Supervisor)

## Requirements
* **Python 3.4 or more** (older versions are not tested) and **pip**
* **Having a (at least free) Twitter developer account** (https://developer.twitter.com/en/apply-for-access), to get the
 key, the token and their secrets, which are all required to access the Twitter API.
* Don't forget to give **'Direct Message' permission** for your API.

## Installation
* Clone the project repository on your machine.
* Run `pip install -Ur requirements.txt`
* Create a `config.json` file (if you choose another name, specify it with the [option](#options)`--config` when you run
 the script) in the project directory, where you will put the API keys, the id of the account you want to supervise, and
  the name of the SQLite database file where the app data will be stored. It should look like this:

    ```json
    {
      "twitter_api": {
        "username": "@aTwitterUserName",
        "consumer_key": "...",
        "consumer_secret": "...",
        "access_token": "...",
        "access_token_secret": "..."
      },
      "database_file": "followers.db"
    }
    ```

## Tests
in the project directory, run: 
```bash
$ pytest
``` 
and if you want to test if the methods calling the Twitter API works too:
```bash
$ pytest --allow_api_call
```
## How to use it?
### Core command line
Run `$ python main.py`(Windows) or `$ python3 main.py`(Linux):
* the first time it will only create a `followers.db` SQLite database (to store the app data) and a `.log` file.
* Then, each time this command is run, the specified account (`"username"` key in `config.json`) will receive messages
telling him who are the followers it has gained or lost in the meantime.


### Options
```
optional arguments:
  -h, --help            show this help message and exit
  --quiet               disable the sending of direct messages
  --config CONFIG_FILE  specify which configuration file to use. It must be a
                        JSON file.
  --database DB_FILE    specify which SQLite .db file to use
  --delete_tweets [NUM_OF_PRESERVED_TWEETS]
                        delete old tweets of the account, preserve only the
                        specified number (by default 50)
  --delete_retweets [NUM_OF_PRESERVED_RETWEETS]
                        delete old "blank" retweets (does not delete quoted
                        statuses), preserve only the specified number (by
                        default 10)
  --delete_favorites [NUM_OF_PRESERVED_FAVORITES]
                        delete old likes of the account, preserve only the
                        specified number (by default 10)
  --version             show the program version number and exit

```


## Automate the script with cron
If you wish to automate this operation, you can, for example, create a scheduled job on a Linux server with **cron**:
* edit the crontab file of a user with the command `crontab -e`
* if you want to check for new followers/unfollowers each day at 7:00 a.m, insert:
<br/>`0 7 * * * cd [path to the parent directory of "Twitter-Supervisor"]/Twitter-Supervisor && python3 main.py`
<br/>(`0 7 * * *` is the schedule time, https://crontab.guru/ can help you to define it. The rest of the entry is the 
command cron will run)
* save and close the editor with `Ctrl+X`and then `Y`(nano) or `:wq`(vim), and it is done !

For more information about cron, the syntax of the crontab files, nano or vim... ask your favorite search engine !

## Limitations of the Twitter API
The Twitter API has limitations which are particularly restraining the ability to delete your statuses and favorites in 
mass. With a standard developer account you :

- can only access the latest 3200 tweets of a user. Therefore, you cannot delete older tweets (except if you delete recent
tweets to let older ones takes their places!)
- can theoretically delete no more than 15 statuses and 15 favorites per 15 minutes window.

Consequently, the `--delete_tweets`, `--delete_retweets` or `--delete-favorites` [options](#options) are not useful if you want to mass
 delete your likes and tweets at once. Their intended purpose is enable you automatically delete your oldest tweets and 
 likes, in the long term, with an [automated](#automate-the-script-with-cron) use of the script.
