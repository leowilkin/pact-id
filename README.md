# 📞 PaCT ID - Personal and Cheap International Dialling

**PaCT ID** is a Twilio-powered local-to-international calling bridge. It allows you to call and receive calls across borders using local Twilio numbers while preserving caller IDs — with a handy PWA frontend for mobile dialing.

---

## 🌍 How It Works

- **Inbound Calls from Others**  
  - If someone calls your **US Twilio number**, it's forwarded to your **UK personal number** via your **UK Twilio number**, showing the original US caller ID.
  - If someone calls your **UK Twilio number**, it's forwarded to your **US personal number** via your **US Twilio number**, showing the original UK caller ID.

- **Outbound Calls from You**  
  - If *you* call the **UK Twilio number**, you're prompted to enter a number (e.g., a US number), and it connects using your **US Twilio number**, showing your personal UK number as caller ID.
  - If *you* call the **US Twilio number**, you're prompted to enter a number (e.g., a UK number), and it connects using your **UK Twilio number**, showing your personal US number as caller ID.

---

## ✅ Features

- Local-to-international call bridging
- Full preservation of original caller IDs
- Web-based PWA dialler interface - [hosted seperately](https://github.com/leowilkin/pactid-pwa)
- Secure Cloudflare Tunnel support
- Call normalisation (07 and +44 formats accepted)
- Configurable via environment variables

---

## 🛠 Prerequisites

- A Linux VPS (e.g. Ubuntu 22.04 or later)
- Python 3.8+ installed
- `cloudflared` for secure tunnel to Twilio
- Two Twilio phone numbers (1x US, 1x UK)
- Your personal phone number(s) in both regions

---

## 🔧 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/leowilkin/pactid.git
cd pactid
```

### 2. Set up virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create a `.env` file

```bash
nano .env
```

Example:

```env
US_TWILIO_NUMBER=+18012345678
UK_TWILIO_NUMBER=+447123456789
PERSONAL_UK=+447123456789
PERSONAL_US=+18012345678

# Optional feature flag
ENABLE_US_PERSONAL_ROUTING=true
```

### 4. Create systemd Service

```bash
sudo nano /etc/systemd/system/twilio.service
```

Paste:

```ini
[Unit]
Description=PaCT ID Twilio Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/twilio
ExecStart=/opt/twilio/bin/python /opt/twilio/bridge.py
Restart=always
EnvironmentFile=/opt/twilio/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable twilio
sudo systemctl start twilio
```

## 🌐 Configure Cloudflare Tunnel

1. Go to [dash.cloudflare.com](dash.cloudflare.com), and enter Zero Trust
2. Networks > Tunnels
3. Create a new tunnel > Cloudflared > name your tunnel
4. Debian > 64-bit
5. Copy and paste the install code into your terminal
6. Once completed, copy and paste the activation code into your terminal
7. Next > configure public hostname as twilio.yourdomain.com, and save

## 🔁 Configure Twilio Webhooks

> [!IMPORTANT]  
> You cannot be on a trial account, as you have to have two numbers.

Set the following webhook URLs for your Twilio numbers:

| Number Type |               Webhook URL              |
|-------------|:--------------------------------------:|
| US Number   | https://twilio.yourdomain.com/voice_us |
| UK Number   | https://twilio.yourdomain.com/voice_uk |

These should be set as the Voice & Fax > A Call Comes In handler (Webhook + TwiML).

## 📱 Using the PWA Dialler

Head on over to [leowilkin/pactid-pwa](github.com/leowilkin/pactid-pwa) to find out more.

## View Logs

To view the access logs for the service, on your terminal do:

```bash
journalctl -u twilio.service -f
```

## Testing

### Outbound

https://thetestcall.blogspot.com/

### Inbound

Find a friend!
