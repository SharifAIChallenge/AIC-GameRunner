from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from authentication.models import IP


class TokenIPAuth(TokenAuthentication):
    model = Token

    def authenticate(self, request):
        ans = super().authenticate(request)
        if not ans:
            return ans
        try:
            ip = IP.objects.get(user=ans[0])
        except IP.DoesNotExist:
            msg = _('Token does not have any available IPs')
            raise exceptions.AuthenticationFailed(msg)
        if ip != request.META.get('REMOTE_ADDR'):
            msg = _('Token is not available with this IP')
            raise exceptions.AuthenticationFailed(msg)
        return ans
