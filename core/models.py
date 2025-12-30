from django.db import models
from authentication.models import User

class Issue(models.Model):
    STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('solved', 'Solved'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    
    # Improved geographical data
    block = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    
    # Keep full address for legacy/display readiness
    address = models.CharField(max_length=255, null=True, blank=True)
    
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unverified')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    
    # Workflow fields
    rejection_reason = models.TextField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    
    verified_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    
    verified_by = models.ForeignKey(User, related_name='verified_issues', on_delete=models.SET_NULL, null=True, blank=True)
    rejected_by = models.ForeignKey(User, related_name='rejected_issues', on_delete=models.SET_NULL, null=True, blank=True)
    solved_by = models.ForeignKey(User, related_name='solved_issues', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class IssueHistory(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"History for {self.issue.title} at {self.changed_at}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('solved', 'Solved'),
        ('info', 'Info'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
