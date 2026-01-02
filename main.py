from fastapi import FastAPI, Request, Response
import os
import httpx
import uvicorn

app = FastAPI()

# Configuration
AGENT_ID = os.getenv("AGENT_ID", "agent_6601kc8yp37een4smehwxjz1q037")
XI_API_KEY = os.getenv("XI_API_KEY", "YOUR_XI_API_KEY")
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/convai/twilio/register-call"

@app.post("/inbound-call")
async def handle_inbound_call(request: Request):
    # 1. Capture Twilio metadata
    form_data = await request.form()
    caller_number = form_data.get("From")
    destination_number = form_data.get("To")

    # 2. Setup initiation data with empty strings
    # IMPORTANT: Ensure EVERY variable in your agent is listed here.
    # If even one variable is missing, ElevenLabs will return a 422 error.
    payload = {
        "agent_id": AGENT_ID,
        "from_number": caller_number,
        "to_number": destination_number,
        "direction": "inbound",
        "conversation_initiation_client_data": {
            "dynamic_variables": {
                "procedure_name": " ",
                "mrn": " ",
                "patient_id": " ",
                "patient_insurance_member_id": " ",
                "patient_email": " ",
                "patient_appointment_type": " ",
                "patient_address": " ",
                "patient_dob": " ",
                "referring_physician_first_name": " ",
                "referring_physician_last_name": " ",
                "patient_name": " ",
                "patient_insurance_name": " "
            }
        }
    }

    headers = {
        "xi-api-key": XI_API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ELEVENLABS_URL, json=payload, headers=headers)
            
            # 3. Handle Success
            if response.status_code == 200:
                # Returns the TwiML XML to Twilio
                return Response(content=response.text, media_type="text/xml")
            
            # 4. Handle Failure (Validation Error 422 or Auth Error 401)
            else:
                # Check your Replit console to see the exact error from ElevenLabs
                print(f"ElevenLabs Error ({response.status_code}): {response.text}")
                return Response(
                    content="<Response><Say>Connection error. Check console logs.</Say></Response>", 
                    media_type="text/xml"
                )
        except Exception as e:
            print(f"Network Error: {str(e)}")
            return Response(content="<Response><Say>Network error.</Say></Response>", media_type="text/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)