"""
╔══════════════════════════════════════════════════════════════╗
║     NET-FIRE-MONITOR  v3.9.3 –  Notfall-Admin (Sync-Update)  ║
║     Master-Kontrolle mit Echtzeit-Synchronisation            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys, os, platform, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import core as _core
from core import FirewallEngine, validate_ip, PERSIST_FILE, CommandQueue

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    from rich.prompt import Confirm, Prompt
    from rich.text import Text
except ImportError:
    sys.exit("Bitte 'pip install rich' ausführen.")

console = Console()

def check_root():
    if platform.system() != "Windows" and os.geteuid() != 0:
        console.print("[bold red]❌ Root-Rechte erforderlich.[/bold red]"); sys.exit(1)

def notify_monitor():
    """Informiert den laufenden Monitor über Änderungen."""
    CommandQueue.push({"action": "reload_config"})

def get_current_blocks():
    if PERSIST_FILE.exists():
        try: return json.loads(PERSIST_FILE.read_text(encoding="utf-8")).get("blocked_ips", [])
        except Exception: pass
    return []

def list_blocks():
    blocks = get_current_blocks()
    if not blocks:
        console.print("\n[green]✅ Keine IPs blockiert.[/green]"); return
    table = Table(title="Aktive Firewall-Sperren", box=box.HEAVY)
    table.add_column("Nr.", justify="right", style="dim")
    table.add_column("IP-Adresse", style="bold red")
    table.add_column("Status", justify="center")
    for i, ip in enumerate(blocks, 1):
        table.add_row(str(i), ip, "🚫 GESPERRT")
    console.print(table)

def process_command(cmd_input):
    parts = cmd_input.strip().split()
    if not parts: return True
    cmd = parts[0].lower()
    
    if cmd == "list":
        list_blocks()
    
    elif cmd == "block" and len(parts) == 2:
        ip = parts[1]
        if not validate_ip(ip):
            console.print(f"[red]❌ Ungültige IP[/red]"); return True
        fw = FirewallEngine()
        _core._firewall = fw
        fw.block_ip(ip, reason="Manuell via Notfall-Admin")
        time.sleep(1.0)
        _core.save_persist()
        notify_monitor() # Monitor informieren
        console.print(f"[bold green]✅ {ip} gesperrt und Monitor informiert.[/bold green]")

    elif cmd == "unblock" and len(parts) == 2:
        ip = parts[1]
        blocks = get_current_blocks()
        if ip in blocks:
            fw = FirewallEngine()
            fw.blocked_ips = set(blocks)
            fw.unblock_ip(ip)
            _core._firewall = fw
            time.sleep(1.0)
            _core.save_persist()
            notify_monitor() # Monitor informieren
            console.print(f"[bold green]✅ {ip} entsperrt und Monitor informiert.[/bold green]")
        else:
            console.print(f"[yellow]⚠️ IP nicht gefunden.[/yellow]")

    elif cmd == "clear":
        if Confirm.ask("[bold red]Wirklich alles löschen?[/bold red]"):
            fw = FirewallEngine()
            _core._firewall = fw
            fw.cleanup_all()
            time.sleep(1.2)
            _core.save_persist()
            notify_monitor()
            console.print("[bold green]✅ Alle Regeln entfernt.[/bold green]")

    elif cmd in ("exit", "quit", "q"): return False
    return True

def main():
    check_root()
    # Willkommens-Anzeige ...
    console.print(Panel("Net-Fire-Monitor Notfall-Admin v3.9.3", style="bold blue"))
    console.print("Befehle: [cyan]list, block <IP>, unblock <IP>, clear, exit[/cyan]")

    running = True
    while running:
        try:
            user_input = Prompt.ask("\n[bold blue]nfm-admin[/bold blue]")
            running = process_command(user_input)
        except KeyboardInterrupt: running = False

if __name__ == "__main__":
    main()