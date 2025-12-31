from django.utils import timezone
from .models import OTPVerification
from Cityplus.supabase_client import supabase

def send_otp(phone_number):
    """
    Triggers Supabase to send an OTP via Twilio to the user's phone.
    Also creates a local placeholder record for tracking purposes (optional).
    """
    try:
        # Supabase handles Generation & Sending
        response = supabase.auth.sign_in_with_otp({
            "phone": phone_number
        })
        
        # We don't get the code back, so we cannot return it.
        # We assume success if no exception raised.
        
        # (Optional) Store audit log that OTP was requested
        OTPVerification.objects.create(
            phone_number=phone_number,
            otp_code="SUPABASE_HANDLED", 
            expiration_time=timezone.now() + timezone.timedelta(minutes=5),
            is_verified=False
        )
        
        return "SENT_VIA_SUPABASE"
        
    except Exception as e:
        print(f"Error sending OTP via Supabase: {e}")
        return None
