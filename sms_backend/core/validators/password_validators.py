"""
Password validators for Django.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterValidator:
    """
    Validate that the password contains at least one special character.
    """
    
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            raise ValidationError(
                _('Password must contain at least one special character.'),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _('Your password must contain at least one special character.')


class UppercaseValidator:
    """
    Validate that the password contains at least one uppercase letter.
    """
    
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'),
                code='password_no_uppercase',
            )
    
    def get_help_text(self):
        return _('Your password must contain at least one uppercase letter.')
