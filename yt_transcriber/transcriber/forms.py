from django import forms

class YouTubeURLForm(forms.Form):
    url = forms.URLField(
        label='YouTube URL',
        max_length=200,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter YouTube URL'
        })
    )