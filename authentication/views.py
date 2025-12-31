from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from Cityplus.supabase_client import supabase
from django.contrib.auth import get_user_model, authenticate, login
from django.utils import timezone
from .utils import send_otp
from .models import OTPVerification, LoginAttempt

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


# --- CITIZEN AUTH (Custom Flow) ---

def citizen_auth_start(request):
    """
    Step 1: User enters Phone.
    - If Registered: Redirect to Login.
    - If Not Registered (or New): Send OTP -> Redirect to Verify.
    """
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        
        # Check if user exists
        user_qs = User.objects.filter(phone_number=phone)
        if user_qs.exists():
            user = user_qs.first()
            if user.is_registered:
                messages.info(request, "Account exists. Please log in.")
                return redirect('citizen_login')
            else:
                # Exists but not registered (maybe dropped off?)
                send_otp(phone)
                # messages.warning(request, f"DEBUG: Your OTP is {otp}") -- Removed for Production
                return redirect('verify_otp', phone=phone)
        else:
            # New User
            send_otp(phone)
            # messages.warning(request, f"DEBUG: Your OTP is {otp}") -- Removed for Production
            return redirect('verify_otp', phone=phone)

    return render(request, 'authentication/auth_start.html')

def verify_otp_view(request, phone):
    """
    Step 2: Verify OTP via Supabase.
    """
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        
        try:
            # Supabase Verify
            response = supabase.auth.verify_otp({
                "phone": phone,
                "token": otp_input,
                "type": "sms"
            })
            
            if response.user and response.session:
                # OPTIONAL: Sync Session or just trust the flow
                # create_django_session(request, response) 
                
                request.session['verified_phone'] = phone
                return redirect('set_credentials')
            else:
                messages.error(request, "Verification failed (No session returned).")
                
        except Exception as e:
            messages.error(request, f"Invalid OTP or expired: {str(e)}")
    
    return render(request, 'authentication/verify_otp.html', {'phone_number': phone})

def set_credentials_view(request):
    """
    Step 3: Set Username & Password.
    """
    phone = request.session.get('verified_phone')
    if not phone:
        return redirect('citizen_auth_start')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'authentication/set_credentials.html')
            
        # Database Check: Username Uniqueness
        # We must exclude the current user (self) in case they are retrying or updating
        current_user_qs = User.objects.filter(phone_number=phone)
        username_check = User.objects.filter(username=username)
        
        if current_user_qs.exists():
            username_check = username_check.exclude(pk=current_user_qs.first().pk)
            
        if username_check.exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'authentication/set_credentials.html')
            
        # Create or Update User
        if current_user_qs.exists():
            user = current_user_qs.first()
            user.username = username
            user.set_password(password)
            user.is_registered = True
            user.role = 'citizen'
            user.save()
        else:
            user = User.objects.create_user(
                username=username, 
                password=password, 
                phone_number=phone, 
                role='citizen',
                is_registered=True
            )
            
        # Login and Redirect
        login(request, user)
        del request.session['verified_phone'] # Cleanup
        return redirect('citizen_dashboard') # Assuming URL name

    return render(request, 'authentication/set_credentials.html')

def citizen_login_view(request):
    """
    Step 4: Returning User Login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_citizen:
                login(request, user)
                
                # Log attempt
                LoginAttempt.objects.create(user=user, ip_address=request.META.get('REMOTE_ADDR'), successful=True)
                
                return redirect('citizen_dashboard')
            else:
                messages.error(request, "Access denied. Not a citizen account.")
        else:
            # Log failed attempt if username exists??
            messages.error(request, "Invalid credentials.")
            
    return render(request, 'authentication/citizen_login.html')

def logout_view(request):
    try:
        supabase.auth.sign_out()
    except:
        pass
    
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()
    return redirect('citizen_auth_start') # Redirect to start

# Deprecated
def register_view(request):
    return redirect('citizen_auth_start')
