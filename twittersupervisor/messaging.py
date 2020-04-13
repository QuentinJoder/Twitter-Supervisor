from twitter import error
import logging


class Messaging:

    def __init__(self, api, args):
        self.twitter_api = api
        self.args = args

    def announce_follow_event(self, following, user_ids):
        # The method of the API can't have more than 100 users IDs in parameter.
        if len(user_ids) > 100:
            pattern = 'decided' if following is True else 'ceased'
            message = 'More than a hundred people {0} to follow you recently'.format(pattern)
            self.publish_message(message)

        elif user_ids != set():
            try:
                friendships_info = self.twitter_api.get_friendship_lookup(list(user_ids))
                for friendship_info in friendships_info:
                    self.publish_message(self.write_message(following, friendship_info))

            except error.TwitterError as e:
                self.publish_message(e)

    # TODO i18n of the message ?
    @staticmethod
    def write_message(following, friendship_info):
        if following:
            message = '{0} (@{1}) follows you now'.format(friendship_info.name, friendship_info.screen_name)
        else:
            try:
                message = '{0} (@{1}) unfollowed you'.format(friendship_info.name, friendship_info.screen_name)
                # TODO check if unfollower blocked the user (=> tweepy)
                if friendship_info.connections['blocking']:
                    message = message + ' because you blocked this user'
            # TODO Better handling of errors 50 (not found) & 63 (suspended)
            except AttributeError as e:
                logging.error(e)
                message = 'UserStatus of unfollower: {}'.format(friendship_info)

        if friendship_info.connections['following']:
            message = message + '. You are a follower of this user'
        if friendship_info.connections['muting']:
            message = message + '. You muted this user'
        return message

    def publish_message(self, message):
        if self.args.quiet:
            logging.info(message)
        else:
            self.twitter_api.send_direct_message(message)
