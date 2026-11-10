import hmac
import hashlib
import json
import base64
import io
import qrcode

SECRET_KEY = "eventsphere-super-secure-campus-secret-key-2026"

def generate_qr_token(registration_code, roll_no, event_id):
    """
    Creates an authenticated QR pass payload with HMAC SHA-256 integrity signature.
    """
    payload_data = f"{registration_code}:{roll_no}:{event_id}"
    signature = hmac.new(SECRET_KEY.encode(), payload_data.encode(), hashlib.sha256).hexdigest()[:12]
    qr_token = f"ESPASS:{registration_code}:{roll_no}:{event_id}:{signature}"
    return qr_token

def parse_and_verify_qr_token(token_str):
    """
    Parses token string and validates HMAC signature.
    Returns (is_valid, data_dict, error_message)
    """
    if not token_str or not isinstance(token_str, str):
        return False, None, "Empty QR token"
    
    parts = token_str.strip().split(':')
    # Can accept full format ESPASS:REG_CODE:ROLL_NO:EVENT_ID:SIG
    if len(parts) == 5 and parts[0] == "ESPASS":
        reg_code, roll_no, event_id_str, sig = parts[1], parts[2], parts[3], parts[4]
        try:
            event_id = int(event_id_str)
        except ValueError:
            return False, None, "Invalid event ID format in pass"
        
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{reg_code}:{roll_no}:{event_id}".encode(),
            hashlib.sha256
        ).hexdigest()[:12]

        if not hmac.compare_digest(sig, expected_sig):
            return False, None, "Pass signature tampered or invalid"
        
        return True, {
            "registration_code": reg_code,
            "roll_no": roll_no,
            "event_id": event_id
        }, None
    
    # Also support direct registration code lookup (e.g. REG-XXXXX or ES-XXXXX) for manual entry fallback
    if token_str.startswith("ES-") or token_str.startswith("REG-"):
        return True, {
            "registration_code": token_str.strip(),
            "roll_no": None,
            "event_id": None
        }, None

    return False, None, "Unrecognized QR pass format"

def generate_qr_image_base64(qr_token):
    """
    Generates a crisp PNG QR code image as a base64 Data URL.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(qr_token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E293B", back_color="#FFFFFF")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

