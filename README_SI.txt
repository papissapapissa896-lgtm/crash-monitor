Crash Monitor - Starter package

මෙය mobile-friendly dashboard එකක් සහ SQLite round history එකක්.

Lunafy/Pterodactyl startup command:
  python app.py

Python 3 server environment එකක් තෝරාගන්න. Dependencies:
  pip install -r requirements.txt

Port:
  8080 (PORT environment variable එකෙන් වෙනස් කළ හැක)

Dashboard routes:
  /         - Dashboard
  /api/health - Health check
  /api/stats  - Stats and latest stored rounds
  POST /api/rounds - Manual round add endpoint (JSON: multiplier, note)

IMPORTANT:
- 1xBet live feed එක මේ package එකට connect කරලා නැහැ. Live feed endpoint එක තහවුරු කර නැති නිසා fake/live ලෙස නොපෙන්වයි.
- Multiplier එක manually add කළ හැක. Statistics stored/manual data වලට පමණි.
- මේ app එක ඊළඟ crash multiplier එක predict කරන්නේ නැහැ. Gambling risk පවතී.
