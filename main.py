from fastapi import FastAPI, Request, Response
import uvicorn
import os
from elevenlabs import ElevenLabs
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# Your ElevenLabs Configuration
AGENT_ID = os.getenv("AGENT_ID", "agent_6601kc8yp37een4smehwxjz1q037")
XI_API_KEY = os.getenv("XI_API_KEY", "YOUR_XI_API_KEY")

# Initialize ElevenLabs client
client = ElevenLabs(
    api_key=XI_API_KEY,
    base_url="https://api.elevenlabs.io/"
)

# Thread pool executor for running synchronous SDK calls
executor = ThreadPoolExecutor(max_workers=5)

@app.post("/inbound-call")
async def handle_inbound_call(request: Request):
    # 1. Identify the user number dynamically
    # Twilio sends data as form-encoded, so we get it from request.form()
    form_data = await request.form()
    caller_number = form_data.get("From")  # This is the person calling you
    destination_number = form_data.get("To") # This is your Twilio number

    # 2. Prepare the conversation initiation data with empty values
    # This ensures the call goes through even if CRM data is missing
    conversation_initiation_client_data = {
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

    # 3. Call ElevenLabs to register the session using the SDK
    try:
        # Run the synchronous SDK call in a thread pool
        loop = asyncio.get_event_loop()
        twiml_response = await loop.run_in_executor(
            executor,
            lambda: client.conversational_ai.twilio.register_call(
                agent_id=AGENT_ID,
                from_number=caller_number,
                to_number=destination_number,
                direction="inbound",
                conversation_initiation_client_data=conversation_initiation_client_data
            )
        )
        
        # 4. ElevenLabs returns TwiML (XML)
        # Send this XML directly back to Twilio to connect the call
        return Response(content=twiml_response, media_type="text/xml")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(
            content="<Response><Say>Error connecting to agent.</Say></Response>",
            media_type="text/xml"
        )

@app.get("/")
async def root():
    return {"message": "FastAPI webhook server is running", "status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

