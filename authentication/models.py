from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token as BaseToken


class IP(models.Model):
    ip = models.GenericIPAddressField(null=False, blank=False)
    user = models.ForeignKey(
        User, related_name='IP',
        on_delete=models.CASCADE
    )
