from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User
# using this special class i can create all forms 
# for fields inside the model Room
# use exclude to remove nay unwanted fields
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host','participants']



class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username','email']
              

