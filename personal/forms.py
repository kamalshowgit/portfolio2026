from django import forms
from .models import Profile, QuickLink, Project, Note, ContactMessage, Experience, Education

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'title', 'bio', 'email', 'photo', 'linkedin', 'github', 'location', 'phone']

class QuickLinkForm(forms.ModelForm):
    class Meta:
        model = QuickLink
        fields = ['title', 'url']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'url', 'image']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'folder', 'completed']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['employer', 'title', 'location', 'start', 'end', 'description']

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'year', 'details']
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your name', 'style': 'width:100%;padding:8px;margin-bottom:10px;border:1px solid #ccc;border-radius:6px'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com', 'style': 'width:100%;padding:8px;margin-bottom:10px;border:1px solid #ccc;border-radius:6px'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'style': 'width:100%;padding:8px;margin-bottom:10px;border:1px solid #ccc;border-radius:6px'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your message...', 'rows': 4, 'style': 'width:100%;padding:8px;margin-bottom:10px;border:1px solid #ccc;border-radius:6px'}),
        }
