# Bitcoin Blockclock

A simple fullscreen blockclock for Bitcoin data. The app shows the current block height prominently in the center, with additional network information below it, such as difficulty, halving progress, mempool data, fees, and hashrate.

## Starting

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
python main.py
```

If `python` points to an older version on your system, use:

```bash
python3 main.py
```

The app requires an internet connection because Bitcoin data is loaded from external APIs.

## Controls

- `F11`: Toggle fullscreen mode
- `Escape`: Exit the app
- Click the Bitcoin logo in the top-right corner: Open settings
- Click the lower area of the screen: Exit the app

Data is refreshed automatically about every 20 seconds. The time of the last update is shown at the bottom of the screen.

## Settings

Open the settings by clicking the Bitcoin logo in the top-right corner.

### Info

In the `Info` tab, you can choose which detail values are shown on the main screen:

- `Difficulty`
- `Halving`
- `Next Adjustment`
- `Tx Count`
- `Txs (Mempool)`
- `Block Fees`
- `Mempool Fees`
- `Hashrate`

Enabled switches are shown on the main screen. Click `Apply` after changing the selection.

### Colors

In the `Colors` tab, you can customize the display colors:

- `background`: Background color
- `text`: Detail text color
- `blockheight`: Large block height color

Click a color swatch, choose a color, then click `Apply`.

Note: Current settings are only applied for the running app session. After restarting the app, the default colors and default info values are used again.

## Raspberry Pi

Python 3.9 or newer is recommended.

Check your Python version:

```bash
python --version
python3 --version
```

If `python main.py` causes issues but `python3` shows a suitable version, start the app with:

```bash
python3 main.py
```

For fullscreen use on a Raspberry Pi, start the app from a graphical desktop session, not from a plain SSH-only terminal.

## Troubleshooting

If the main screen shows `Error`, the data could not be loaded. Check:

- Internet connection
- Whether the dependencies are installed
- Whether the app was started from the project folder, so `assets/bitcoin_logo.png` can be found
