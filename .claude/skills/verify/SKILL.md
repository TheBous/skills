---
name: verify
description: Launch demo-shop (app.py, which reads prices from DATABASE_URL), open the product page in a real headless browser and capture screenshots at desktop and phone width. Use to prove any change to the page or to the prices it shows.
---

# Verify demo-shop

Run `scripts/verify.sh` from the project root. It checks its prerequisites (doctor), starts `app.py` on a free port, waits until the page answers, takes screenshots at desktop (1280x800) and phone (390x844) width, stops the server and prints the evidence folder.

Evidence goes to `.verify/evidence/<timestamp>/`: `desktop.png`, `phone.png`, `server.log`. It survives the run; the script stops only the server it started.

Journey: open `/`. The page shows the product, the price and the main button.
