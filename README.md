# Screen Capture & Overlay Application

Dieses Python-Projekt bietet eine Anwendung zum Aufnehmen von Bildschirminhalten mit einem überlagerten Fenster. Es ermöglicht eine benutzerfreundliche Bildschirmaufnahme mit verschiedenen Features wie Größenänderungen, Positionierung auf mehreren Bildschirmen und einer überlagerten Anzeige, die dynamisch anpassbar ist.

### Beispielanwendung
Diese Anwendung ist ideal, wenn du während eines Meetings oder einer Bildschirmfreigabe in Tools wie **Microsoft Teams**, **Zoom** oder **Google Meet** nur bestimmte Teile deines (sehr großen) Bildschirms teilen möchtest. Die Anwendung ermöglicht dir, einen festgelegten Bereich deines Bildschirms aufzunehmen, anstatt den gesamten Bildschirm oder nur eine Anwendung zu teilen.

## Features

### 1. **Fenster zur Bildschirmaufnahme**
   - Das Hauptfenster, `ScreenCaptureWindow`, wird verwendet, um einen bestimmten Bereich des Bildschirms zu erfassen und anzuzeigen.
   - Das Fenster kann in seiner Größe und Position angepasst werden, wobei das Seitenverhältnis des Overlay-Fensters beibehalten wird.

### 2. **Overlay-Fenster**
   - Ein überlagerndes Fenster, `OverlayWindow`, wird verwendet, um eine Transparenz zu erzeugen und als Auswahlrahmen für die Bildschirmaufnahme zu dienen.
   - Es kann verschoben und in der Größe geändert werden, wobei das Seitenverhältnis an das Ausgabefenster angepasst wird.

### 3. **Tastenkürzel**
   - **Strg + Q**: Beendet die Anwendung.
   - **Strg + Doppelklick**: Verschiebt das Ausgabefenster auf den nächsten verfügbaren Bildschirm.
   
### 4. **Fenstergrößenanpassung mit Begrenzung**
   - Das Ausgabefenster passt sich automatisch an die Größe des Monitors an, bleibt jedoch innerhalb der Begrenzungen des Bildschirms (ohne Taskleiste).
   - Die maximale Größe des Fensters wird an die verfügbaren Bildschirmabmessungen angepasst, wobei das Seitenverhältnis beibehalten wird.

### 5. **Mehrbildschirmunterstützung**
   - Die Anwendung unterstützt mehrere Bildschirme. Sie kann das Fenster auf einen anderen Bildschirm verschieben, basierend auf der Position des Cursors oder mithilfe der Funktion **Strg + Doppelklick**.
   - Das Ausgabefenster kann über das Feature "move_to_next_screen()" zyklisch zwischen allen verfügbaren Bildschirmen bewegt werden.

### 6. **Mauszeiger-Tracking**
   - Der Mauszeiger wird im Ausgabefenster angezeigt, und seine Position wird entsprechend dem Verhältnis des Aufnahmefensters zum Ausgabefenster skaliert.
   - Ein Fadenkreuz zeigt die Position des Mauszeigers relativ zur Aufnahme.

### 7. **Fensterinteraktionen**
   - **Doppelklick**: Maximiert das Fenster auf dem aktuellen Bildschirm, wobei das Seitenverhältnis beibehalten wird.
   - Das Fenster kann per Maus gezogen und in der Größe angepasst werden, während das Seitenverhältnis des Overlay-Fensters berücksichtigt wird.

## Installation

### Voraussetzungen
- Python 3.x
- `PyQt5`
- `Pillow`
- `numpy`
- `pyautogui`

Du kannst die erforderlichen Pakete mit dem folgenden Befehl installieren:

```bash
pip install PyQt5 Pillow numpy pyautogui
```

### Verwendung

1. Klone das Repository:

```bash
git clone https://github.com/deinbenutzername/screen-capture-overlay.git
cd screen-capture-overlay
```

2. Führe das Python-Skript aus:

```bash
python main.py
```

3. Die Anwendung startet mit dem Overlay-Fenster. Du kannst die Region anpassen und das Hauptfenster, das den Aufnahmebereich anzeigt, wird angezeigt.

## Bedienung

### Steuerung und Interaktion:
- **Verschieben des Fensters**: Klicke auf das Fenster und ziehe es an die gewünschte Position.
- **Größenänderung des Fensters**: Klicke auf die Ecken des Fensters, um es in der Größe zu ändern.
- **Doppelklick auf das Fenster**: Maximiert das Fenster auf die volle Bildschirmgröße (ohne Taskleiste).
- **Strg + Doppelklick**: Verschiebt das Fenster auf den nächsten verfügbaren Bildschirm.
- **Strg + Q**: Beendet die Anwendung.

## Projektstruktur

```
.
├── main.py            # Hauptskript der Anwendung
├── README.md          # Dokumentation
├── screen_capture_settings.ini  # Speichert die letzten Einstellungen des ScreenCaptureWindow
├── overlay_settings.ini         # Speichert die letzten Einstellungen des OverlayWindow
```

## Hinweise

- Die Fenstergrößen- und Positionsdaten werden in den `ini`-Dateien (`screen_capture_settings.ini`, `overlay_settings.ini`) gespeichert und beim Neustart der Anwendung wiederhergestellt.
- Die Anwendung wurde für die Arbeit auf mehreren Bildschirmen entwickelt und unterstützt Bildschirmübergänge für eine nahtlose Bedienung.