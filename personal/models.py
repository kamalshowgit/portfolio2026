from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=200, default='Kamal Soni')
    title = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class QuickLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.title

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Note(models.Model):
    FOLDER_CHOICES = [
        ('todo', 'Todo'),
        ('ideas', 'Ideas'),
        ('reminders', 'Reminders'),
        ('other', 'Other'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    folder = models.CharField(max_length=50, choices=FOLDER_CHOICES, default='todo')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-folder', '-created_at']


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    employer = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    start = models.CharField(max_length=50, blank=True)
    end = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employer} - {self.title}"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=300)
    degree = models.CharField(max_length=300, blank=True)
    year = models.CharField(max_length=20, blank=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.institution} ({self.year})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']