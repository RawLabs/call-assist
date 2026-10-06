# CallAssist

A configurable phone intake prototype for small businesses or personal lines.
It collects a caller's name, callback number, and request, selects a configured
department, and stores a transcript and summary in SQLite. Optional context such
as account numbers, property details, or vehicle information fits in `details`.

This is a terminal/microphone prototype. There is no VoIP/SIP connection, real
call transfer, appointment booking, or message delivery integration yet.

## Quick start

After [installation](#installation), open the demo menu:

```sh
python app.py
```

1. Choose **1) Sales inquiry demo**, **2) Support message demo**, or
   **3) Appointment request demo** to watch a scripted intake.
2. Choose **4) Interactive text demo** to type the caller's answers yourself.
3. Read the final department and callback/intake summary, then press Enter to
   return to the menu. Choose **6) Exit** when finished.

The text demos use a deterministic mock model and need no live model server.
Microphone sessions need the separate [voice setup](#microphone-and-model-setup).

## Installation

Use Python 3.10 or newer:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The menu includes scripted and interactive text demos using a deterministic mock
model. Those demos need only `pydantic` and `rich`; tests also need `pytest`.
The mock handles simple keywords and names, not arbitrary natural language.

## Microphone and model setup

For microphone input:

```sh
python app.py --voice
```

Voice mode defaults to faster-whisper (`tiny`), pyttsx3, and an OpenAI-compatible
LLM server at `http://localhost:1234/v1` (e.g. LM Studio). It requires a working
microphone, audio output, native audio/TTS dependencies, and a running model
server. Whisper may download its model on first use.

## Customize the business

```sh
cp business.example.json business.json
BUSINESS_PROFILE=business.json python app.py
```

Edit the name, description, confirmed hours, and department descriptions. With
no profile, CallAssist uses neutral defaults and does not invent opening hours.
Both model prompts and controller routing use the profile. Industry-specific
fields are optional context, never mandatory automotive intake requirements.
The mock recognizes department names and basic sales/support/appointment
keywords; live models also receive the department descriptions.

Other environment settings: `LLM_TYPE` (`mock`, `openai_compatible`, `gemini`),
`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `STT_TYPE` (`mock`, `whisper`),
`STT_WHISPER_MODEL`, `TTS_TYPE` (`mock`, `pyttsx3`), `VAD_THRESHOLD`, and `DB_PATH`.
The default database is `calls.db`. Existing logs remain readable; newly saved
state uses generic fields. Databases, credentials, and recorded audio are
excluded from Git.

A caller can say `operator`, `human`, `person`, or `help me please` to request a
human. Repeated silence or failed clarification also saves a human fallback
request. This records a destination; it does not transfer a real call.

## Tests

```sh
python -m pytest -q
```
