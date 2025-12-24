import subprocess
import sys


producers =[
    "atm_transactions.py",
    "bank_transfer.py",
    "mobile_payments.py",
    "pos_terminals.py",
    "web_checkout.py"
]

processes =[]

print(f"Starting {len(producers)} producers...")

for script in producers:
    # This launches each script in its own background process
    p = subprocess.Popen([sys.executable, script])
    processes.append(p)

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\nStopping all producers...")
    for p in processes:
        p.terminate()