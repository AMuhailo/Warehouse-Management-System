from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class StaffURLBarrier(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_chief:
            return redirect("manage:goods_storage_url")
        return super().dispatch(self, request, *args, **kwargs)
    
