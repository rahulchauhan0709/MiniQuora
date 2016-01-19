from django import forms
from django.contrib.auth import authenticate
from account.models import CustomUser
from material import *

class LoginForm(forms.Form):
	username = forms.CharField(max_length=20)
	password = forms.CharField(widget = forms.PasswordInput())
	
	def clean_username(self):
		return self.cleaned_data['username']


	def clean_password(self):
		return self.cleaned_data['password']

	def __init__(self , *args , **kwargs):
		self.user_cache = None
		super(LoginForm , self).__init__(*args , **kwargs)	

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if username and password :
			self.user_cache = authenticate(username = username , password = password)
			if self.user_cache is None:
				raise forms.ValidationError('Invalid Username or Password')
			elif not self.user_cache.is_active:
				raise forms.ValidationError('User is not active')
		return self.cleaned_data

	def get_user(self):
		return self.user_cache

class SignupForm(forms.ModelForm):
	password1 = forms.CharField(label = 'Password' , widget = forms.PasswordInput)
	password2 = forms.CharField(label = 'Confirm Password' , widget = forms.PasswordInput , help_text = 'Should be same as password')
		
	def clean_password2(self):
		data_password1 = self.cleaned_data['password1']
		data_password2 = self.cleaned_data['password2']
		if data_password1 and data_password2 and data_password1 != data_password2:
			raise forms.ValidationError("Passwords dont match")
		return data_password2

	def save(self , commit = True):
		user = super(SignupForm , self).save(commit = False)
		user.set_password(self.cleaned_data.get('password1'))
		user.is_active = False
		if commit:
			user.save()
		return user

	class Meta:
		model = CustomUser
		fields = ['username' , 'email' , 'phone_number']
		
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(max_length = 254)
    def clean_email(self):
        data_email = self.cleaned_data.get('email')
        if data_email and CustomUser.objects.filter(email = data_email).count() == 0:
            raise forms.ValidationError("We cannot find user with this email address. Please verify email address and try again");
        return data_email

class SetPasswordForm(forms.Form):
    password1 = forms.CharField(label='Password', widget = forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget = forms.PasswordInput, help_text = 'Should be same as Password')
    def clean_password2(self):
        data_password1 = self.cleaned_data['password1']
        data_password2 = self.cleaned_data['password2']
        if data_password1 and data_password2 and data_password1 != data_password2:
            raise forms.ValidationError("Passwords don't match")
        return data_password2
        
class ProfileForm(forms.ModelForm):
    old_password = forms.CharField(label='Old Password', widget = forms.PasswordInput, required = False)
    new_password = forms.CharField(label='New Password', widget = forms.PasswordInput, required = False)
    
    layout = Layout(
        Row(Span6('first_name'), Span6('last_name')),
        Row(Span2('gender'), Span4('dob'), Span6('phone_number')),
        Row('username', 'email'),
        Row('old_password', 'new_password'),
        'profile_pic'
    )
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['first_name'].required = True
        
    def clean_gender(self):
        data_gender = self.cleaned_data['gender']
        if data_gender and data_gender == 'NS':
            raise forms.ValidationError('You must specify a valid gender')
        return data_gender
      
    def clean_old_password(self):
        data_old_password = self.cleaned_data['old_password']
        if data_old_password and not self.instance.check_password(data_old_password):
            raise forms.ValidationError('Incorrect Password')
        return data_old_password
    
    class Meta:
        model = CustomUser
        fields = ['gender', 'profile_pic', 'dob', 'phone_number', 'username', 'email', 'first_name', 'last_name']


