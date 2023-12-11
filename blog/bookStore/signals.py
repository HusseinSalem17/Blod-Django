from django.db.models.signals import post_save
from django.contrib.auth.models import User

from .models import Customer
from django.contrib.auth.models import Group

# need to import the signals in the apps.py file using ready function
# need to add this file in the settings.py file in INSTALLED_APPS
# OR
# need to add this line in the __init__.py file in the same app


def customer_create_profile(sender, instance, created, **kwargs):
    # created for any new in database of User
    if created:
        # this to get the group name
        group = Group.objects.get(name="customer")
        instance.groups.add(group)
        Customer.objects.create(
            user=instance,
            name=instance.username,
        )
        print("Profile created!")


# post_save: signal to create a profile for any new user
# connect: to connect the signal to the function (first parameter: function, second parameter: sender)
# first parameter(function) : is to listen to any new user
# sender (User): is the model that will send the signal
post_save.connect(customer_create_profile, sender=User)
