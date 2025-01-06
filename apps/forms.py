import re

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, BooleanField, ModelForm
from phonenumber_field.formfields import PhoneNumberField

from apps.models import User, Order


class LoginForm(Form):
    phone_number = CharField(max_length=255)
    password = CharField(max_length=255)
    check_box = BooleanField(error_messages={"required" : "Shartlarni qabul qiling !"})

    def clean_phone_number(self):
        phone_number =self.cleaned_data.get("phone_number")
        return  "+" + re.sub('\D' ,"" ,  phone_number)

    def clean_password(self):
        return make_password(self.cleaned_data.get('password'))


class ProfileModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    class Meta:
        model = User
        fields = "first_name" , "last_name" , "district" , "address" , "telegram_id" , "description"
        # extra_kwargs = {
        #     "first_name": {"required" : False}
        # }

    def clean(self):
        data = self.cleaned_data
        for k , v in data.copy().items():
            if not v:
                del data[k]
        return data




    def save(self, commit=False):
        return super().save(commit)


class OrderForm(Form):

    name  = CharField()
    phone_number = CharField()
    product_id = CharField()

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        return "+" + re.sub('\D', "", phone_number)











