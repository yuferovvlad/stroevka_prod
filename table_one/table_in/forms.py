# from django.forms import ModelForm
from django import forms
from .models import TableStat, TableUsers, SHIRT_SIZES
from django.core.files.images import get_image_dimensions


class CategoryForm(forms.ModelForm):
    class Meta:
        model = TableStat
        fields = ('name', 'number', 'check_top_category')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'check_top_category': forms.Select(attrs={'class': 'form-control'})
        }


class AddUsers(forms.ModelForm):
    class Meta:
        model = TableUsers
        fields = ('name',
                  'doljnost',
                  'user_category',
                  'user_status',
                  'user_date_range',
                  'image', 'user_corona', 
                  'user_vakcina_corona', 
                  'users_sign')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'doljnost': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'user_category': forms.Select(attrs={'class': 'form-control'}),
            'user_status': forms.Select(attrs={'class': 'form-control'}),
            'user_date_range': forms.DateInput(format='%d.%m.%Y - %d.%m.%Y', attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'user_corona': forms.CheckboxInput(),
            'user_vakcina_corona': forms.CheckboxInput(),
            'users_sign': forms.CheckboxInput()
        }

    def clean_picture(self):
       picture = self.cleaned_data.get("image")
       if not picture:
           raise forms.ValidationError("No image!")
       else:
           w, h = get_image_dimensions(picture)
           if w != 100:
               raise forms.ValidationError(
                   "The image is %i pixel wide. It's supposed to be 100px" % w)
           if h != 200:
               raise forms.ValidationError(
                   "The image is %i pixel high. It's supposed to be 200px" % h)
       return picture


class ChangeStatusUsers(forms.ModelForm):
    class Meta:
        model = TableUsers
        fields = ('name', 'user_category')
        
        widgets = {
            'name': forms.TextInput(),
            'user_category': forms.CharField(widget=forms.Select(choices=SHIRT_SIZES))
        }

        def save(self, user=None):
            user_status = super(TableUsers, self).save(commit=False)
            if user:
                user_status.user = user
            user_status.save()
            return user_status


# class ChangeSignForm(forms.ModelForm):
#     class Meta:
#         model = SignUsers
#         fields = ('users_sign',)

#         widgets = {
#             'users_sign': forms.Select(attrs={'class': 'form-control'})
#         }

        # def save(self, user=None):
        #     user_status = super(SignUsers, self).save(commit=False)
        #     if user:
        #             user_status.user = user
        #         user_status.save()
        #         return user_status
