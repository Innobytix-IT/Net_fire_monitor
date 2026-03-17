# Net-Fire-Monitor v3.9

> **(C) 2023–2026 Manuel Person – Innobytix-IT**

---

> 🇩🇪 **Diese README ist zweisprachig. Der deutsche Teil befindet sich zuerst, der englische Teil folgt im Anschluss.**
> 🇬🇧 **This README is bilingual. The German section comes first, the English section follows below.**

---

# 🇩🇪 DEUTSCH

---

## Inhaltsverzeichnis

1. [Was ist Net-Fire-Monitor?](#was-ist-net-fire-monitor)
2. [Was ist neu in v3.9?](#was-ist-neu-in-v39)
3. [Architektur (Zwei-Prozess-Modell)](#architektur-zwei-prozess-modell)
4. [Voraussetzungen](#voraussetzungen)
5. [Installation](#installation)
6. [Start & Betrieb](#start--betrieb)
7. [Web-Interface](#web-interface)
8. [E-Mail-Passwort sicher einrichten](#e-mail-passwort-sicher-einrichten)
9. [Konfiguration](#konfiguration)
10. [Firewall-Modi](#firewall-modi)
11. [Threat Intelligence](#threat-intelligence)
12. [Firewall-Regeln definieren](#firewall-regeln-definieren)
13. [E-Mail-Benachrichtigung](#e-mail-benachrichtigung)
14. [Syslog-Export](#syslog-export)
15. [Dashboard-Übersicht](#dashboard-übersicht)
16. [Log-Dateien](#log-dateien)
17. [Häufige Fragen (FAQ)](#häufige-fragen-faq)
18. [Sicherheitshinweise](#sicherheitshinweise)
19. [Projektstruktur](#projektstruktur)

---

## Was ist Net-Fire-Monitor?

Net-Fire-Monitor ist ein aktives **Netzwerk-Monitor- und Intrusion-Prevention-System (IPS)** für Linux, Windows und macOS. Es erfasst den gesamten Netzwerkverkehr in Echtzeit, erkennt Anomalien und kann Angreifer-IPs automatisch über die Systemfirewall blockieren.

Das Tool bietet zwei Bedienoberflächen gleichzeitig:

- **Terminal-Dashboard** – Rich-basierte Live-Ansicht direkt im Terminal
- **Web-Interface** – HTTPS-gesichertes Browser-Dashboard mit CSRF-Schutz, erreichbar im ganzen Netzwerk

---

## Was ist neu in v3.9?

| Änderung | Details |
|----------|---------|
| **Zwei-Prozess-Architektur** | Monitor läuft als root (Scapy + iptables), Web-Interface als unprivilegierter User `netfiremon` |
| **HTTPS Web-Interface** | Self-Signed-Zertifikat wird automatisch generiert, inkl. LAN-IP-SANs |
| **CSRF-Schutz** | Alle schreibenden API-Endpunkte sind durch CSRF-Token abgesichert |
| **scrypt-Passwort-Hashing** | Web-Interface-Passwort wird mit scrypt (n=16384) gehasht, legacy SHA-256 wird automatisch migriert |
| **Brute-Force-Schutz** | 10 Fehlversuche → 15 Minuten Sperrzeit |
| **IPC via Dateisystem** | Monitor und Web-Prozess kommunizieren über atomare Datei-Writes statt geteiltem Speicher |
| **Persistenz nach Neustart** | Blockierte IPs, Regeln, Whitelist und Blacklist werden nach Systemstart wiederhergestellt |
| **OOM-Schutz** | Begrenzte Datenstrukturen (`_BoundedCounter`, `_BoundedPortscanTracker`) verhindern RAM-Erschöpfung bei SYN-Floods |
| **Security-Header** | X-Frame-Options, CSP, HSTS, Referrer-Policy werden automatisch gesetzt |
| **TI Whitelist-Schutz** | Whitelisted IPs werden niemals durch Threat-Intel-Auto-Block gesperrt |
| **TI Start-Jitter** | Feed-Downloads starten mit zufälligem Offset (0–5 Min.) |
| **Syslog-Export** | CEF-Format, TCP/UDP, konfigurierbar |

---

## Architektur (Zwei-Prozess-Modell)

```
┌─────────────────────────────────────────────┐
│  netfiremon.service  (User: root)           │
│  ┌──────────────────────────────────────┐   │
│  │  NetworkMonitor (Scapy, iptables)    │   │
│  │  FirewallEngine, ThreatIntelManager  │   │
│  │  RuleEngine, EmailNotifier           │   │
│  └──────────┬──────────────────────┬───┘   │
│             │ schreibt alle 2s      │ liest  │
│        LIVE_STATE_FILE          CMD_QUEUE   │
└─────────────┼──────────────────────┼────────┘
              │                      │
┌─────────────┼──────────────────────┼────────┐
│  netfiremon-web.service (User: netfiremon)  │
│  ┌──────────▼──────────────────────▼───┐   │
│  │  Flask/Gunicorn  (Port 5443, HTTPS) │   │
│  │  CSRF · Auth · Security-Header      │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Warum zwei Prozesse?**
- Der Monitor braucht Root-Rechte für Scapy und iptables.
- Das Web-Interface braucht diese Rechte **nicht** und läuft daher als unprivilegierter System-User. Ein kompromittiertes Web-Interface kann keine Firewall-Regeln direkt manipulieren.
- Kommunikation erfolgt über atomare Datei-Schreibvorgänge im `data/`-Verzeichnis.

---

## Voraussetzungen

- **Python 3.10** oder neuer
- **Linux** (empfohlen): `iptables`, `ip6tables`, `systemd`
- **Windows**: [Npcap](https://npcap.com/#download) + Administratorrechte
- **macOS**: `pfctl` + Root-Rechte (`sudo`)

Python-Pakete werden beim ersten Start **automatisch installiert**:

```
scapy · rich · plyer · geoip2 · requests · flask · gunicorn · cryptography
```

### Optional: Geo-IP-Datenbank

Für Länder- und Stadtanzeige wird die kostenlose **GeoLite2-City**-Datenbank von MaxMind benötigt:

1. Konto erstellen: [maxmind.com/en/geolite2/signup](https://www.maxmind.com/en/geolite2/signup)
2. `GeoLite2-City.mmdb` herunterladen
3. Datei nach `/opt/netfiremon/GeoLite2-City.mmdb` kopieren (oder bei manuellem Start ins Projektverzeichnis)

---

## Installation

### Linux – automatisch via install.sh (empfohlen)

```bash
# Als root ausführen:
sudo bash install.sh
```

Das Skript führt folgende Schritte durch:

1. Legt den System-User `netfiremon` an (kein Login, kein Home)
2. Erstellt `/opt/netfiremon/` mit korrekten Dateiberechtigungen
3. Installiert alle Python-Pakete in ein Virtual Environment (`.venv`)
4. Registriert `netfiremon.service` (Monitor, root) und `netfiremon-web.service` (Web, unprivilegiert)
5. Führt den Setup-Wizard durch (Passwort, Konfiguration)
6. Startet beide Dienste

### Dienste steuern

```bash
# Status prüfen
sudo systemctl status netfiremon netfiremon-web

# Neu starten
sudo systemctl restart netfiremon netfiremon-web

# Logs live verfolgen
sudo journalctl -u netfiremon -f
sudo journalctl -u netfiremon-web -f
```

### Windows / macOS – manuell

```bash
# Windows (als Administrator):
python netfiremon_web.py

# Linux / macOS (Root erforderlich):
sudo python3 netfiremon_web.py
```

---

## Start & Betrieb

Beim **ersten Start** (oder mit `--setup`) startet der Setup-Wizard:

```bash
sudo python3 netfiremon_web.py --setup
```

Im **Auto-Modus** (für systemd):

```bash
sudo python3 netfiremon_web.py --auto
```

### Start-Modi (interaktiv)

```
0  –  Nur Terminal-Dashboard
1  –  Terminal + Web-Interface
2  –  Nur Web-Interface
```

---

## Web-Interface

Das Web-Interface ist über HTTPS erreichbar:

```
https://<IP-des-Hosts>:5443
```

> ℹ️ Die Browser-Warnung beim ersten Aufruf ist normal – das Zertifikat ist selbst-signiert. Es wird automatisch mit den LAN-IPs des Hosts als Subject Alternative Names (SAN) generiert.

### Funktionen im Web-Interface

| Seite | Funktion |
|-------|---------|
| **Dashboard** | Live-Statistiken, Graph, Top-Talker, Protokolle, letzte Pakete |
| **Alarme** | Alarm-Liste mit Whitelist/Blacklist/Block-Buttons pro IP |
| **Whitelist / Blacklist** | IPs hinzufügen und entfernen |
| **Firewall-Regeln** | Port/Protokoll-Regeln erstellen und löschen |
| **Logs** | Monitor-Log und Firewall-Log live lesen |
| **Konfiguration** | Alle Parameter über die UI anpassen |

### Netzwerk-Modus & Passwort

Ist das Web-Interface netzwerkweit erreichbar (bind `0.0.0.0`), ist ein Passwort **Pflicht**. Das Passwort wird beim Setup-Wizard einmalig gesetzt und mit **scrypt** gehasht gespeichert.

---

## E-Mail-Passwort sicher einrichten

Das E-Mail-Passwort wird **niemals** in der Config-Datei gespeichert. Es wird über die Umgebungsvariable `NFM_EMAIL_PASSWORD` geladen oder separat in `data/.email_password` (Dateiberechtigung 0600).

### Gmail – App-Passwort erstellen (Pflicht!)

> ⚠️ Das echte Google-Passwort funktioniert hier **nicht**. Google verlangt ein App-Passwort.

1. [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) aufrufen
2. Name: `NetFireMonitor` → **Erstellen**
3. Den 16-stelligen Code notieren

### Umgebungsvariable setzen

**Windows** (dauerhaft, als Administrator):
```cmd
setx NFM_EMAIL_PASSWORD "abcdefghijklmnop" /M
```

**Linux / macOS** (dauerhaft in `~/.bashrc` oder `~/.zshrc`):
```bash
export NFM_EMAIL_PASSWORD="abcdefghijklmnop"
```

**Nur für eine Session (Linux/macOS):**
```bash
NFM_EMAIL_PASSWORD="abcdefghijklmnop" sudo -E python3 netfiremon_web.py
```

---

## Konfiguration

Alle Einstellungen werden in `data/net_fire_monitor_config.json` gespeichert.

> ⚠️ **Diese Datei nicht auf GitHub hochladen!** Sie enthält sensible Netzwerkinformationen.

### Alle Parameter

| Parameter | Standard | Beschreibung |
|-----------|----------|--------------|
| `average_period` | `60` | Baseline-Messdauer in Sekunden |
| `monitor_interval` | `10` | Messintervall in Sekunden |
| `threshold` | `20` | Alarm-Schwellenwert in % über Baseline |
| `bpf_filter` | plattformabhängig | Scapy BPF-Filter |
| `interface` | `""` | Netzwerk-Interface (`""` = alle) |
| `interfaces` | `[]` | Mehrere Interfaces gleichzeitig |
| `notify_desktop` | `true` | Desktop-Benachrichtigungen |
| `notify_log` | `true` | Log-Datei-Einträge |
| `resolve_dns` | `true` | DNS-Auflösung im Dashboard |
| `geo_lookup` | `true` | Geo-IP-Ländererkennung |
| `detect_portscan` | `true` | Port-Scan-Erkennung |
| `portscan_limit` | `100` | Ports pro 10 s → Portscan-Alarm |
| `whitelist` | `[]` | IPs ohne Traffic-Alarm und ohne Auto-Block |
| `blacklist` | `[]` | IPs mit sofortigem Alarm bei jedem Paket |
| `firewall_mode` | `"monitor"` | Firewall-Modus (siehe unten) |
| `firewall_rules` | `[]` | Benutzerdefinierte Port/Protokoll-Regeln |
| `max_tracked_ips` | `50000` | Max. IPs im RAM (OOM-Schutz) |
| `threat_intel_enabled` | `true` | Threat-Intel-Feeds aktivieren |
| `threat_intel_auto_block` | `false` | Bekannte Bedrohungs-IPs automatisch blockieren |
| `threat_intel_feeds` | `[...]` | Feed-URLs (kommagetrennte Liste) |
| `threat_intel_update_interval` | `3600` | Sekunden zwischen Feed-Updates |
| `email_enabled` | `false` | E-Mail-Benachrichtigungen |
| `email_smtp` | `"smtp.gmail.com"` | SMTP-Server |
| `email_port` | `587` | SMTP-Port |
| `email_user` | `""` | Absender-E-Mail |
| `email_recipient` | `""` | Empfänger-E-Mail |
| `email_sender` | `""` | Anzeigename Absender (optional) |
| `export_csv` | `true` | CSV-Report speichern |
| `export_json` | `false` | JSON-Report speichern |
| `report_rotate` | `7` | Reports nach N Tagen löschen |
| `syslog_enabled` | `false` | Syslog-Export aktivieren |
| `syslog_host` | `"localhost"` | Syslog-Zielhost |
| `syslog_port` | `514` | Syslog-Port |
| `syslog_protocol` | `"udp"` | `udp` oder `tcp` |
| `syslog_tag` | `"net-fire-monitor"` | Syslog-Tag-Präfix |
| `behind_reverse_proxy` | `false` | ProxyFix aktivieren (nur wenn nginx/caddy vorgeschaltet!) |

---

## Firewall-Modi

### 👁 monitor (Standard)
Nur beobachten. Keine automatischen Eingriffe. Ideal zum Kennenlernen des eigenen Netzwerks.

### ⚡ confirm
Bei einem Alarm wird eine E-Mail gesendet. Die Blockierung erfolgt manuell über das Web-Interface oder Terminal. Erfordert konfigurierte E-Mail.

### 🔥 auto
Verdächtige externe IPs werden **sofort automatisch blockiert**. Dabei gelten folgende Schutzmaßnahmen:

- IPs auf der **Whitelist** werden **niemals** blockiert – auch nicht durch Threat-Intel
- **Private/LAN-IPs** werden nie blockiert
- **Rate Limiting**: max. 30 Blocks pro Minute, min. 10 s Abstand pro IP
- Beim sauberen Beenden wird gefragt, ob alle Regeln aufgehoben werden sollen
- Beim Systemstart werden blockierte IPs aus dem Persistenz-Snapshot wiederhergestellt

> ⚠️ Im `auto`-Modus können durch False Positives legitime Server temporär blockiert werden. Whitelist sorgfältig pflegen!

---

## Threat Intelligence

Das Tool lädt automatisch Listen bekannter Bedrohungs-IPs von konfigurierbaren Feeds:

| Feed | Beschreibung |
|------|-------------|
| **Feodo Tracker** | Botnet Command-and-Control-Server |
| **CINS Army** | Bekannte Angreifer-IPs |
| **Spamhaus DROP** | Gestohlene / kompromittierte Netze (CIDR) |

**Technische Details:**

- Feeds werden alle **60 Minuten** im Hintergrund aktualisiert (konfigurierbares Intervall)
- Start-Jitter: jede Instanz wartet 0–5 Minuten zufällig, um Feed-Server nicht zu überlasten
- Lokales Caching in `data/threat_intel_cache.txt` → schneller Start, keine Wartezeit
- **CIDR-Unterstützung**: Netzwerkadressen wie `185.220.0.0/16` werden als Netzwerkbereiche geprüft
- Beim Start wird angezeigt: `TI: 12.450 IPs + 38 Netze`
- Max. 50 MB Download pro Feed (Schutz gegen kompromittierte Feed-Server)
- **Whitelist hat Vorrang**: Whitelisted IPs werden durch Threat-Intel niemals blockiert, auch nicht im `auto`-Modus

---

## Firewall-Regeln definieren

Regeln werden im Web-Interface unter **Firewall-Regeln** erstellt oder direkt in der Config unter `firewall_rules` definiert:

```json
"firewall_rules": [
  {
    "proto": "tcp",
    "port": 23,
    "src_ip": "",
    "action": "block",
    "comment": "Telnet immer blockieren"
  },
  {
    "proto": "tcp",
    "port": 3389,
    "src_ip": "",
    "action": "alert",
    "comment": "RDP-Zugriff immer alarmieren"
  },
  {
    "proto": "any",
    "port": 0,
    "src_ip": "10.0.0.99",
    "action": "block",
    "comment": "Bestimmte interne IP blockieren"
  }
]
```

| Feld | Werte | Beschreibung |
|------|-------|-------------|
| `proto` | `tcp`, `udp`, `icmp`, `any` | Protokoll |
| `port` | `0`–`65535` (`0` = alle Ports) | Ziel-Port |
| `src_ip` | IP-Adresse oder `""` für alle | Quell-IP |
| `action` | `block`, `alert`, `allow` | Aktion bei Übereinstimmung |
| `comment` | beliebiger Text (max. 200 Zeichen) | Beschreibung der Regel |

---

## E-Mail-Benachrichtigung

Bei jedem Alarm sendet Net-Fire-Monitor eine HTML-E-Mail mit vollständiger IP-Analyse:

```
🚨 Net-Fire-Monitor Alarm

Zeitpunkt : 2026-03-14 10:27:17
Alarm     : Netzwerkverkehr 293.6 pps via 2.16.168.125 ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IP        : 2.16.168.125
Hostname  : a2-16-168-125.deploy.static.akamaitechnologies.com
Geo-IP    : Frankfurt am Main, DE
Besitzer  : Akamai Technologies
Bedrohung : ✅ Nicht bekannt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Grund     : PPS_Exceeded
Modus     : confirm
```

Die IP-Analyse erfolgt automatisch über:
- **socket.gethostbyaddr()** → Hostname (thread-sicher, 0,5 s Timeout)
- **whois** (Linux/macOS) → Besitzer/Organisation
- **Geo-IP** (wenn GeoLite2-DB vorhanden) → Land & Stadt
- **Threat-Intel-Cache** → Bedrohungsstatus

---

## Syslog-Export

Net-Fire-Monitor kann Alarme im **CEF-Format** (Common Event Format) an einen Syslog-Server senden:

```
Konfiguration in der Config oder im Web-Interface:
  syslog_enabled:  true
  syslog_host:     "192.168.1.10"
  syslog_port:     514
  syslog_protocol: "udp"   # oder "tcp"
  syslog_tag:      "net-fire-monitor"
```

Beispiel-CEF-Nachricht:
```
<132>Mar 14 10:27:17 hostname net-fire-monitor: CEF:0|NetFireMonitor|Net-Fire-Monitor|3.9|threat_intel|☠️ Bekannte Bedrohung: 185.220.101.45|4|src=185.220.101.45 reason=threat_intel
```

---

## Dashboard-Übersicht

### Web-Dashboard (https://\<IP\>:5443)

Das Web-Dashboard zeigt in Echtzeit:

- **Header**: Interface, Firewall-Modus (MONITOR/CONFIRM/AUTO), TI-Einträge (z. B. `12.450 IPs + 38 Netze`), Uhrzeit
- **Graph**: PPS-Verlauf der letzten 60 Sekunden mit Baseline-Markierung
- **Statistiken**: Aktuelles PPS/BPS, Baseline, Schwellenwert, Alarm-Zähler, geblockte IPs
- **Top-Talker**: IP, Hostname, Geo-IP, LAN/WAN-Indikator, Paketanzahl
- **Protokoll-Balken**: TCP / UDP / ICMP / OTHER
- **Top-Ports**: Port, Dienst, Anzahl
- **Letzte Pakete**: Zeitstempel, Geo, Src-IP → Dst-IP, Protokoll, Port, Größe

### Terminal-Dashboard

```
╔══════════════════════════════════════════════════════╗
║  NET-FIRE-MONITOR v3.9  │  eth0  │  🔥 AUTO          ║
║  TI: 12.450 IPs + 38 Netze  │  10:29:40             ║
╠══════════════════════════════════════════════════════╣
║  📈 PPS-Verlauf (letzte 60 Sekunden)                 ║
╠══════════════╦═══════════════╦═════════════════════╣
║ 📊 Statistik ║ 🔌 Protokolle ║ 🚨 Letzte Alarme     ║
╠══════════════╩═══════════════╬═════════════════════╣
║ 🔝 Top-Talker                ║ 🔒 Top-Ports         ║
╠══════════════════════════════╩═════════════════════╣
║ 📦 Letzte Pakete (mit Geo-IP)                       ║
╚════════════════════════════════════════════════════╝
```

---

## Log-Dateien

Alle Dateien liegen in `data/` (`/opt/netfiremon/data/` bei systemd-Installation):

| Datei | Inhalt | Max. Größe |
|-------|--------|------------|
| `net_fire_monitor.log` | Alle Ereignisse & Alarme | 5 MB × 3 Backups |
| `firewall.log` | Alle Firewall-Aktionen (BLOCKED / UNBLOCKED) | 2 MB × 5 Backups |
| `net_fire_monitor_live.json` | Live-State für Web-Interface (alle 2 s) | ~50 KB |
| `net_fire_monitor_state.json` | Vollständiger Snapshot (beim Beenden) | ~200 KB |
| `net_fire_monitor_baseline.json` | Gespeicherte Baseline (max. 24 h alt) | ~1 KB |
| `net_fire_monitor_persist.json` | Blockierte IPs, Regeln, Listen (Neustart-Persistenz) | variabel |
| `threat_intel_cache.txt` | Bekannte Bedrohungs-IPs und Netze (Cache) | variabel |
| `cmd_queue/` | IPC-Verzeichnis: Kommandos vom Web- an Monitor-Prozess | temporär |
| `reports/*.csv` | Paket-Reports | rotiert nach N Tagen |

---

## Häufige Fragen (FAQ)

**Das Tool blockiert keine IPs obwohl der Modus `auto` ist.**
→ Administratorrechte prüfen. Firewall-Regeln erfordern erhöhte Rechte (Windows: Als Administrator starten / Linux: `sudo` bzw. systemd-Dienst).

**E-Mail-Versand schlägt fehl (`BadCredentials`).**
→ Bei Gmail kein echtes Passwort verwenden, sondern ein App-Passwort. Siehe Abschnitt „E-Mail-Passwort sicher einrichten".

**Ich habe mich selbst ausgesperrt / eine IP fälschlicherweise blockiert.**
→ Tool beenden (Strg+C) → beim Beenden „Alle Firewall-Regeln aufheben?" mit `y` bestätigen.
Oder manuell:
```bash
# Linux:
sudo iptables -D INPUT -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP
sudo iptables -D OUTPUT -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP
sudo iptables -D FORWARD -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP

# Windows:
netsh advfirewall firewall delete rule name="NetFireMon_Block_1.2.3.4"
```

**Zu viele False-Positive-Alarme.**
→ Bekannte IPs zur Whitelist hinzufügen. `threshold`-Wert erhöhen (z. B. auf 40–50 %). Auf `confirm`-Modus wechseln.

**Die Threat-Intel-Liste ist leer.**
→ Internetverbindung prüfen. Das Tool lädt beim nächsten Start aus dem Cache. Feed-Fehler werden in `net_fire_monitor.log` protokolliert.

**Web-Interface nicht erreichbar.**
→ Prüfen ob `netfiremon-web.service` läuft: `sudo systemctl status netfiremon-web`. Logs: `sudo journalctl -u netfiremon-web -n 50`.

**Browser zeigt Zertifikat-Warnung.**
→ Normal bei Self-Signed-Zertifikat. Im Browser einmalig „Risiko akzeptieren" klicken. Für produktiven Betrieb kann das Zertifikat in `certs/` durch ein eigenes ersetzt werden.

**Monitor-Dienst startet nicht, wartet auf Netzwerk.**
→ `ExecStartPre` im Service wartet bis zu 30 s auf ein aktives Interface. Prüfen ob das Netzwerk-Interface tatsächlich `UP` ist.

---

## Sicherheitshinweise

- **Nur im eigenen Netzwerk betreiben!** Paketerfassung in fremden Netzwerken ist in den meisten Ländern illegal.
- Die Config-Datei enthält persönliche Netzwerkdaten → **nicht auf GitHub hochladen**.
- Das E-Mail-Passwort wird nicht in der Config gespeichert – es wird über `NFM_EMAIL_PASSWORD` oder `data/.email_password` geladen.
- Im `auto`-Modus können False Positives legitime IPs blockieren. Whitelist **vor** Aktivierung sorgfältig einrichten.
- **Öffentliche IPs in der Whitelist** werden nie blockiert – auch nicht durch Threat-Intel. Eine Warnung wird ins Log geschrieben wenn öffentliche IPs in der Whitelist stehen.
- Das Web-Interface im Netzwerk-Modus ist durch Passwort, HTTPS, CSRF-Token und Brute-Force-Schutz gesichert. Für Internetzugang zusätzlich einen Reverse-Proxy (nginx/caddy) vorschalten.
- Der `behind_reverse_proxy`-Parameter darf **nur** aktiviert werden, wenn tatsächlich ein Reverse-Proxy vorgeschaltet ist – sonst ist `X-Forwarded-For` fälschbar.

---

## Projektstruktur

```
netfiremon/
├── core.py                          ← Gemeinsame Engine (Monitor, Firewall, TI, IPC)
├── netfiremon_web.py                ← Web-Interface (Flask/Gunicorn) + Setup-Wizard
├── netfiremon_terminal.py           ← Terminal-Dashboard (Rich)
├── netfiremon.service               ← systemd: Monitor-Prozess (root)
├── netfiremon-web.service           ← systemd: Web-Prozess (netfiremon user)
├── install.sh                       ← Installations-Skript
├── requirements.txt                 ← Python-Abhängigkeiten
├── web/
│   ├── templates/
│   │   ├── base.html                ← Basis-Layout mit CSRF-Helper
│   │   ├── dashboard.html           ← Dashboard-Seite
│   │   └── login.html               ← Login-Seite
│   └── static/
│       ├── app.js                   ← Navigation, Alarme, Listen, Regeln, Config
│       ├── dashboard.js             ← Live-Graph, Stats, Top-Talker
│       └── style.css                ← Terminal-Dark-Theme
└── certs/                           ← TLS-Zertifikat (auto-generiert)
    ├── cert.pem
    └── key.pem
```

**Nicht im Repository (durch .gitignore schützen):**
```
data/                                ← Alle veränderlichen Daten
  net_fire_monitor_config.json       ← Persönliche Einstellungen
  net_fire_monitor.log               ← Monitor-Log
  firewall.log                       ← Firewall-Aktionen
  net_fire_monitor_live.json         ← Live-State
  net_fire_monitor_state.json        ← Snapshot
  net_fire_monitor_baseline.json     ← Baseline
  net_fire_monitor_persist.json      ← Persistenz-Daten
  net_fire_monitor_web_config.json   ← Web-Passwort-Hash
  .email_password                    ← E-Mail-Passwort (0600)
  .web_secret_key                    ← Flask Session-Key (0600)
  threat_intel_cache.txt             ← IP-Listen Cache
  cmd_queue/                         ← IPC-Queue
  reports/                           ← CSV/JSON-Reports
GeoLite2-City.mmdb                   ← Geo-IP-Datenbank (zu groß für Git)
```

---

*Net-Fire-Monitor ist ein Open-Source-Projekt und wird ohne Gewährleistung bereitgestellt.*
*Verwendung auf eigene Verantwortung – Paketerfassung nur in eigenen Netzwerken!*

---
---

# 🇬🇧 ENGLISH

---

## Table of Contents

1. [What is Net-Fire-Monitor?](#what-is-net-fire-monitor)
2. [What's new in v3.9?](#whats-new-in-v39)
3. [Architecture (Two-Process Model)](#architecture-two-process-model)
4. [Requirements](#requirements)
5. [Installation](#installation-1)
6. [Starting & Running](#starting--running)
7. [Web Interface](#web-interface-1)
8. [Setting Up the E-Mail Password Securely](#setting-up-the-e-mail-password-securely)
9. [Configuration](#configuration-1)
10. [Firewall Modes](#firewall-modes)
11. [Threat Intelligence](#threat-intelligence-1)
12. [Defining Firewall Rules](#defining-firewall-rules)
13. [E-Mail Notifications](#e-mail-notifications)
14. [Syslog Export](#syslog-export-1)
15. [Dashboard Overview](#dashboard-overview)
16. [Log Files](#log-files)
17. [FAQ](#faq)
18. [Security Notes](#security-notes)
19. [Project Structure](#project-structure)

---

## What is Net-Fire-Monitor?

Net-Fire-Monitor is an active **network monitoring and Intrusion Prevention System (IPS)** for Linux, Windows and macOS. It captures all network traffic in real time, detects anomalies, and can automatically block attacker IPs via the system firewall.

The tool provides two interfaces simultaneously:

- **Terminal dashboard** – Rich-based live view directly in the terminal
- **Web interface** – HTTPS-secured browser dashboard with CSRF protection, accessible across the network

---

## What's new in v3.9?

| Change | Details |
|--------|---------|
| **Two-process architecture** | Monitor runs as root (Scapy + iptables), web interface as unprivileged user `netfiremon` |
| **HTTPS web interface** | Self-signed certificate generated automatically, including LAN IP SANs |
| **CSRF protection** | All write API endpoints protected by CSRF tokens |
| **scrypt password hashing** | Web interface password hashed with scrypt (n=16384), legacy SHA-256 auto-migrated |
| **Brute-force protection** | 10 failed attempts → 15-minute lockout |
| **File-based IPC** | Monitor and web process communicate via atomic file writes |
| **Post-restart persistence** | Blocked IPs, rules, whitelist and blacklist restored after system reboot |
| **OOM protection** | Bounded data structures prevent RAM exhaustion during SYN floods |
| **Security headers** | X-Frame-Options, CSP, HSTS, Referrer-Policy set automatically |
| **TI whitelist protection** | Whitelisted IPs are never blocked by Threat Intel auto-block |
| **TI start jitter** | Feed downloads start with a random offset (0–5 min.) |
| **Syslog export** | CEF format, TCP/UDP, configurable |

---

## Architecture (Two-Process Model)

```
┌─────────────────────────────────────────────┐
│  netfiremon.service  (User: root)           │
│  ┌──────────────────────────────────────┐   │
│  │  NetworkMonitor (Scapy, iptables)    │   │
│  │  FirewallEngine, ThreatIntelManager  │   │
│  │  RuleEngine, EmailNotifier           │   │
│  └──────────┬──────────────────────┬───┘   │
│             │ writes every 2s       │ reads  │
│        LIVE_STATE_FILE          CMD_QUEUE   │
└─────────────┼──────────────────────┼────────┘
              │                      │
┌─────────────┼──────────────────────┼────────┐
│  netfiremon-web.service (User: netfiremon)  │
│  ┌──────────▼──────────────────────▼───┐   │
│  │  Flask/Gunicorn  (Port 5443, HTTPS) │   │
│  │  CSRF · Auth · Security Headers     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Why two processes?**
- The monitor needs root privileges for Scapy and iptables.
- The web interface does **not** need these privileges and therefore runs as an unprivileged system user. A compromised web interface cannot directly manipulate firewall rules.
- Communication is handled via atomic file writes in the `data/` directory.

---

## Requirements

- **Python 3.10** or newer
- **Linux** (recommended): `iptables`, `ip6tables`, `systemd`
- **Windows**: [Npcap](https://npcap.com/#download) + Administrator rights
- **macOS**: `pfctl` + root (`sudo`)

Python packages are **installed automatically** on first launch:

```
scapy · rich · plyer · geoip2 · requests · flask · gunicorn · cryptography
```

### Optional: Geo-IP Database

The free **GeoLite2-City** database from MaxMind is required for country and city display:

1. Create an account: [maxmind.com/en/geolite2/signup](https://www.maxmind.com/en/geolite2/signup)
2. Download `GeoLite2-City.mmdb`
3. Copy the file to `/opt/netfiremon/GeoLite2-City.mmdb` (or the project directory for manual installs)

---

## Installation

### Linux – automatic via install.sh (recommended)

```bash
# Run as root:
sudo bash install.sh
```

The script performs the following steps:

1. Creates the `netfiremon` system user (no login, no home directory)
2. Creates `/opt/netfiremon/` with correct file permissions
3. Installs all Python packages into a virtual environment (`.venv`)
4. Registers `netfiremon.service` (monitor, root) and `netfiremon-web.service` (web, unprivileged)
5. Runs the setup wizard (password, configuration)
6. Starts both services

### Service Management

```bash
# Check status
sudo systemctl status netfiremon netfiremon-web

# Restart
sudo systemctl restart netfiremon netfiremon-web

# Follow logs live
sudo journalctl -u netfiremon -f
sudo journalctl -u netfiremon-web -f
```

### Windows / macOS – manual

```bash
# Windows (as Administrator):
python netfiremon_web.py

# Linux / macOS (root required):
sudo python3 netfiremon_web.py
```

---

## Starting & Running

On **first launch** (or with `--setup`) the setup wizard starts:

```bash
sudo python3 netfiremon_web.py --setup
```

In **auto mode** (for systemd):

```bash
sudo python3 netfiremon_web.py --auto
```

### Start modes (interactive)

```
0  –  Terminal dashboard only
1  –  Terminal + web interface
2  –  Web interface only
```

---

## Web Interface

The web interface is accessible via HTTPS:

```
https://<host-ip>:5443
```

> ℹ️ The browser warning on first access is normal – the certificate is self-signed. It is automatically generated with the host's LAN IPs as Subject Alternative Names (SAN).

### Web Interface Features

| Page | Function |
|------|---------|
| **Dashboard** | Live statistics, graph, top talkers, protocols, recent packets |
| **Alarms** | Alarm list with whitelist/blacklist/block buttons per IP |
| **Whitelist / Blacklist** | Add and remove IPs |
| **Firewall Rules** | Create and delete port/protocol rules |
| **Logs** | View monitor log and firewall log live |
| **Configuration** | Adjust all parameters via UI |

### Network Mode & Password

When the web interface is accessible network-wide (bind `0.0.0.0`), a password is **mandatory**. The password is set once during the setup wizard and stored as a **scrypt** hash.

---

## Setting Up the E-Mail Password Securely

The e-mail password is **never** stored in the config file. It is loaded via the environment variable `NFM_EMAIL_PASSWORD` or separately stored in `data/.email_password` (file permission 0600).

### Gmail – Create an App Password (Required!)

> ⚠️ Your real Google password will **not** work here. Google requires an App Password.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Name: `NetFireMonitor` → **Create**
3. Note the 16-digit code

### Set the Environment Variable

**Windows** (permanent, as Administrator):
```cmd
setx NFM_EMAIL_PASSWORD "abcdefghijklmnop" /M
```

**Linux / macOS** (permanent in `~/.bashrc` or `~/.zshrc`):
```bash
export NFM_EMAIL_PASSWORD="abcdefghijklmnop"
```

**For a single session (Linux/macOS):**
```bash
NFM_EMAIL_PASSWORD="abcdefghijklmnop" sudo -E python3 netfiremon_web.py
```

---

## Configuration

All settings are stored in `data/net_fire_monitor_config.json`.

> ⚠️ **Do not upload this file to GitHub!** It contains sensitive network information.

### All Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `average_period` | `60` | Baseline measurement duration in seconds |
| `monitor_interval` | `10` | Measurement interval in seconds |
| `threshold` | `20` | Alert threshold in % above baseline |
| `bpf_filter` | platform-dependent | Scapy BPF filter |
| `interface` | `""` | Network interface (`""` = all) |
| `interfaces` | `[]` | Multiple interfaces simultaneously |
| `notify_desktop` | `true` | Desktop notifications |
| `notify_log` | `true` | Log file entries |
| `resolve_dns` | `true` | DNS resolution in dashboard |
| `geo_lookup` | `true` | Geo-IP country detection |
| `detect_portscan` | `true` | Port scan detection |
| `portscan_limit` | `100` | Ports per 10 s → port scan alert |
| `whitelist` | `[]` | IPs exempt from traffic alerts and auto-block |
| `blacklist` | `[]` | IPs that trigger an immediate alert on every packet |
| `firewall_mode` | `"monitor"` | Firewall mode (see below) |
| `firewall_rules` | `[]` | Custom port/protocol rules |
| `max_tracked_ips` | `50000` | Max. IPs in RAM (OOM protection) |
| `threat_intel_enabled` | `true` | Enable Threat Intel feeds |
| `threat_intel_auto_block` | `false` | Automatically block known malicious IPs |
| `threat_intel_feeds` | `[...]` | Feed URLs |
| `threat_intel_update_interval` | `3600` | Seconds between feed updates |
| `email_enabled` | `false` | E-mail notifications |
| `email_smtp` | `"smtp.gmail.com"` | SMTP server |
| `email_port` | `587` | SMTP port |
| `email_user` | `""` | Sender e-mail address |
| `email_recipient` | `""` | Recipient e-mail address |
| `email_sender` | `""` | Display name for sender (optional) |
| `export_csv` | `true` | Save CSV report |
| `export_json` | `false` | Save JSON report |
| `report_rotate` | `7` | Delete reports after N days |
| `syslog_enabled` | `false` | Enable syslog export |
| `syslog_host` | `"localhost"` | Syslog destination host |
| `syslog_port` | `514` | Syslog port |
| `syslog_protocol` | `"udp"` | `udp` or `tcp` |
| `syslog_tag` | `"net-fire-monitor"` | Syslog tag prefix |
| `behind_reverse_proxy` | `false` | Enable ProxyFix (only if nginx/caddy is in front!) |

---

## Firewall Modes

### 👁 monitor (Default)
Observe only. No automatic actions. Ideal for getting started and learning your network.

### ⚡ confirm
An e-mail is sent on every alert. Blocking is done manually via the web interface or terminal. Requires configured e-mail.

### 🔥 auto
Suspicious external IPs are **blocked immediately and automatically**. The following safeguards apply:

- IPs on the **whitelist** are **never** blocked – not even by Threat Intel
- **Private/LAN IPs** are never blocked
- **Rate limiting**: max. 30 blocks per minute, min. 10 s gap per IP
- On clean shutdown you are asked whether to remove all rules
- On system restart, blocked IPs are restored from the persistence snapshot

> ⚠️ In `auto` mode, false positives can temporarily block legitimate servers. Set up your whitelist carefully before enabling!

---

## Threat Intelligence

The tool automatically downloads lists of known malicious IPs from configurable feeds:

| Feed | Description |
|------|-------------|
| **Feodo Tracker** | Botnet Command & Control servers |
| **CINS Army** | Known attacker IPs |
| **Spamhaus DROP** | Stolen / compromised networks (CIDR) |

**Technical details:**

- Feeds are updated every **60 minutes** in the background (configurable interval)
- Start jitter: each instance waits a random 0–5 minutes to avoid overloading feed servers
- Local caching in `data/threat_intel_cache.txt` → fast startup, no waiting
- **CIDR support**: network ranges like `185.220.0.0/16` are checked as network blocks
- Dashboard shows: `TI: 12,450 IPs + 38 networks`
- Max. 50 MB download per feed (protection against compromised feed servers)
- **Whitelist takes precedence**: whitelisted IPs are never blocked by Threat Intel, even in `auto` mode

---

## Defining Firewall Rules

Rules are created in the web interface under **Firewall Rules** or directly in the config under `firewall_rules`:

```json
"firewall_rules": [
  {
    "proto": "tcp",
    "port": 23,
    "src_ip": "",
    "action": "block",
    "comment": "Always block Telnet"
  },
  {
    "proto": "tcp",
    "port": 3389,
    "src_ip": "",
    "action": "alert",
    "comment": "Always alert on RDP access"
  },
  {
    "proto": "any",
    "port": 0,
    "src_ip": "10.0.0.99",
    "action": "block",
    "comment": "Block specific internal IP"
  }
]
```

| Field | Values | Description |
|-------|--------|-------------|
| `proto` | `tcp`, `udp`, `icmp`, `any` | Protocol |
| `port` | `0`–`65535` (`0` = all ports) | Destination port |
| `src_ip` | IP address or `""` for all | Source IP |
| `action` | `block`, `alert`, `allow` | Action on match |
| `comment` | any text (max. 200 characters) | Rule description |

---

## E-Mail Notifications

Net-Fire-Monitor sends an HTML e-mail with full IP analysis on every alert:

```
🚨 Net-Fire-Monitor Alert

Timestamp : 2026-03-14 10:27:17
Alert     : Network traffic 293.6 pps via 2.16.168.125 ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IP        : 2.16.168.125
Hostname  : a2-16-168-125.deploy.static.akamaitechnologies.com
Geo-IP    : Frankfurt am Main, DE
Owner     : Akamai Technologies
Threat    : ✅ Not known
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reason    : PPS_Exceeded
Mode      : confirm
```

IP analysis is performed automatically using:
- **socket.gethostbyaddr()** → hostname (thread-safe, 0.5 s timeout)
- **whois** (Linux/macOS) → owner/organisation
- **Geo-IP** (if GeoLite2 DB present) → country & city
- **Threat Intel cache** → threat status

---

## Syslog Export

Net-Fire-Monitor can send alerts in **CEF format** (Common Event Format) to a syslog server:

```
Configuration in config or web interface:
  syslog_enabled:  true
  syslog_host:     "192.168.1.10"
  syslog_port:     514
  syslog_protocol: "udp"   # or "tcp"
  syslog_tag:      "net-fire-monitor"
```

Example CEF message:
```
<132>Mar 14 10:27:17 hostname net-fire-monitor: CEF:0|NetFireMonitor|Net-Fire-Monitor|3.9|threat_intel|Known threat: 185.220.101.45|4|src=185.220.101.45 reason=threat_intel
```

---

## Dashboard Overview

### Web Dashboard (https://\<IP\>:5443)

The web dashboard shows in real time:

- **Header**: Interface, firewall mode (MONITOR/CONFIRM/AUTO), TI entries (e.g. `12,450 IPs + 38 networks`), clock
- **Graph**: PPS history over the last 60 seconds with baseline marker
- **Statistics**: Current PPS/BPS, baseline, threshold, alert counter, blocked IPs
- **Top talkers**: IP, hostname, Geo-IP, LAN/WAN indicator, packet count
- **Protocol bars**: TCP / UDP / ICMP / OTHER
- **Top ports**: port, service, count
- **Recent packets**: timestamp, geo, src IP → dst IP, protocol, port, size

### Terminal Dashboard

```
╔══════════════════════════════════════════════════════╗
║  NET-FIRE-MONITOR v3.9  │  eth0  │  🔥 AUTO          ║
║  TI: 12,450 IPs + 38 networks  │  10:29:40           ║
╠══════════════════════════════════════════════════════╣
║  📈 PPS history (last 60 seconds)                    ║
╠══════════════╦═══════════════╦═════════════════════╣
║ 📊 Stats     ║ 🔌 Protocols  ║ 🚨 Recent alerts     ║
╠══════════════╩═══════════════╬═════════════════════╣
║ 🔝 Top talkers               ║ 🔒 Top ports         ║
╠══════════════════════════════╩═════════════════════╣
║ 📦 Recent packets (with Geo-IP)                     ║
╚════════════════════════════════════════════════════╝
```

---

## Log Files

All files are located in `data/` (`/opt/netfiremon/data/` for systemd installs):

| File | Contents | Max. size |
|------|----------|-----------|
| `net_fire_monitor.log` | All events & alerts | 5 MB × 3 backups |
| `firewall.log` | All firewall actions (BLOCKED / UNBLOCKED) | 2 MB × 5 backups |
| `net_fire_monitor_live.json` | Live state for web interface (every 2 s) | ~50 KB |
| `net_fire_monitor_state.json` | Full snapshot (on shutdown) | ~200 KB |
| `net_fire_monitor_baseline.json` | Saved baseline (max. 24 h old) | ~1 KB |
| `net_fire_monitor_persist.json` | Blocked IPs, rules, lists (restart persistence) | variable |
| `threat_intel_cache.txt` | Known threat IPs and networks (cache) | variable |
| `cmd_queue/` | IPC directory: commands from web to monitor process | temporary |
| `reports/*.csv` | Packet reports | rotated after N days |

---

## FAQ

**The tool is not blocking IPs even though the mode is set to `auto`.**
→ Check administrator rights. Firewall rules require elevated privileges (Windows: run as Administrator / Linux: `sudo` or systemd service).

**E-mail sending fails (`BadCredentials`).**
→ For Gmail, use an App Password, not your real password. See section "Setting Up the E-Mail Password Securely".

**I accidentally blocked myself / a legitimate IP.**
→ Stop the tool (Ctrl+C) → confirm "Remove all firewall rules?" with `y` on exit.
Or remove manually:
```bash
# Linux:
sudo iptables -D INPUT -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP
sudo iptables -D OUTPUT -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP
sudo iptables -D FORWARD -s 1.2.3.4 -m comment --comment "NetFireMon" -j DROP

# Windows:
netsh advfirewall firewall delete rule name="NetFireMon_Block_1.2.3.4"
```

**Too many false positive alerts.**
→ Add known IPs to the whitelist. Increase the `threshold` value (e.g. to 40–50 %). Switch to `confirm` mode.

**The Threat Intel list is empty.**
→ Check your internet connection. The tool loads from cache on next start. Feed errors are logged in `net_fire_monitor.log`.

**Web interface not reachable.**
→ Check if `netfiremon-web.service` is running: `sudo systemctl status netfiremon-web`. Logs: `sudo journalctl -u netfiremon-web -n 50`.

**Browser shows certificate warning.**
→ Normal for a self-signed certificate. Click "Accept the risk" once in the browser. For production use the certificate in `certs/` can be replaced with your own.

**Monitor service does not start, waiting for network.**
→ `ExecStartPre` in the service waits up to 30 s for an active interface. Check whether the network interface is actually `UP`.

---

## Security Notes

- **Only use on your own network!** Packet capture on foreign networks is illegal in most countries.
- The config file contains personal network data → **do not upload to GitHub**.
- The e-mail password is not stored in the config – it is loaded via `NFM_EMAIL_PASSWORD` or `data/.email_password`.
- In `auto` mode, false positives can block legitimate IPs. Set up your whitelist **before** enabling.
- **Public IPs on the whitelist** are never blocked – not even by Threat Intel. A warning is written to the log if public IPs are on the whitelist.
- The web interface in network mode is secured by password, HTTPS, CSRF tokens and brute-force protection. For internet-facing deployments, place a reverse proxy (nginx/caddy) in front.
- The `behind_reverse_proxy` parameter must **only** be enabled if an actual reverse proxy is in front – otherwise `X-Forwarded-For` is forgeable.

---

## Project Structure

```
netfiremon/
├── core.py                          ← Shared engine (monitor, firewall, TI, IPC)
├── netfiremon_web.py                ← Web interface (Flask/Gunicorn) + setup wizard
├── netfiremon_terminal.py           ← Terminal dashboard (Rich)
├── netfiremon.service               ← systemd: monitor process (root)
├── netfiremon-web.service           ← systemd: web process (netfiremon user)
├── install.sh                       ← Installation script
├── requirements.txt                 ← Python dependencies
├── web/
│   ├── templates/
│   │   ├── base.html                ← Base layout with CSRF helper
│   │   ├── dashboard.html           ← Dashboard page
│   │   └── login.html               ← Login page
│   └── static/
│       ├── app.js                   ← Navigation, alarms, lists, rules, config
│       ├── dashboard.js             ← Live graph, stats, top talkers
│       └── style.css                ← Terminal dark theme
└── certs/                           ← TLS certificate (auto-generated)
    ├── cert.pem
    └── key.pem
```

**Not in repository (protect with .gitignore):**
```
data/                                ← All mutable data
  net_fire_monitor_config.json       ← Personal settings
  net_fire_monitor.log               ← Monitor log
  firewall.log                       ← Firewall actions
  net_fire_monitor_live.json         ← Live state
  net_fire_monitor_state.json        ← Snapshot
  net_fire_monitor_baseline.json     ← Baseline
  net_fire_monitor_persist.json      ← Persistence data
  net_fire_monitor_web_config.json   ← Web password hash
  .email_password                    ← E-mail password (0600)
  .web_secret_key                    ← Flask session key (0600)
  threat_intel_cache.txt             ← IP list cache
  cmd_queue/                         ← IPC queue
  reports/                           ← CSV/JSON reports
GeoLite2-City.mmdb                   ← Geo-IP database (too large for Git)
```

---

*Net-Fire-Monitor is an open-source project and is provided without warranty.*
*Use at your own risk – packet capture only on your own networks!*
