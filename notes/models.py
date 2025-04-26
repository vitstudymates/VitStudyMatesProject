from django.db import models
from django.contrib.auth.models import User




class SignUp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    
    # Remove duplicate fields like first_name, last_name, email, password
    # as they're already part of the User model
    
    def __str__(self):
        return self.user.username
        





class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    
    def _str_(self):
        return self.name

class PlacementExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    interview_date = models.DateField()
    package_offered = models.CharField(max_length=50, blank=True)
    got_selected = models.BooleanField(default=False)
    
    # Interview rounds
    rounds_description = models.TextField(help_text="Describe the rounds you went through")
    technical_questions = models.TextField(help_text="Share technical questions asked", blank=True)
    hr_questions = models.TextField(help_text="Share HR questions asked", blank=True)
    
    # Preparation advice
    preparation_strategy = models.TextField(help_text="How did you prepare?")
    resources_used = models.TextField(help_text="Books, websites, courses you used")
    tips_for_juniors = models.TextField(help_text="Any advice for juniors?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _str_(self):
        return f"{self.user.username}'s experience at {self.company.name}"

class PlacementQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
        return f"Question by {self.user.username}"

class PlacementAnswer(models.Model):
    question = models.ForeignKey(PlacementQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
        return f"Answer by {self.user.username}"


class PlacementComment(models.Model):
    experience = models.ForeignKey(PlacementExperience, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
        return f"Comment by {self.user.username} on {self.experience.company.name} experience"








from django.db import models
from django.contrib.auth.models import User

class Notes(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Changed the default from 'pending' to 'approved'
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    
    class Meta:
        verbose_name = 'Notes'
        verbose_name_plural = 'Notes'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    








# First, let's create a model for note requests in models.py

from django.db import models
from django.contrib.auth.models import User



    









from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class NoteRequest(models.Model):
    """Model for note requests from users"""
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('solved', 'Solved'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    course_code = models.CharField(max_length=20, blank=True, null=True)
    course_name = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('note_request_detail', args=[self.pk])
    
    @property
    def reply_count(self):
        return self.replies.count()


class RequestReply(models.Model):
    """Model for replies to note requests"""
    note_request = models.ForeignKey(NoteRequest, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Request replies'
    
    def __str__(self):
        return f"Reply to {self.note_request.title}"


class NoteFile(models.Model):
    """Model for files attached to request replies"""
    reply = models.ForeignKey(RequestReply, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='notes_files/')
    filename = models.CharField(max_length=255)
    file_size_kb = models.IntegerField(default=0)
    file_extension = models.CharField(max_length=10, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Assuming the uploader is the user related to the reply
            user = self.reply.user  
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.points += 15  # You can give more for full notes
            profile.save()





from django.db import models
from django.contrib.auth.models import User

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.is_used and self.expires_at > datetime.now()




# q paper
# models.py
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.title}"

class SemesterPaper(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year = models.IntegerField(default=2025)
    semester = models.CharField(max_length=20, default='FALL')
    file = models.FileField(upload_to='semester_papers/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            profile, _ = Profile.objects.get_or_create(user=self.uploaded_by)
            profile.points += 20  # Give higher for q-papers if desired
            profile.save()




#points 
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

# Signal to auto-create or update Profile when User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
