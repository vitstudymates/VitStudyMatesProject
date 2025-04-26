from django import forms
from .models import Notes

class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'description', 'course_code', 'course_name', 'file']
        
    def __init__(self, *args, **kwargs):
        super(NotesForm, self).__init__(*args, **kwargs)
        
        # Add placeholders and classes
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter title of your notes',
            'class': 'form-control'
        })
        
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Provide a brief description of your notes',
            'class': 'form-control'
        })
        
        self.fields['course_code'].widget.attrs.update({
            'placeholder': 'e.g., CS101, MATH202',
            'class': 'form-control'
        })
        
        self.fields['course_name'].widget.attrs.update({
            'placeholder': 'e.g., Introduction to Programming, Calculus II',
            'class': 'form-control'
        })
        
        self.fields['file'].widget.attrs.update({
            'class': 'form-control'
        })
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Get file extension
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError("Only PDF, DOC, and DOCX files are allowed.")
            
            # Check file size (10MB max)
            if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                raise forms.ValidationError("File size must be under 10MB.")
        return file
    




    











from django import forms
from .models import NoteRequest, RequestReply, NoteFile


class NoteRequestForm(forms.ModelForm):
    """Form for creating note requests"""
    class Meta:
        model = NoteRequest
        fields = ['title', 'course_code', 'course_name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Describe what notes you\'re looking for and any specific topics or requirements...'}),
        }


class RequestReplyForm(forms.ModelForm):
    """Form for replying to note requests"""
    class Meta:
        model = RequestReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'reply-input',
                'placeholder': 'Write your reply here... You can provide information or attach notes files.',
                'rows': 4
            })
        }


class NoteFileForm(forms.ModelForm):
    """Form for uploading note files"""
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': False}))
    
    class Meta:
        model = NoteFile
        fields = ['file']



# Q paper
# forms.py
from django import forms
from .models import SemesterPaper

class PaperUploadForm(forms.ModelForm):
    class Meta:
        model = SemesterPaper
        fields = ['title', 'file']  # Removed course as we're handling it separately
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'file-upload-input', 'accept': '.pdf'})
        }