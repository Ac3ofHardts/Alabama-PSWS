from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class StationActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.profile.signup_confirmation)
        )

station_activation_token = StationActivationTokenGenerator()
