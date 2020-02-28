from toolbox.forms import RegistrationFormEx
from django.contrib.auth.models import User

def user_created(sender, user, request, **kwargs):
	form = RegistrationFormEx(request.POST)
	user.first_name = form.data["first_name"]
	user.last_name = form.data["last_name"]
	user.save()

from registration.signals import user_registered
user_registered.connect(user_created)
