# Mac setup: Bambu Lab + Claude Desktop

This takes about 20 minutes. You'll end up with:

| Piece | What it does |
|---|---|
| **Bambu Studio** | Official slicer; also handles cloud/Handy-app printing |
| **OrcaSlicer** | Open-source slicer with better calibration tools (optional) |
| **OpenSCAD**, **Blender** | Modeling apps that Claude can drive through connectors |
| **openscad** connector | Claude writes OpenSCAD, renders previews, exports STL in chat |
| **blender** connector | Claude controls a live Blender scene |
| **bambu** connector | Claude sends sliced files to your printer, checks status, picks AMS slots |
| **filesystem** connector | Claude Desktop can read/write this repo's `out/` files |

## 1. Install everything

Open **Terminal** (Cmd+Space, type "Terminal"), then:

```bash
git clone https://github.com/EliasWaicho/Claude-zoo.git ~/Claude-zoo
cd ~/Claude-zoo
bash setup/install-mac.sh
```

This installs Homebrew (if missing), `uv`, Node, Python, Bambu Studio,
OrcaSlicer, OpenSCAD and Blender, then builds the example wall hook to prove it works.

## 2. Get your printer's connection details

On the printer's touchscreen, go to **Settings → Network (WLAN)**:

- **IP address**: e.g. `192.168.1.57` → `PRINTER_HOST`
- **Access Code**: 8 characters → `BAMBU_TOKEN`
- **LAN Only / Developer Mode**: recent Bambu firmware only lets third-party
  tools control the printer when **LAN Only mode + Developer Mode** are on.
  Turning them on disconnects the Bambu Handy app and cloud printing. Skip this if you'd rather keep
  the cloud; the other connectors still work, and you'd send prints from Bambu Studio.

**Serial number**: printer **Settings → Device** (or Bambu Studio → Device tab) → `BAMBU_SERIAL`

**Model**: lowercase code, e.g. `a1`, `a1mini`, `p1s`, `p1p`, `x1c`, `h2d` → `BAMBU_MODEL`

**Tip:** give the printer a fixed IP address in your router settings so it doesn't change.

## 3. Add the connectors to Claude Desktop

1. Claude Desktop → **Settings → Developer → Edit Config**. This opens
   `~/Library/Application Support/Claude/claude_desktop_config.json`.
2. Paste in the contents of [`claude_desktop_config.example.json`](claude_desktop_config.example.json)
   (merge it into `"mcpServers"` if the file already has some).
3. Replace the placeholders: printer IP, model, serial, access code, and `YOUR_NAME`
   (run `whoami` in Terminal to get it).
   - On an **Intel Mac**, change `/opt/homebrew/bin/` to `/usr/local/bin/`.
     (`which uvx` tells you the right path.)
   - Don't want one of them? Just delete that block.
4. **Quit Claude Desktop completely (Cmd+Q) and reopen it.** The connectors appear
   under the **+ → Connectors** menu in a chat.

**Keep your access code private.** It lives only in that local config file;
never commit it to this repo.

## 4. Blender add-on (only if you want the Blender connector)

```bash
uvx mcp-for-blender install-addon
```

Then in Blender: **Edit → Preferences → Add-ons**, enable **Interface: MCP for Blender**.
In the 3D view press **N** → **BlenderMCP** tab → **Connect to Claude**.
Blender has to be open, with that button pressed, whenever you use the connector.

## 5. Try it

In a new Claude Desktop chat:

- *"Use OpenSCAD to make a 40 mm cube with a 10 mm hole through it and show me a render."*
- *"What's my Bambu printer doing right now?"* (checks the bambu connector)
- *"In Blender, add a low-poly tree and export it as STL to ~/Desktop."*

Then print the example: open `~/Claude-zoo/out/wall_hook.3mf` in Bambu Studio,
pick your printer/filament, **Slice**, then **Print**. Or save it as a sliced
`.gcode.3mf` and ask Claude to *"print ~/Desktop/wall_hook.gcode.3mf on my Bambu"*.

## Troubleshooting

- **Connector shows an error / "spawn uvx ENOENT"**: the path in `command` is wrong.
  Run `which uvx` / `which npx` and use that full path.
- **Bambu connector can't connect**: check the IP (it may have changed), that LAN Only +
  Developer Mode are on, and that your Mac is on the same Wi-Fi as the printer.
- **Logs**: `~/Library/Logs/Claude/mcp-server-*.log`
- **Updating the repo's models**: `cd ~/Claude-zoo && git pull`
