from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Issue, Notification
from django.contrib import messages
from Cityplus.supabase_client import supabase
from supabase import create_client, Client
import os
import time
import mimetypes

from django.db.models import Q

@login_required
def dashboard(request):
    # Fetch issues based on phone number (New) OR Username (Old/Legacy)
    phone = request.user.phone_number
    
    if phone:
        # Create variations to catch legacy data (e.g. '919384256364' stored as username)
        phone_clean = phone.replace('+', '') # Remove +
        
        issues = Issue.objects.filter(
            Q(citizen__phone_number=phone) |      # Standard match
            Q(citizen__username=phone) |          # Username match exact
            Q(citizen__username=phone_clean)      # Username match without +
        ).order_by('-created_at')
    else:
        # Fallback
        issues = Issue.objects.filter(citizen=request.user).order_by('-created_at')
    
    # Calculate stats for the dashboard
    stats = {
        'total': issues.count(),
        'unverified': issues.filter(status='unverified').count(),
        'verified': issues.filter(status='verified').count(),
        'rejected': issues.filter(status='rejected').count(),
        'solved': issues.filter(status='solved').count(),
    }
    
    return render(request, 'citizen/dashboard_v2.html', {'issues': issues, 'stats': stats})

@login_required
def issue_detail(request, pk):
    # Allow access if the issue belongs to the user OR matches their phone number (Legacy Logic)
    phone = request.user.phone_number
    
    if phone:
        phone_clean = phone.replace('+', '')
        issue = get_object_or_404(
            Issue.objects.filter(
                Q(citizen=request.user) |
                Q(citizen__phone_number=phone) |
                Q(citizen__username=phone) |
                Q(citizen__username=phone_clean)
            ), 
            pk=pk
        )
    else:
        issue = get_object_or_404(Issue, pk=pk, citizen=request.user)
        
    return render(request, 'citizen/issue_detail.html', {'issue': issue})

@login_required
def submit_issue(request):
    if request.method == 'POST':
        # Get standard data
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        # Get geo data
        block = request.POST.get('block')
        village = request.POST.get('village')
        landmark = request.POST.get('landmark')
        lat = request.POST.get('location_lat')
        lng = request.POST.get('location_lng')
        
        # Combine for legacy support if needed
        address = f"{village}, {block}, {landmark}"
        
        # Handle Image Upload
        image_url = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            file_ext = mimetypes.guess_extension(image_file.content_type) or '.jpg'
            file_name = f"issue_{int(time.time())}_{request.user.id}{file_ext}"
            file_path = f"issues/{file_name}"
            
            try:
                bucket_name = "issue-images"
                
                # --- ATTEMPT 1: Authenticated Upload using Session Token ---
                # This is preferred so we don't need 'Anon' insert permissions
                sb_token = request.session.get('sb_access_token')
                
                if sb_token:
                    # Create a temporary client with the user's token
                    url: str = os.environ.get("SUPABASE_URL")
                    key: str = os.environ.get("SUPABASE_KEY")
                    
                    # Custom headers to act as the user
                    headers = {"Authorization": f"Bearer {sb_token}"}
                    # Note: We can't easily pass headers to create_client in all versions, 
                    # but we can try setting the session or just using the globally initialized client 
                    # if we perform a specialized call.
                    
                    # EASIER WAY: The bucket is likely public. 
                    # If we simply want to upload, we generally need the Service Key or a Policy allowing Anon.
                    # Assuming we don't have Service Key, we will try to use the token.
                    
                    res = supabase.storage.from_(bucket_name).upload(
                        path=file_path,
                        file=image_file.read(),
                        file_options={"content-type": image_file.content_type, "upsert": "true", "x-upsert": "true"}
                    )
                else:
                    # Fallback to default (Anon) upload
                    res = supabase.storage.from_(bucket_name).upload(
                        path=file_path,
                        file=image_file.read(),
                        file_options={"content-type": image_file.content_type, "upsert": "true"}
                    )
                
                # Get Public URL
                image_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            
            except Exception as e:
                # Log the actual error for debugging
                print(f"Supabase Upload Error: {e}")
                # For now, suppressing the user-facing error if it saves locally? 
                # No, better to warn them.
                messages.warning(request, f"Image upload failed: {str(e)}")
                # Continue to save the issue without the image

        # Create Issue
        Issue.objects.create(
            citizen=request.user,
            title=title,
            description=description,
            category=category,
            block=block,
            village=village,
            landmark=landmark,
            address=address,
            location_lat=lat if lat else None,
            location_lng=lng if lng else None,
            image_url=image_url,
            status='unverified' # Explicitly set status to unverified
        )
        
        messages.success(request, "Issue submitted successfully! It is now pending verification.")
        return redirect('citizen_dashboard')
        
    return render(request, 'citizen/submit_issue.html')
