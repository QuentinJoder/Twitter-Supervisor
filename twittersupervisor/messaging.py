import logging


class Messaging:

    def __init__(self, api, args):
        self.twitter_api = api
        self.args = args

    # TODO i18n of the messages ?
    def announce_follow_event(self, following, user_ids):
        # The method of the API can't have more than 100 users IDs in parameter.
        if len(user_ids) > 100:
            pattern = 'decided' if following is True else 'ceased'
            message = 'More than a hundred people {0} to follow you recently'.format(pattern)
            self.publish_message(message)
        elif user_ids != set():
            if following:
                self.announce_followers(user_ids)
            else:
                self.announce_traitors(user_ids)
        else:
            pass

    def announce_followers(self, followers):
        friendships_info = self.twitter_api.get_friendship_lookup(list(followers))
        for friendship_info in friendships_info:
            message = '{0} (@{1}) follows you now'.format(friendship_info.name, friendship_info.screen_name)
            if friendship_info.connections['following']:
                message = message + '. You are a follower of this user'
            if friendship_info.connections['muting']:
                message = message + '. You muted this user'
            self.publish_message(message)

    def announce_traitors(self, traitors):
        for traitor in traitors:
            friendships, error = self.twitter_api.get_friendship_show(traitor)
            if error is None:
                target_info = friendships[1]
                message = '@{} unfollowed you'.format(target_info.screen_name)
                source_info = friendships[0]
                if source_info.blocking:
                    message = message + ' and is blocked by you'
                if source_info.blocked_by:
                    message = message + '. This user blocks you'
                if source_info.following:
                    message = message + '. You are a follower of this user'
                if source_info.muting:
                    message = message + '. You muted this user'
                self.publish_message(message)
            # TODO in case of error, get unfollower username from the DB
            elif hasattr(error, 'api_code') and error.api_code == 50:
                self.publish_message('One of your follower\'s account (n°{}) has been deleted'
                                     .format(traitor))
            elif hasattr(error, 'api_code') and error.api_code == 63:
                self.publish_message('One of your follower\'s account (n°{}) has been suspended'
                                     .format(traitor))
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
