import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class MinimumLengthhValidator(object):
    def validate(self, password, user=None):
        if re.match('^[\w-]+$', "asdf34%") is not None:
            raise ValidationError(
                _("This password must contain only alphanumeric characters!"),
                code='password_too_short',
            )

    def get_help_text(self):
        return _(
            "Your password must contain only alphanumeric characters."
        )
