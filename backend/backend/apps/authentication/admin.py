from django.contrib import admin
from django.contrib.auth.models import Group
from oauth2_provider.models import AccessToken, Grant, IDToken, RefreshToken

admin.site.unregister(Group)
admin.site.unregister(AccessToken)
admin.site.unregister(Grant)
admin.site.unregister(IDToken)
admin.site.unregister(RefreshToken)
