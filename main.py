from fastapi import FastAPI, Request, Response
import uvicorn
import os
import httpx
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
        # Check if API key is set
        if XI_API_KEY == "YOUR_XI_API_KEY" or not XI_API_KEY:
            print("ERROR: XI_API_KEY is not set in environment variables!")
            return Response(
                content="<Response><Say>Configuration error. Please check API key.</Say></Response>",
                media_type="text/xml"
            )
        
        # Run the synchronous SDK call in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: client.conversational_ai.twilio.register_call(
                agent_id=AGENT_ID,
                from_number=caller_number,
                to_number=destination_number,
                direction="inbound",
                conversation_initiation_client_data=conversation_initiation_client_data
            )
        )
        
        # Handle different return types from SDK
        # The SDK might return a string, response object, or dict
        if isinstance(result, str):
            twiml_response = result
        elif hasattr(result, 'text'):
            twiml_response = result.text
        elif hasattr(result, 'content'):
            twiml_response = result.content
        elif isinstance(result, dict) and 'twiml' in result:
            twiml_response = result['twiml']
        else:
            # Try to convert to string
            twiml_response = str(result)
        
        print(f"Successfully got TwiML response: {twiml_response[:200]}...")
        
        # 4. ElevenLabs returns TwiML (XML)
        # Send this XML directly back to Twilio to connect the call
        return Response(content=twiml_response, media_type="text/xml")
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"SDK Error details: {error_details}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Fallback to HTTP method if SDK fails
        print("Attempting fallback to HTTP method...")
        try:
            ELEVENLABS_URL = "https://api.elevenlabs.io/v1/convai/twilio/register-call"
            payload = {
                "agent_id": AGENT_ID,
                "from_number": caller_number,
                "to_number": destination_number,
                "direction": "inbound",
                "conversation_initiation_client_data": conversation_initiation_client_data
            }
            headers = {
                "xi-api-key": XI_API_KEY,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(ELEVENLABS_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    print("Fallback HTTP method succeeded!")
                    return Response(content=response.text, media_type="text/xml")
                else:
                    print(f"HTTP fallback failed with status {response.status_code}: {response.text}")
                    return Response(
                        content="<Response><Say>Error connecting to agent. Please check logs.</Say></Response>",
                        media_type="text/xml"
                    )
        except Exception as fallback_error:
            print(f"Fallback also failed: {str(fallback_error)}")
            return Response(
                content="<Response><Say>Error connecting to agent. Please check configuration.</Say></Response>",
                media_type="text/xml"
            )

@app.get("/")
async def root():
    return {"message": "FastAPI webhook server is running", "status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

