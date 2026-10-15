"""
QR Code Login Helper for Telegram.

Bypasses SMS and OTP code issues completely.
Generates an HTML page with a QR code — simply scan it in:
Telegram -> Settings -> Devices -> Link Desktop Device.
"""

import asyncio
import os
import webbrowser
from telethon import TelegramClient
from config import API_ID, API_HASH


async def main():
    print("\n" + "=" * 50)
    print("📱 Telegram QR Code Login")
    print("=" * 50)

    client = TelegramClient("user_session", API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n✅ You are ALREADY logged in as: {me.first_name} (@{me.username or 'N/A'})")
        print("You can directly run: python main.py\n")
        await client.disconnect()
        return

    qr_login = await client.qr_login()
    print("\n⏳ Generating QR code...")

    # Generate a lightweight HTML page that renders the QR code locally
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Telegram QR Login</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: #0f172a;
            color: #f8fafc;
        }}
        .card {{
            background: #1e293b;
            padding: 30px 40px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            text-align: center;
        }}
        #qrcode {{
            margin: 20px auto;
            padding: 16px;
            background: white;
            border-radius: 12px;
            display: inline-block;
        }}
        ol {{
            text-align: left;
            line-height: 1.8;
            margin-top: 15px;
            font-size: 15px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h2>📱 Scan to Log In</h2>
        <div id="qrcode"></div>
        <ol>
            <li>Open <b>Telegram</b> on your phone</li>
            <li>Go to <b>Settings</b> &rarr; <b>Devices</b></li>
            <li>Tap <b>Link Desktop Device</b></li>
            <li>Point your camera at this QR code</li>
        </ol>
    </div>
    <script>
        new QRCode(document.getElementById("qrcode"), {{
            text: "{qr_login.url}",
            width: 256,
            height: 256
        }});
    </script>
</body>
</html>"""

    html_path = os.path.abspath("login_qr.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n🌐 Opening QR code in your browser...")
    webbrowser.open(f"file://{html_path}")

    print("\n👉 On your phone:")
    print("   1. Open Telegram")
    print("   2. Go to Settings -> Devices")
    print("   3. Tap 'Link Desktop Device'")
    print("   4. Scan the QR code shown in your browser\n")
    print("Waiting for scan...")

    try:
        await qr_login.wait(timeout=120)
        me = await client.get_me()
        print(f"\n🎉 Successfully logged in as: {me.first_name} (@{me.username or 'N/A'})!")
        print("Your session is saved. You can now run:\n   python main.py\n")
    except Exception as e:
        print(f"\n❌ Login timed out or failed: {e}")
        print("Run 'python login_qr.py' to try again.")
    finally:
        # Clean up temporary HTML file
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
            except Exception:
                pass
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
