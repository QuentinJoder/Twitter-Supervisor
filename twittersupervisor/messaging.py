import logging


class Messaging:

    def __init__(self, args, api, database):
        self.twitter_api = api
        self.args = args
        self.database = database

    # TODO:
    #  i18n of the messages
    #  Handle special characters to show the "Display name" of the user
    def present_new_followers(self, followers_set):
        if len(followers_set) != 0:  # Avoid useless "GET friendships/lookup" request
            friendships_info = self.twitter_api.get_friendship_lookup(list(followers_set))
            for friendship_info in friendships_info:
                message = '@{} follows you now.'.format(friendship_info.screen_name)
                if friendship_info.connections['following']:
                    message = message + ' You are a follower of this user.'
                if friendship_info.connections['muting']:
                    message = message + ' You muted this user.'
                self.publish_message(message)

    def denounce_traitors(self, traitors):
        for traitor in traitors:
            friendships, error = self.twitter_api.get_friendship_show(traitor)
            if error is None:
                target_info = friendships[1]
                message = '@{} unfollowed you'.format(target_info.screen_name)
                source_info = friendships[0]
                if source_info.blocking:
                    message = message + ' You blocked him/her.'
                if source_info.blocked_by:
                    message = message + ' This user blocks you.'
                if source_info.following:
                    message = message + ' You are a follower of this user.'
                if source_info.muting:
                    message = message + ' You muted this user.'
                self.publish_message(message)
            elif hasattr(error, 'api_code') and error.api_code == 50:
                traitor_name = self._get_username(traitor)
                self.publish_message('One of your follower\'s account ({}) has been deleted'
                                     .format(traitor_name))
            elif hasattr(error, 'api_code') and error.api_code == 63:
                traitor_name = self._get_username(traitor)
                self.publish_message('One of your follower\'s account ({}) has been suspended'
                                     .format(traitor_name))
            else:
                message = 'GET friendships/show failed: source username={0},target_id={1}, error:{2}'\
                    .format(self.twitter_api.username, traitor, error)
                logging.error(message)
                self.publish_message(message)

    def publish_message(self, message):
        if self.args.quiet:
            logging.info(message)
        else:
            self.twitter_api.send_direct_message(message)

    def _get_username(self, user_id):
        name = self.database.get_username_by_id(user_id)
        if name is None:
            name = 'n°' + user_id
        else:
            name = '@' + name
        return name
