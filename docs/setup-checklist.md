# Setup checklist

Steps that need your own accounts and payment. Expect about 3–4 hours in total.

## Demo line

1. Pick one voice-AI platform. Compare a white-label plan (for example Trillet Studio, $99/month for up to 3 client workspaces) with one platform that offers a free trial. Check current terms before paying.
2. Get a local 425 phone number in the platform for the demo.
3. Run `python tools/render_agent.py examples/clients/cascade-gutter-pros.json` and paste the output into a new agent.
4. Turn on call recording and confirm the greeting includes the recording notice.
5. Send the owner text alert to your own phone so you see what clients will get.
6. Make a free booking page (Google Calendar appointment schedule or a free Calendly plan) and add its link to the client file.
7. Call the demo line 10 times: a normal quote, an angry caller, an emergency leak, someone who wants a human, and a spam call. Fix anything that sounds wrong.
8. Record one clean demo call to play for contractors.

## Each pilot client

1. Have them sign the pilot agreement (`docs/pilot-agreement.md`).
2. Create a client file in `clients/` (keep real client files out of public repos) and render their prompt.
3. Have them turn on no-answer call forwarding from their business line to the AI number. Their carrier explains how.
4. Test three calls together before going live.
5. Review every call after 3 days and tune the script.

## Before charging anyone

- Register with Washington's Business Licensing Service.
- Get a general liability insurance quote.
- Have a lawyer review the pilot agreement.
- Register business text messaging with your platform (often called 10DLC registration).
