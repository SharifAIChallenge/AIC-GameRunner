from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from api.models import Token, IP


class TokenIPAuth(TokenAuthentication):
    model = Token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            key = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        model = self.get_model()
        try:
            token = Token.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        if token.ip_stricted:
            ip = request.META.get('REMOTE_ADDR')
            try:
                token.IP.get(ip=ip)
            except model.DoesNotExist:
                raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return None, True
