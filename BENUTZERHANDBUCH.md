# NET-FIRE-MONITOR v3.9.3 – Benutzerhandbuch

> **Dein professioneller Netzwerk-Wächter für kleine Unternehmen**

Willkommen! Dieses Handbuch erklärt dir alles, was du als Anwender wissen musst – von der Philosophie über die tägliche Arbeit bis zu Profi-Funktionen. Keine Vorkenntnisse in Netzwerktechnik nötig.

---

## Inhaltsverzeichnis

1. [Was macht dieses Tool?](#1-was-macht-dieses-tool)
2. [Die Philosophie: Echtzeit-Schutz vs. Hardware-Schonung](#2-die-philosophie-echtzeit-schutz-vs-hardware-schonung)
3. [Installation](#3-installation)
4. [Erster Start](#4-erster-start)
5. [Das Web-Dashboard verstehen](#5-das-web-dashboard-verstehen)
6. [Die Alarm-Zentrale: Was passiert, wenn ich was klicke?](#6-die-alarm-zentrale-was-passiert-wenn-ich-was-klicke)
7. [Korrekte Workflows: Wie arbeite ich mit der Software?](#7-korrekte-workflows-wie-arbeite-ich-mit-der-software)
8. [Listen verwalten: Whitelist, Blacklist und Stummschaltung](#8-listen-verwalten-whitelist-blacklist-und-stummschaltung)
9. [Firewall-Regeln definieren](#9-firewall-regeln-definieren)
10. [Firewall-Modi verstehen](#10-firewall-modi-verstehen)
11. [Threat Intelligence (automatische Bedrohungserkennung)](#11-threat-intelligence-automatische-bedrohungserkennung)
12. [E-Mail-Benachrichtigungen einrichten](#12-e-mail-benachrichtigungen-einrichten)
13. [Syslog / SIEM-Integration (für Profis)](#13-syslog--siem-integration-für-profis)
14. [Logs analysieren](#14-logs-analysieren)
15. [Das Notfall-Tool](#15-das-notfall-tool)
16. [Konfiguration im Detail](#16-konfiguration-im-detail)
17. [Zusammenfassung für den Alltag](#17-zusammenfassung-für-den-alltag)
18. [Häufige Fragen (FAQ)](#18-häufige-fragen-faq)
19. [Fehlerbehebung](#19-fehlerbehebung)

---

## 1. Was macht dieses Tool?

Net-Fire-Monitor ist ein **Netzwerk-Wächter**, der deinen Computer oder Server rund um die Uhr überwacht. Er erkennt:

- **DDoS-Angriffe** – Wenn jemand deinen Server mit Datenpaketen flutet
- **Port-Scans** – Wenn jemand dein System nach offenen Türen absucht
- **Bekannte Hacker-IPs** – Durch automatischen Abgleich mit globalen Bedrohungsdatenbanken
- **Ungewöhnlichen Traffic** – Wenn plötzlich viel mehr Daten fließen als normal

Und er kann **sofort reagieren**: Angreifer-IPs werden in Echtzeit gesperrt, sodass kein einziges weiteres Paket durchkommt.

Das Tool bietet dir zwei Bedienoberflächen:

| Oberfläche | Beschreibung | Wann nutzen? |
|---|---|---|
| **Web-Dashboard** | Browser-basiert, HTTPS-gesichert, im ganzen Netzwerk erreichbar | Tägliche Arbeit, Alarm-Management |
| **Terminal-Dashboard** | Rich-basierte Live-Ansicht direkt im Terminal | Server ohne Desktop, SSH-Zugriff |

---

## 2. Die Philosophie: Echtzeit-Schutz vs. Hardware-Schonung

Bevor wir zu den Buttons kommen, ist ein technisches Prinzip wichtig:

### Der Schutz ist SOFORT

Wenn du eine IP blockierst, schließt sich das „Schloss" am Rechner **in derselben Millisekunde**. Kein Paket kommt mehr durch. Die Firewall-Regel wird direkt im Betriebssystem gesetzt (iptables unter Linux, Windows-Firewall unter Windows).

### Die SSD wird GESCHONT

Damit dein Rechner nicht bei jedem kleinen Alarm auf die Festplatte schreiben muss (was die Lebensdauer deiner SSD verkürzt), merkt sich das Tool Änderungen erst einmal im **Arbeitsspeicher (RAM)**. Erst nach **10 Minuten** oder beim **Beenden des Programms** wird dieser Stand dauerhaft in eine Datei geschrieben.

> **Was bedeutet das konkret?**
> Wenn du den Stecker ziehst (Stromausfall), gehen maximal die letzten 10 Minuten an Statistiken verloren. Die Firewall-Regeln selbst sind aber bereits im Betriebssystem aktiv – die Blockierungen überleben sogar einen Stromausfall. Beim nächsten Start stellt das Tool automatisch den letzten bekannten Zustand wieder her.

---

## 3. Installation

### Windows

1. **Python 3.10+** installieren: [python.org/downloads](https://www.python.org/downloads/)
   - Wichtig: Haken bei **"Add Python to PATH"** setzen!
2. **Npcap** installieren: [npcap.com](https://npcap.com) (wird für Paketerfassung benötigt)
3. Die Net-Fire-Monitor-Dateien in einen Ordner entpacken
4. **Als Administrator** eine Eingabeaufforderung öffnen
5. In den Ordner navigieren und starten:
   ```
   cd C:\Pfad\zum\Ordner
   pip install -r requirements.txt
   python netfiremon_web.py
   ```

### Linux (empfohlen für Produktivbetrieb)

```bash
# Automatische Installation mit systemd-Diensten:
sudo bash install.sh
```

Das Installationsskript erledigt alles automatisch:
- Legt einen dedizierten System-User `netfiremon` an (Sicherheit!)
- Erstellt ein Python Virtual Environment
- Installiert alle Abhängigkeiten
- Richtet zwei systemd-Dienste ein (Monitor + Web)
- Startet den Einrichtungsassistenten

### Optional: GeoIP-Datenbank

Für die Länderzuordnung von IP-Adressen (kostenlos):
1. Registrierung bei [maxmind.com](https://www.maxmind.com/en/geolite2/signup)
2. `GeoLite2-City.mmdb` herunterladen
3. In den Programmordner kopieren

---

## 4. Erster Start

Beim allerersten Start führt dich ein **Einrichtungsassistent** durch die wichtigsten Einstellungen:

```
╔══════════════════════════════════════════════════════════╗
║      NET-FIRE-MONITOR  v3.9  –  Ersteinrichtung         ║
╚══════════════════════════════════════════════════════════╝

SCHRITT 1/3 – Python-Pakete installieren
  ✅  scapy – bereits installiert
  ✅  rich – bereits installiert
  ...

SCHRITT 2/3 – Systemtreiber
  ✅  Npcap ist bereits installiert.

SCHRITT 3/3 – GeoLite2-City Datenbank
  ✅  GeoLite2-City.mmdb gefunden.
```

Danach wirst du nach deinen Präferenzen gefragt:
- **Schwellenwert** (Standard: 50%) – Wie viel mehr Traffic als normal einen Alarm auslöst
- **Firewall-Modus** – Siehe [Kapitel 10](#10-firewall-modi-verstehen)
- **E-Mail** – Willst du bei Alarmen eine E-Mail bekommen?
- **Threat Intelligence** – Automatische Hacker-IP-Listen (empfohlen: JA)

> **Tipp:** Alle Einstellungen kannst du später jederzeit im Web-Dashboard unter **Konfiguration** ändern.

---

## 5. Das Web-Dashboard verstehen

Nach dem Start erreichst du das Dashboard unter:
- **Lokal:** `https://localhost:5443`
- **Im Netzwerk:** `https://<deine-IP>:5443`

> **Browser-Warnung:** Beim ersten Zugriff zeigt der Browser eine Sicherheitswarnung wegen des Self-Signed-Zertifikats. Das ist normal und erwartet. Klicke auf „Erweitert" → „Trotzdem fortfahren".

### Die 6 Seiten im Überblick

| Seite | Symbol | Was zeigt sie? |
|---|---|---|
| **Dashboard** | Startseite | Live-Statistiken: Pakete/s, Bandbreite, Top-Talker, Protokolle |
| **Alarme** | Glocke | Alle Sicherheitsmeldungen mit Aktions-Buttons |
| **Listen** | Schild | Whitelist, Blacklist und Stummschaltungen verwalten |
| **Regeln** | Zahnrad | Eigene Firewall-Regeln erstellen und löschen |
| **Logs** | Dokument | Monitor- und Firewall-Protokolle durchsuchen |
| **Config** | Einstellungen | Alle Systemeinstellungen anpassen |

### Das Live-Dashboard

Das Dashboard aktualisiert sich alle **2 Sekunden** und zeigt:

- **Traffic-Graph** – Paketrate über die letzten 60 Messungen (gelbe Linie = Baseline)
- **Aktuelle Werte** – Pakete pro Sekunde (pps) und Bandbreite (KB/s, MB/s)
- **Top-Talker** – Die aktivsten IP-Adressen mit Hostname, Land und LAN/WAN-Kennzeichnung
- **Protokoll-Verteilung** – Anteil TCP, UDP, ICMP
- **Top-Ports** – Die am häufigsten angesprochenen Ports mit Service-Namen
- **Letzte Pakete** – Echtzeit-Paketliste mit Quelle, Ziel, Protokoll und Größe
- **Alarme** – Die neuesten Sicherheitsmeldungen

---

## 6. Die Alarm-Zentrale: Was passiert, wenn ich was klicke?

Auf der Seite **Alarme** findest du unter jeder Meldung fünf Aktions-Buttons. Hier ist ihre Funktion im Detail:

### ✅ Whitelist (Vertrauen)

| | |
|---|---|
| **Was passiert?** | Die IP wird als „sicher" markiert. |
| **Wann nutzen?** | Für eigene Geräte, Partner, vertrauenswürdige Dienste (Google, Microsoft, Cloudflare). |
| **Effekt** | Diese IP wird **niemals** blockiert – auch nicht wenn sie sehr viel Traffic verursacht oder auf einer globalen Bedrohungsliste steht. |
| **Rückgängig?** | Ja – auf der Seite „Listen" unter Whitelist das ✕ klicken. |

### 🚫 Blacklist (Fahndungsliste)

| | |
|---|---|
| **Was passiert?** | Die IP kommt auf eine interne Beobachtungsliste. |
| **Wann nutzen?** | Für IPs, die du als gefährlich eingestuft hast und bei denen du sofort gewarnt werden willst, falls sie jemals wieder auftauchen. |
| **Effekt** | Jedes Mal wenn diese IP ein Paket schickt, erscheint ein **feuerroter Alarm** – auch wenn der Traffic nur minimal ist. |
| **Rückgängig?** | Ja – auf der Seite „Listen" unter Blacklist das ✕ klicken. |

> **Wichtig:** Blacklist ≠ Blockieren! Die Blacklist ist eine **Beobachtungsliste**, kein Firewall-Block. Wenn du eine IP komplett aussperren willst, nutze den **Blocken**-Button.

### 🔒 Blocken (Sofort-Aussperrung)

| | |
|---|---|
| **Was passiert?** | Das Tool weist das Betriebssystem an, die IP komplett zu sperren (iptables/Windows-Firewall). |
| **Wann nutzen?** | Bei akuten Angriffen, nervigen Scannern, oder wenn eine IP dich mit Daten flutet. |
| **Effekt** | Es herrscht **sofort Ruhe**. Die IP kann dich in beide Richtungen nicht mehr erreichen (eingehend UND ausgehend). |
| **Rückgängig?** | Ja – auf der Seite „Listen" die blockierte IP suchen und das ✕ klicken. Oder über das [Notfall-Tool](#15-das-notfall-tool). |

### 🔇 Stumm / 🔔 Entstummen (Alarm-Pause)

| | |
|---|---|
| **Was passiert?** | Du pausierst die Benachrichtigungen für diese IP – wählbar: 15 Min, 1 Std, 6 Std, 24 Std oder dauerhaft. |
| **Wann nutzen?** | Wenn ein Dienst eigentlich okay ist, aber gerade so viel Traffic macht, dass er ständig Alarme auslöst (z.B. ein Cloud-Backup, Windows-Update). |
| **Effekt** | Die Firewall bleibt **offen**, der Traffic wird **gezählt**, aber du bekommst keine nervigen Popups, E-Mails oder Log-Einträge mehr für diese IP. |
| **Rückgängig?** | Ja – automatisch nach Ablauf der gewählten Zeit, oder sofort über den 🔔-Button bzw. die Seite „Listen". |

### ⏭️ Überspringen (Erledigt / Zur Kenntnis genommen)

| | |
|---|---|
| **Was passiert?** | Der Alarm verschwindet sanft aus deiner Liste (Slide-Out-Animation). |
| **Wann nutzen?** | Wenn du den Alarm gesehen und für harmlos befunden hast. |
| **Effekt** | Rein visuell – das Dashboard wird aufgeräumt. Es hat **keine Auswirkung** auf die Firewall, Listen oder den Traffic. |
| **Rückgängig?** | Beim nächsten Seiten-Refresh erscheinen nur neue Alarme. Übersprungene Alarme bleiben in den Logs erhalten. |

---

## 7. Korrekte Workflows: Wie arbeite ich mit der Software?

### Workflow A: Ein neuer Alarm erscheint

```
1. PRÜFEN
   └─ Schau auf den Hostnamen und das Land.
      Ist es ein bekannter Dienst? (Cloudflare, Amazon, Google, dein ISP?)

2. ENTSCHEIDEN
   ├─ Angreifer?              → 🔒 Blocken
   ├─ Bekannter Dienst,       → 🔇 Stumm (1 Std.)
   │  der gerade viel zu
   │  tun hat?
   ├─ Fehlalarm?              → ⏭️ Überspringen
   └─ Vertrauenswürdige IP?   → ✅ Whitelist
```

### Workflow B: Versehentlich geblockt ("Ich habe mich ausgesperrt")

1. **Keine Panik!** Die Sperre lässt sich jederzeit aufheben.
2. Gehe auf die Seite **Listen**.
3. Suche die IP unter den aktiv gesperrten IPs.
4. Klicke auf das **✕** neben der IP. Die Firewall öffnet sich **sofort** wieder.

> Falls du dich komplett aus dem Web-Interface ausgesperrt hast, nutze das [Notfall-Tool](#15-das-notfall-tool).

### Workflow C: Regelmäßige Pflege (1× pro Woche)

1. **Alarme durchgehen** – Gibt es wiederkehrende Muster? Sollte eine IP auf die Whitelist?
2. **Logs prüfen** – Unter „Logs" → „Firewall" siehst du alle Blockierungen mit Zeitstempel.
3. **Threat Intelligence** – Prüfe auf der Dashboard-Seite, ob die TI-Feeds aktuell sind (Anzahl der geladenen IPs/Netze).

---

## 8. Listen verwalten: Whitelist, Blacklist und Stummschaltung

Die Seite **Listen** ist deine zentrale Verwaltung für IP-Klassifizierungen:

### Whitelist (Vertrauensliste)

- IPs die **niemals** blockiert werden
- Empfohlen für: eigene Server, Backup-Dienste, DNS-Server
- **Achtung:** Das Tool erkennt automatisch DNS-Server und Gateway und schützt diese bereits – du musst sie nicht manuell hinzufügen

### Blacklist (Beobachtungsliste)

- IPs die bei **jedem Kontakt** einen Alarm auslösen
- Empfohlen für: bekannte Angreifer, verdächtige Scanner

### Stummschaltung (Alarm-Pause)

- Zeitlich begrenzte Alarm-Unterdrückung
- Keine Auswirkung auf Firewall oder Traffic-Zählung
- Läuft automatisch ab

### Globaler Alarm-Cooldown

Unter den Stumm-Einstellungen kannst du den **globalen Cooldown** festlegen (Standard: 300 Sekunden). Das bedeutet: Für dieselbe IP und denselben Alarmgrund wird innerhalb dieser Zeitspanne nur **ein** Alarm ausgelöst – verhindert Alarm-Flut bei DDoS.

---

## 9. Firewall-Regeln definieren

Auf der Seite **Regeln** kannst du eigene Firewall-Regeln erstellen. Diese gelten **dauerhaft** und unabhängig von Alarmen.

### Beispiele

| Protokoll | Port | Quell-IP | Aktion | Kommentar |
|---|---|---|---|---|
| TCP | 23 | (leer) | block | Telnet ist unsicher |
| TCP | 3389 | (leer) | alert | RDP-Zugriffe melden |
| UDP | 0 | 10.0.0.50 | allow | Interner DNS |

### Aktionstypen

- **block** – Paket wird blockiert und IP gesperrt
- **alert** – Paket wird durchgelassen, aber ein Alarm wird ausgelöst
- **allow** – Paket wird durchgelassen (nützlich für Ausnahmen)

> **Tipp:** Port `0` bedeutet „alle Ports". Leere Quell-IP bedeutet „jede IP".

---

## 10. Firewall-Modi verstehen

Net-Fire-Monitor hat drei Betriebsmodi, die du jederzeit unter **Config** ändern kannst:

### MONITOR (Grün) – Nur beobachten

```
Empfohlen für:  Erste Wochen, Kennenlernen des Netzwerk-Traffics
Was passiert:   Das Tool beobachtet und warnt, greift aber NICHT ein
Vorteil:        Kein Risiko, versehentlich etwas zu blockieren
```

### CONFIRM (Gelb) – Fragen vor dem Handeln

```
Empfohlen für:  Täglicher Betrieb in den meisten Unternehmen
Was passiert:   Bei Auffälligkeiten bekommst du einen Alarm und
                entscheidest selbst, ob blockiert werden soll
Vorteil:        Volle Kontrolle bei jeder Entscheidung
```

### AUTO (Rot) – Automatisch blockieren

```
Empfohlen für:  Server ohne permanente Überwachung, Nachtbetrieb
Was passiert:   Bekannte Bedrohungen und Schwellenwert-Überschreitungen
                werden AUTOMATISCH blockiert
Vorteil:        24/7-Schutz ohne menschliches Eingreifen
Risiko:         Kann bei falsch konfiguriertem Schwellenwert legitimen
                Traffic blockieren → erst im MONITOR-Modus testen!
```

> **Empfohlener Einführungspfad:**
> 1. Woche: **MONITOR** – Beobachten, Baseline kennenlernen
> 2. Woche: **CONFIRM** – Alarme manuell bearbeiten
> 3. Woche+: **AUTO** oder **CONFIRM** je nach Komfortniveau

---

## 11. Threat Intelligence (automatische Bedrohungserkennung)

Net-Fire-Monitor lädt automatisch Listen von zehntausenden bekannten Angreifer-IPs herunter:

### Integrierte Feeds

| Feed | Quelle | Aktualisierung |
|---|---|---|
| Feodo Tracker | abuse.ch | Botnet-Command-Server |
| CI Army | cinsscore.com | Generische Angreifer-IPs |
| Spamhaus DROP | spamhaus.org | CIDR-Netzbereiche |

### So funktioniert es

1. Beim Start werden die Feeds geladen (Cache für Offline-Betrieb)
2. Alle 60 Minuten (konfigurierbar) werden die Listen aktualisiert
3. **Jedes eingehende Paket** wird gegen diese Listen geprüft (O(log N) – hochperformant)
4. Bei einem Treffer: Alarm + optional Auto-Block (wenn `threat_intel_auto_block` aktiv)

### CIDR-Unterstützung

Die Feeds enthalten nicht nur einzelne IPs, sondern auch ganze Netzbereiche (z.B. `45.134.0.0/16`). Net-Fire-Monitor versteht beides und prüft Pakete effizient per Binary Search – auch bei 50.000+ Einträgen bleibt die Performance bei < 1ms pro Lookup.

---

## 12. E-Mail-Benachrichtigungen einrichten

Du kannst dir bei jedem Alarm automatisch eine E-Mail schicken lassen – inklusive:
- IP-Adresse und Hostname
- Geo-IP-Standort (Land, Stadt)
- Besitzer/Organisation (per WHOIS)
- Threat-Intelligence-Status
- Alarmgrund

### Einrichtung (Gmail-Beispiel)

1. **Config** → E-Mail aktivieren
2. SMTP-Server: `smtp.gmail.com`
3. Port: `587`
4. Benutzername: deine Gmail-Adresse
5. Passwort: ein [App-spezifisches Passwort](https://myaccount.google.com/apppasswords) (NICHT dein normales Passwort!)
6. Empfänger: deine E-Mail-Adresse

> **Sicherheit:** Das E-Mail-Passwort wird separat gespeichert (nicht in der Haupt-Config) und mit restriktiven Dateiberechtigungen geschützt. Alternativ kann es über die Umgebungsvariable `NFM_EMAIL_PASSWORD` gesetzt werden.

---

## 13. Syslog / SIEM-Integration (für Profis)

Net-Fire-Monitor kann alle Alarme im **CEF-Format** (Common Event Format) an einen Syslog-Server senden:

```
CEF:0|NetFireMonitor|Net-Fire-Monitor|3.9|portscan|Port-Scan von 45.134.26.91 (47 Ports/10s)|4|src=45.134.26.91 reason=portscan
```

### Kompatibel mit

- Splunk
- Graylog
- Elastic/ELK Stack
- QRadar
- Jeder RFC-3164-kompatible Syslog-Server

### Einrichtung

1. **Config** → Syslog aktivieren
2. SIEM-Host und Port eingeben
3. Protokoll wählen: UDP (Standard) oder TCP
4. Tag anpassen (Standard: `net-fire-monitor`)

---

## 14. Logs analysieren

Die Seite **Logs** bietet zwei Ansichten:

### Monitor-Log

Zeigt alle Systemereignisse:
- Programmstart und Baseline-Messung
- Threat-Intelligence-Updates
- Alarm-Meldungen (farbcodiert)
- Config-Änderungen

### Firewall-Log

Zeigt alle Firewall-Aktionen:
- `BLOCKED 185.220.101.42  Grund: Threat Intel` – IP wurde gesperrt
- `UNBLOCKED 185.220.101.42` – Sperre wurde aufgehoben
- Zeitstempel für jeden Vorgang

### Suchfunktion

Beide Logs haben ein **Suchfeld** – tippe z.B. eine IP-Adresse oder „BLOCKED" ein, um gezielt zu filtern.

### Auto-Scroll

Standardmäßig scrollt das Log automatisch zum neuesten Eintrag. Deaktiviere den Haken **Auto-Scroll** um in Ruhe alte Einträge zu lesen.

---

## 15. Das Notfall-Tool

Wenn das Web-Interface einmal nicht erreichbar ist (z.B. bei totaler Netzwerk-Überlastung oder wenn du dich versehentlich ausgesperrt hast):

### Starten

```bash
# Windows (als Administrator):
python nfm_notfalladmin.py

# Linux (als root):
sudo python3 nfm_notfalladmin.py
```

### Befehle

| Befehl | Beschreibung |
|---|---|
| `list` | Zeigt alle aktuell blockierten IPs |
| `block 1.2.3.4` | Sperrt eine IP sofort |
| `unblock 1.2.3.4` | Hebt die Sperre für eine IP sofort auf |
| `clear` | Entfernt ALLE Firewall-Regeln (mit Bestätigung) |
| `exit` | Beendet das Notfall-Tool |

### Synchronisation

Das Notfall-Tool synchronisiert sich automatisch mit dem laufenden Monitor. Wenn du eine IP blockierst oder freigibst, wird der Monitor darüber informiert und aktualisiert seinen internen Zustand.

---

## 16. Konfiguration im Detail

Alle Einstellungen können über die Seite **Config** im Web-Dashboard geändert werden. Hier die wichtigsten Parameter:

### Allgemein

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `threshold` | 50 | Schwellenwert in % – wie viel mehr Traffic als die Baseline einen Alarm auslöst |
| `monitor_interval` | 10 | Messintervall in Sekunden |
| `average_period` | 120 | Dauer der Baseline-Messung beim Start (Sekunden) |
| `interface` | (leer) | Netzwerk-Interface – leer = alle überwachen |
| `bpf_filter` | auto | Berkeley Packet Filter – bestimmt welche Pakete erfasst werden |

### Benachrichtigungen

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `notify_desktop` | Ja | Desktop-Popup bei Alarmen |
| `notify_log` | Ja | Alarme ins Log schreiben |
| `email_enabled` | Nein | E-Mail-Benachrichtigungen |

### Erkennung

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `resolve_dns` | Ja | Hostnamen auflösen (etwas mehr Traffic) |
| `geo_lookup` | Ja | Geo-IP-Standorte anzeigen |
| `detect_portscan` | Ja | Port-Scan-Erkennung aktiv |
| `portscan_limit` | 100 | Ab wie vielen Ports/10s ein Port-Scan erkannt wird |

### Reports

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `export_csv` | Ja | Alle Pakete als CSV speichern |
| `export_json` | Nein | Zusätzlich als JSON speichern |
| `report_rotate` | 7 | Alte Reports nach X Tagen löschen |

### Sicherheit

| Einstellung | Standard | Beschreibung |
|---|---|---|
| `behind_reverse_proxy` | Nein | NUR aktivieren wenn ein Reverse-Proxy (nginx, Caddy) vorgeschaltet ist! |
| `max_tracked_ips` | 50.000 | Maximale Anzahl gleichzeitig getrackter IPs (OOM-Schutz) |

---

## 17. Zusammenfassung für den Alltag

Net-Fire-Monitor ist dein **stiller Wächter**. Im Idealfall läuft das Tool im Modus **CONFIRM**:

1. Du bekommst eine **E-Mail** oder einen **Desktop-Alarm** wenn etwas Ungewöhnliches passiert
2. Du öffnest das **Web-Dashboard** und schaust dir den Alarm an
3. Mit **einem Klick** entscheidest du: Whitelist, Blacklist, Blocken, Stumm oder Überspringen
4. Das Tool kümmert sich um den Rest – hardware-schonend, sicher und hochperformant

```
  Normaler Tag:                    Alarm-Tag:
  ┌──────────────┐                 ┌──────────────┐
  │   Dashboard   │                │  E-Mail kommt │
  │   alles grün  │                │  "Alarm: ..."  │
  │   ✅ Fertig   │                │       ↓        │
  └──────────────┘                 │  Dashboard     │
                                   │  öffnen        │
                                   │       ↓        │
                                   │  1 Klick:      │
                                   │  🔒 Blocken    │
                                   │       ↓        │
                                   │  ✅ Erledigt   │
                                   └──────────────┘
```

---

## 18. Häufige Fragen (FAQ)

### Kann ich das Tool im Hintergrund laufen lassen?

**Ja!** Unter Linux richtet `install.sh` automatisch systemd-Dienste ein, die beim Hochfahren starten. Unter Windows kannst du den Modus `--auto` nutzen:
```
python netfiremon_web.py --auto
```

### Muss ich regelmäßig Updates machen?

- **Threat Intelligence:** Wird automatisch alle 60 Minuten aktualisiert
- **GeoIP-Datenbank:** Sollte alle 1–3 Monate manuell aktualisiert werden (Download von MaxMind)
- **Software selbst:** Bei neuen Versionen die Dateien ersetzen und Dienste neu starten

### Browser zeigt "Nicht sicher" – ist das gefährlich?

**Nein.** Die Warnung erscheint weil das TLS-Zertifikat selbst-signiert ist (kein offizieller Aussteller). Die Verbindung ist trotzdem **verschlüsselt**. Für ein internes Tool in einem kleinen Unternehmen ist das völlig in Ordnung.

### Was passiert bei einem Stromausfall?

1. Firewall-Regeln im Betriebssystem bleiben aktiv (diese überleben einen Reboot)
2. Beim nächsten Start stellt das Tool automatisch den letzten Zustand aus der Persistenz-Datei wieder her
3. Die Baseline wird aus dem gespeicherten Snapshot geladen (kein erneutes 2-Minuten-Warten)

### Wie viel Ressourcen verbraucht das Tool?

- **RAM:** ca. 50–150 MB (je nach Traffic-Volumen)
- **CPU:** < 1% im Normalbetrieb, max. 5% bei DDoS
- **Festplatte:** nur alle 10 Minuten ein Schreibvorgang (SSD-schonend!)

### Kann ich mehrere Server gleichzeitig überwachen?

Ja – installiere Net-Fire-Monitor auf jedem Server und sende die Alarme via **Syslog** an einen zentralen SIEM-Server (Splunk, Graylog, ELK).

### Mein Virenscanner warnt vor Scapy – ist das normal?

**Ja.** Scapy ist ein legitimes Netzwerk-Werkzeug, das rohe Pakete lesen kann. Manche Virenscanner stufen das als „Hacker-Tool" ein. Du kannst eine Ausnahme für den Python-Prozess einrichten.

---

## 19. Fehlerbehebung

### "❌ Root-Rechte erforderlich"

```bash
# Linux:
sudo python3 netfiremon_web.py

# Windows: Rechtsklick auf Eingabeaufforderung → "Als Administrator ausführen"
```

### "❌ Scapy nicht gefunden"

```bash
pip install scapy
# oder
pip install -r requirements.txt
```

### "Npcap nicht gefunden" (Windows)

Lade Npcap von [npcap.com](https://npcap.com) herunter und installiere es. Setze bei der Installation den Haken **"WinPcap API-compatible Mode"**.

### Web-Interface nicht erreichbar

1. Prüfe ob der Dienst läuft: `sudo systemctl status netfiremon-web`
2. Prüfe die Firewall: Port 5443 muss freigegeben sein
3. Prüfe die Logs: `sudo journalctl -u netfiremon-web -n 50`

### Zu viele Alarme / Alarm-Flut

1. Erhöhe den **Schwellenwert** (Config → threshold) auf z.B. 80%
2. Erhöhe den **globalen Cooldown** (Listen → Alarm-Cooldown)
3. Nutze **Stummschaltung** für bekannte harmlose Dienste
4. Setze vertrauenswürdige IPs auf die **Whitelist**

---

> **Net-Fire-Monitor v3.9.3** – (C) 2023-2026 Manuel Person, Innobytix-IT
>
> Dieses Tool wurde mit Sorgfalt entwickelt und auditiert. Bei Fragen oder Problemen erstelle ein Issue auf GitHub.
