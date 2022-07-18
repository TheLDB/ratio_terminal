<p align="center">
  <img src="./art/main.png" width="300"/>
</p>

<h1 align="center">Ratio Terminal</h1>
<p align="center">Remember Twitter ratios? Well, here these are for Discord.</p>

<a href="https://hub.docker.com/r/kitwnd/ratio_terminal"><p align="center">Docker Hub</p></a>

### Setup

#### Docker (recommended)

- Clone/download this repo
- Rename `data/.env.example` to `data/.env` and add your bot token to that file.
- `docker-compose up -d`

#### Manual

- Python 3.10 recommended
- Clone/download this repo
- `pip install -r requirements.txt`
- Rename `data/.env.example` to `data/.env` and add your bot token to that file.
- `python3 src/main.py`

### License

MIT
