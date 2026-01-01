# FastAPI Twilio-ElevenLabs Webhook

A FastAPI webhook server that handles inbound Twilio calls and connects them to ElevenLabs conversational AI agents.

## Setup on Replit

1. **Import this repository** into Replit

2. **Set Environment Variables**:
   - Click on the "Secrets" tab (lock icon) in Replit
   - Add the following secrets:
     - `AGENT_ID`: Your ElevenLabs agent ID
     - `XI_API_KEY`: Your ElevenLabs API key
     - `PORT`: (Optional) Port number (defaults to 8000)

3. **Install Dependencies**:
   - Replit should automatically install dependencies from `requirements.txt`
   - If not, run: `pip install -r requirements.txt`

4. **Run the Server**:
   - Click the "Run" button in Replit
   - The server will start on the configured port

5. **Get Your Webhook URL**:
   - Replit provides a public URL in the format: `https://your-repl-name.your-username.repl.co`
   - Your webhook endpoint will be: `https://your-repl-name.your-username.repl.co/inbound-call`

6. **Configure Twilio**:
   - In your Twilio console, set the webhook URL for your phone number to:
     - `https://your-repl-name.your-username.repl.co/inbound-call`
   - Set the HTTP method to `POST`

## Endpoints

- `POST /inbound-call`: Handles inbound Twilio calls and connects them to ElevenLabs
- `GET /`: Health check endpoint

## Environment Variables

- `AGENT_ID`: Your ElevenLabs agent ID
- `XI_API_KEY`: Your ElevenLabs API key
- `PORT`: Server port (default: 8000)

## Notes

- The server uses environment variables for sensitive configuration
- Make sure to keep your API keys secure using Replit's Secrets feature
- The webhook handles form-encoded data from Twilio

