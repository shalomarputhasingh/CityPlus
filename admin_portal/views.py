from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.models import Issue, Notification, IssueHistory
from django.db.models import Count
import json
from django.core.serializers.json import DjangoJSONEncoder

# --- Dashboard ---
@login_required
def dashboard(request):
    # Fetch all issues
    issues = Issue.objects.all().select_related('citizen').order_by('-created_at')
    
    # 1. Total Counts
    stats = {
        'total_blocks': 8,
        'total_taluks': 5,
        'total_villages': 98
    }
    
    # 2. Issues Summary
    summary = {
        'total': issues.count(),
        'unverified': issues.filter(status='unverified').count(),
        'verified': issues.filter(status='verified').count(), # Covers In Progress
        'rejected': issues.filter(status='rejected').count(),
        'solved': issues.filter(status='solved').count(),
        # Mappings for template which uses distinct names
        'pending': issues.filter(status='unverified').count(),
        'in_progress': issues.filter(status='verified').count(),
    }
    
    # 3. Bar Chart Data (Issues per Block)
    block_data = Issue.objects.values('block').annotate(count=Count('id')).order_by('-count')
    bar_labels = [item['block'] if item['block'] else 'Unknown' for item in block_data]
    bar_counts = [item['count'] for item in block_data]
    
    # 4. Pie Chart Data
    pie_labels = ['Unverified', 'In Progress', 'Rejected', 'Solved']
    pie_data = [summary['unverified'], summary['verified'], summary['rejected'], summary['solved']]
    
    context = {
        'issues': issues[:10], # Just recent ones for dashboard
        'stats': stats,
        'summary': summary,
        'bar_chart': json.dumps({'labels': bar_labels, 'data': bar_counts}, cls=DjangoJSONEncoder),
        'pie_chart': json.dumps({'labels': pie_labels, 'data': pie_data}, cls=DjangoJSONEncoder)
    }
    
    return render(request, 'admin_portal/dashboard.html', context)

# --- Feature A: Verification Queue ---
@login_required
def verification_queue(request):
    issues = Issue.objects.filter(status='unverified').order_by('created_at') # Oldest first usually
    return render(request, 'admin_portal/verification_queue.html', {'issues': issues})

@login_required
def verify_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if request.method == 'POST':
        # Status Change
        issue.status = 'verified'
        issue.verified_at = timezone.now()
        issue.verified_by = request.user
        issue.save()
        
        # Audit
        IssueHistory.objects.create(
            issue=issue,
            old_status='unverified',
            new_status='verified',
            changed_by=request.user,
            notes='Issue verified by admin.'
        )
        
        # Notification
        Notification.objects.create(
            user=issue.citizen,
            issue=issue,
            type='verified',
            message=f"Your issue '{issue.title}' has been verified and is being processed."
        )
        
        messages.success(request, f"Issue #{issue.id} verified successfully.")
        return redirect('verification_queue')
    
    return redirect('verification_queue')

@login_required
def reject_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('rejection_reason')
        
        issue.status = 'rejected'
        issue.rejected_at = timezone.now()
        issue.rejected_by = request.user
        issue.rejection_reason = reason
        issue.save()
        
        # Audit
        IssueHistory.objects.create(
            issue=issue,
            old_status='unverified', # Assuming mainly rejecting from unverified
            new_status='rejected',
            changed_by=request.user,
            rejection_reason=reason,
            notes='Issue rejected.'
        )
        
        # Notification
        Notification.objects.create(
            user=issue.citizen,
            issue=issue,
            type='rejected',
            message=f"Your issue '{issue.title}' was rejected. Reason: {reason}"
        )
        
        messages.success(request, f"Issue #{issue.id} rejected.")
        return redirect('verification_queue')
        
    return redirect('verification_queue')


# --- Feature B: Resolution Queue ---
@login_required
def resolution_queue(request):
    issues = Issue.objects.filter(status='verified').order_by('verified_at')
    return render(request, 'admin_portal/resolution_queue.html', {'issues': issues})

@login_required
def solve_issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    
    if request.method == 'POST':
        notes = request.POST.get('resolution_notes')
        
        issue.status = 'solved'
        issue.solved_at = timezone.now()
        issue.solved_by = request.user
        issue.resolution_notes = notes
        issue.save()
        
        # Audit
        IssueHistory.objects.create(
            issue=issue,
            old_status='verified',
            new_status='solved',
            changed_by=request.user,
            notes=f"Resolved: {notes}"
        )
        
        # Notification
        Notification.objects.create(
            user=issue.citizen,
            issue=issue,
            type='solved',
            message=f"Good news! Your issue '{issue.title}' has been resolved."
        )
        
        messages.success(request, f"Issue #{issue.id} marked as solved.")
        return redirect('resolution_queue')
        
    return redirect('resolution_queue')

# --- Feature C: Reporting ---
@login_required
def report_config(request):
    return render(request, 'admin_portal/report_config.html')

@login_required
def generate_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')
        category = request.POST.get('category')
        
        # Base Query
        issues = Issue.objects.all().order_by('-created_at')
        
        # Apply Filters
        if start_date:
            issues = issues.filter(created_at__date__gte=start_date)
        if end_date:
            issues = issues.filter(created_at__date__lte=end_date)
            
        if status and status != 'all':
            issues = issues.filter(status=status)
            
        if category and category != 'all':
            issues = issues.filter(category=category)
            
        context = {
            'issues': issues,
            'start_date': start_date,
            'end_date': end_date,
            'status_filter': status,
            'category_filter': category
        }
        
        # Render the basic HTML template which auto-opens print dialog
        return render(request, 'admin_portal/report_print.html', context)
        
    return redirect('report_config')
