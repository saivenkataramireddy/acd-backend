from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.event import EventCreate, EventResponse
from app.services.event_processor import process_emergency_event
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter()

def trigger_emergency_cascade(event_id: str, lat: float, lon: float, user_full_name: str = "A User", contacts: list = None):
    # This is a background task function that processes notifications asynchronously
    # to avoid holding up the HTTP response
    import os
    print(f"Starting emergency cascade for event {event_id} at {lat}, {lon}...")
    
    if contacts:
        tw_sid = os.getenv("TWILIO_ACCOUNT_SID")
        tw_token = os.getenv("TWILIO_AUTH_TOKEN")
        tw_from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        tw_from_sms = os.getenv("TWILIO_SMS_FROM")
        
        name = user_full_name if user_full_name else "A User"
        message_body = f"EMERGENCY ALERT: This is an automated message from {name}. I have been involved in an emergency! Location: https://maps.google.com/?q={lat},{lon}"
        
        for contact in contacts:
            # Clean number to digits only, then format if not using explicit '+'
            clean_num = ''.join(filter(str.isdigit, contact))
            to_num_wa = f"whatsapp:+{clean_num}" if not contact.startswith("whatsapp:") else contact
            to_num_sms = f"+{clean_num}"
            
            if tw_sid and tw_token:
                try:
                    from twilio.rest import Client
                    client = Client(tw_sid, tw_token)
                    
                    # 1. Send WhatsApp
                    msg_wa = client.messages.create(
                        from_=tw_from_whatsapp,
                        body=message_body,
                        to=to_num_wa
                    )
                    print(f"Successfully sent Twilio WhatsApp to {to_num_wa}: {msg_wa.sid}")
                    
                    # 2. Send Standard SMS
                    if tw_from_sms:
                        msg_sms = client.messages.create(
                            from_=tw_from_sms,
                            body=message_body,
                            to=to_num_sms
                        )
                        print(f"Successfully sent Twilio SMS to {to_num_sms}: {msg_sms.sid}")
                    else:
                        print(f"Skipped SMS for {to_num_sms} because TWILIO_SMS_FROM is not set.")
                        
                except Exception as e:
                    print(f"Failed to send Twilio message to {contact}: {e}")
            else:
                # Mock sending for local dev when keys aren't set
                print(f"[MOCK TWILIO API] Successfully sent WhatsApp & SMS securely in background to {clean_num}")
                print(f"[MOCK MESSAGE BODY]: {message_body}")

@router.post("/create", response_model=EventResponse)
async def create_event(
    payload: EventCreate, 
    background_tasks: BackgroundTasks, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ Submits a manual or automated SOS. Responds immediately; delegation happens async. """
    response = await process_emergency_event(db, payload, user)
    
    if response["status"] == "created":
        background_tasks.add_task(
            trigger_emergency_cascade, 
            response["id"], 
            payload.lat, 
            payload.lon,
            payload.userFullName,
            payload.contacts
        )
        
    return response
