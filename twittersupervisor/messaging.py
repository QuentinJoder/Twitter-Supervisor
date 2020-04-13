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
                # If user is suspended/deleted "GET friendship/lookup" won't find it
                if len(friendships_info) != len(user_ids):
                    missing_traitors = self.find_missing_traitors(friendships_info, user_ids)
                    for traitor_id in missing_traitors:
                        user, error_message = self.twitter_api.get_user(traitor_id.id)
                        if error_message['code'] == 50:
                            self.publish_message('One of your follower\'s account (n°{}) has been deleted'
                                                 .format(traitor_id))
                        elif error_message['code'] == 63:
                            self.publish_message('One of your follower\'s account (n°{}) has been suspended'
                                                 .format(traitor_id))
                        else:
                            logging.error('Traitor search fuc**d up with: user {0}, id in DB:{1}, error:{2}'
                                          .format(user, traitor_id, error_message))

            except error.TwitterError as e:
                self.publish_message(e)

    # TODO i18n of the message ?
    @staticmethod
    def write_message(following, friendship_info):
        if following:
            message = '{0} (@{1}) follows you now'.format(friendship_info.name, friendship_info.screen_name)
        else:
            message = '{0} (@{1}) unfollowed you'.format(friendship_info.name, friendship_info.screen_name)
            # TODO check if unfollower blocked the user (=> tweepy)
            if friendship_info.connections['blocking']:
                message = message + ' because you blocked this user'

        if friendship_info.connections['following']:
            message = message + '. You are a follower of this user'
        if friendship_info.connections['muting']:
            message = message + '. You muted this user'
        return message

    @staticmethod
    def find_missing_traitors(found_traitors, traitors_set):
        for found_traitor in found_traitors:
            if found_traitor.id in traitors_set:
                traitors_set.discard(found_traitor.id)
        return traitors_set

    def publish_message(self, message):
        if self.args.quiet:
            logging.info(message)
        else:
            self.twitter_api.send_direct_message(message)
