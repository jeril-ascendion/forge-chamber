# Forge Chamber — Installation Guide

## System Requirements

- Windows 10 or Windows 11 (64-bit)
- 8 GB RAM minimum (16 GB recommended)
- 2 GB free disk space
- Microphone (built-in or external)
- Internet connection (for AI services)

## Download

Download the latest release from GitHub Releases:

**https://github.com/jeril-ascendion/forge-chamber/releases/latest**

You will find one file:
- `Forge-Chamber-1.0.0.exe` — Portable executable (no installer needed)

## Windows SmartScreen Warning

Because the app is not yet code-signed, Windows SmartScreen will show a warning the first time you run it. This is expected.

### For the .exe file:

1. Double-click `Forge-Chamber-1.0.0.exe`
2. SmartScreen shows "Windows protected your PC"
3. Click **"More info"**
4. Click **"Run anyway"**

### If you downloaded a .zip file:

Before extracting, you must unblock the zip:

1. Right-click the `.zip` file
2. Select **Properties**
3. At the bottom, check **"Unblock"**
4. Click **Apply**, then **OK**
5. Now extract the zip and run the exe inside

If you skip the unblock step, every file inside the zip will be individually blocked by Windows.

## First Launch

When you start Forge Chamber for the first time:

1. **Loading screen** — The backend engine starts up (takes 10-30 seconds on first launch)
2. **Onboarding** — You will be asked for:
   - **Your name** — Displayed in the app
   - **Your role** — Your engineering track (e.g., Backend, Frontend, Full Stack, SRE, Cloud)
   - **Skill level** — Junior, Mid, Senior, or Staff
   - **API Keys** — You need at least:
     - `ANTHROPIC_API_KEY` or `GROQ_API_KEY` — For AI agents
     - `DEEPGRAM_API_KEY` — For speech-to-text
     - `CARTESIA_API_KEY` — For text-to-speech
     - `LIVEKIT_API_KEY` + `LIVEKIT_API_SECRET` — For voice rooms
3. **Dashboard** — Once onboarding is complete, you're in. Pick a topic and start a room.

## Troubleshooting

### App does not start / closes immediately

- Make sure you are running the correct `.exe` file (not a zip)
- Check if Windows Defender or your antivirus is quarantining the file — add an exception for Forge Chamber
- Try running as Administrator (right-click > Run as administrator)
- Check the log file at `%APPDATA%/forge-chamber/logs/` for error details

### SmartScreen keeps blocking it

- Make sure you unblocked the zip file before extracting (see above)
- If the exe is still blocked: right-click the exe > Properties > check "Unblock" > Apply

### No audio / microphone not working

- Check that your microphone is connected and set as default in Windows Sound Settings
- Grant microphone permission when the app requests it
- Make sure no other app (Teams, Zoom) is exclusively holding the microphone
- Check that your `DEEPGRAM_API_KEY` and `CARTESIA_API_KEY` are valid

### Backend engine fails to start

- The backend needs port 8765 to be available. Check if something else is using it:
  ```
  netstat -ano | findstr :8765
  ```
- If another process is using the port, close it or restart your machine

### "API key invalid" errors

- Double-check your API keys in Settings
- Make sure there are no extra spaces or newlines in the key values
- Verify your keys are active and have remaining credits on each provider's dashboard
