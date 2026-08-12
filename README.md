# Supa Fighta

## Project Description

Supa Fighta is a one-hit KO fighting game designed as a hobby project. Experience fast-paced, skill-based combat where a single precise strike decides victory is what we would've liked to say if we didn't have the collective IQ of a rock.

## Visuals

![Supa Fighta Gameplay](./assets/supa-fighta.gif)

## Getting Started

### Download

Download `supa-fighta-client.zip` from the latest [release](https://github.com/adeelakmal/Supa-Fighta/releases), extract it, and run `main.exe`.

Keep `main.exe` and the `assets` folder together. Prebuilt releases currently support Windows only.

### Run Locally

Requires Python 3.12.

```bash
cd supa-fighta-client
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py
```

Run the client from `supa-fighta-client` so it can find its assets. The client connects to the hosted game server by default.

#### Ubuntu

Install Tkinter if it is not included with Python:

```bash
sudo apt install python3-tk
```

#### WSL

Install PulseAudio support and use the WSLg audio server:

```bash
sudo apt install libpulse0
SDL_AUDIODRIVER=pulseaudio python src/main.py
```

To run without audio:

```bash
SDL_AUDIODRIVER=dummy python src/main.py
```

## How to Play

### Controls

- **Movement**: Use directional buttons on your keyboard to move your character
- **Dash**: Press a direction button twice to perform a quick dash
- **Punch**: Press the **Spacebar** to attack
- **Parry**: Press the **A** key to parry incoming attacks

*Note: Controller support will be added in a future update.*

## Display resolutions and pixel art

The Settings menu supports 640x360, 1280x720, and 1920x1080. Gameplay,
collisions, networking, and asset layout always use a 640x360 logical canvas;
only the finished frame is scaled for display. The 2x and 3x modes use
nearest-neighbor scaling so pixel edges stay sharp.

Keep one canonical set of sprite sheets at their current resolution. Separate
720p and 1080p asset folders, or manually enlarging the same pixels in Aseprite,
would produce the same image while increasing file size and maintenance work.
Create a higher-resolution variant only when it contains newly drawn detail.

## Technologies Used

- **Client**: [Pygame](https://www.pygame.org/) - Python-based game development library
- **Server**: [Node.js](https://nodejs.org/) - Backend game server implementation
- **Database**: [PostgreSQL](https://www.postgresql.org/) - Data persistence and player management

## Contributing Guidelines

We're open to contributions! We especially welcome help with:
- Music composition and audio design
- Art and visual assets
- Bug fixes and gameplay improvements

### How to Contribute

- **Report Issues**: Use the [Issues](https://github.com/adeelakmal/Supa-Fighta/issues) section to report bugs or suggest features
- **Submit Pull Requests**: Feel free to fork the repository and submit pull requests with improvements
- **Get in Touch**: Reach out to us directly if you'd like to collaborate on specific aspects

## Project Status

🚧 **Work in Progress** - This project is in the early stages of implementation. Expect ongoing updates, new features, and improvements as development continues.
