# Twitter Supervisor
> "I made this program to learn about Python and to know who stop following me on Twitter." - Quentin JODER 

Twitter Supervisor informs you (via direct message) when someone follows or unfollows you. It can also destroy your old
tweets, retweets and favorites but with some limitations (for details read the [related paragraph](#Limitations of the Twitter API)).

![Build and Test](https://github.com/QuentinJoder/Twitter-Supervisor/workflows/build-and-test/badge.svg?branch=master)

## Requirements
* **Python 3.4 or more** (older versions are not tested) and **pip**
* **A Twitter developer account** (a Standard one is good enough), you can apply [here](https://developer.twitter.com/en/apply-for-access).
* **Create an app in the [developer portal](https://developer.twitter.com/en/portal/projects-and-apps)** to get the
credentials required to access the Twitter API.
* Don't forget to give **'Direct Message' permission** to the app there.

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
and if you want to test if the methods calling the Twitter API work too:
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
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        set what minimum log level to use (default is INFO)
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


## Run the program automatically
To do that, you can, for example, create a scheduled job on a Linux server with **cron**:
* edit the crontab file of a user with the command `crontab -e`
* if you want to check for new followers/unfollowers each day at 7:00 a.m, and keep only your 10 most recent tweets, add:
<br/>`0 7 * * * cd /path/to/Twitter-Supervisor && python3 main.py --delete_tweets=10`
<br/>(`0 7 * * *` is the schedule time, https://crontab.guru/ can help you to define it. The rest of the entry is the 
command cron will run)
* save and close the editor with `Ctrl+X`and then `Y`(nano) or `:wq`(vim), and it is done !

For more information about cron, the syntax of the crontab files, nano or vim... ask your favorite search engine !

## Limitations of the Twitter API
The Twitter API has limitations which can restrain your ability to delete your statuses and favorites in 
mass with this tool. With a standard developer account you can:

- only get (and therefore delete) the 3200 last tweets of your own timeline.
- theoretically delete no more than 15 statuses and 15 favorites per 15 minutes window.

Consequently, the `--delete_tweets`, `--delete_retweets` or `--delete-favorites` [options](#options) are not useful if you want to mass
 delete your likes and tweets at once. Their intended purpose is enable you to regularly delete your oldest tweets and 
 likes, over the long term, with a [periodic program execution](#run-the-program-automatically).
