from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from Cityplus.supabase_client import supabase
from django.contrib.auth import get_user_model

# Get the Django User model (we might still need to create a local user for DB consistency, 
# or strictly rely on session. For a hybrid approach, we sync.)
User = get_user_model()

# --- HELPER: Manage Django Session from Supabase Session ---
def create_django_session(request, supabase_response):
    """
    Stores Supabase session data into Django request.session
    and finds/creates a local Django User to keep ORM happy (optional but recommended).
    """
    user_data = supabase_response.user
    session_data = supabase_response.session
    
    # Store essential data in session
    request.session['sb_access_token'] = session_data.access_token
    request.session['sb_user_id'] = user_data.id
    request.session['sb_email'] = user_data.email
    request.session['sb_phone'] = user_data.phone

    # --- Sync with Local Django DB (Optional but good for ForeignKeys) ---
    # We use the Supabase UUID as username or similar
    # For Admin (Email)
    if user_data.email:
        username = user_data.email
        email = user_data.email
        role = 'admin' # Default to admin if logging in via email portal? Or check metadata
    # For Citizen (Phone)
    elif user_data.phone:
        username = user_data.phone
        email = ""
        role = 'citizen'
    else:
        username = user_data.id
        role = 'citizen'

    # Try to get or create local user
    try:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.email = email
            user.role = role
            user.save()
        
        # Log them in via Django's backend so decorators work
        from django.contrib.auth import login
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
    except Exception as e:
        print(f"Error syncing local user: {e}")

# --- ADMIN AUTH (Email + Password via Supabase) ---

def admin_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Supabase Auth
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Setup Session
            create_django_session(request, response)
            
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")
            
    return render(request, 'authentication/admin_login.html')


def admin_register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'authentication/admin_register.html')
            
        try:
            # Supabase Sign Up
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            # If auto-confirm is on, we might get a session immediately.
            # If email confirmation is required, we tell them to check email.
            if response.user and response.session:
                create_django_session(request, response)
                return redirect('admin_dashboard')
            elif response.user:
                messages.success(request, "Registration successful! Please check your email to confirm.")
                return redirect('admin_login')
                
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            
    return render(request, 'authentication/admin_register.html')


# --- CITIZEN AUTH (Phone + OTP via Supabase) ---

def login_view(request):
    """
    Handles Phone entry (send OTP) and OTP entry (verify).
    """
    
    # Check if we are in "Verify" step
    step = request.POST.get('step', 'phone')
    phone_context = request.POST.get('phone_number', '')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. SEND OTP
        if action == 'send_otp':
            phone = request.POST.get('phone_number')
            try:
                # Format phone to E.164 if needed, assuming input +91... or clean it
                # For now, pass as is, Supabase is picky about formats (e.g. +1234567890)
                
                # Supabase OTP Call
                supabase.auth.sign_in_with_otp({ 
                    "phone": phone 
                })
                
                messages.success(request, f"OTP sent to {phone}")
                return render(request, 'authentication/citizen_login.html', {'step': 'verify', 'phone': phone})
                
            except Exception as e:
                messages.error(request, f"Error sending OTP: {str(e)}")
                return render(request, 'authentication/citizen_login.html', {'step': 'phone'})

        # 2. VERIFY OTP
        elif action == 'verify_otp':
            phone = request.POST.get('phone_number')
            token = request.POST.get('otp')
            
            try:
                # Supabase Verify
                response = supabase.auth.verify_otp({
                    "phone": phone,
                    "token": token,
                    "type": "sms"
                })
                
                if response.user and response.session:
                    create_django_session(request, response)
                    return redirect('citizen_dashboard')
                else:
                    messages.error(request, "Verification failed (No session returned).")
                    
            except Exception as e:
                messages.error(request, f"Invalid OTP or expired: {str(e)}")
                return render(request, 'authentication/citizen_login.html', {'step': 'verify', 'phone': phone})

    return render(request, 'authentication/citizen_login.html', {'step': 'phone'})


def logout_view(request):
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()
    return redirect('index')

# Deprecated/Unused register view (since citizen is strictly phone login now)
def register_view(request):
    return redirect('login')
