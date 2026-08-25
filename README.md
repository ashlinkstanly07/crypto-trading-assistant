# Crypto Compass

A personal crypto market-research dashboard, risk planner, and trade journal.

> This project is educational software, not financial advice. It never connects to an exchange and cannot place trades.

## What it does

- Reads current market prices for your selected watchlist from CoinGecko's public API
- Shows a seven-day price chart
- Calculates a maximum position size from your account and risk limit
- Saves personal trade-plan notes locally in `data/trade_journal.csv`
- Lets you download the journal as a CSV file

## Run it on your computer

1. Install [Python 3.11 or newer](https://www.python.org/downloads/). During installation, enable **Add Python to PATH**.
2. Install [Git for Windows](https://git-scm.com/download/win) so you can upload changes from your computer to GitHub.
3. Open PowerShell in this project folder.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

5. Install the packages:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the dashboard:

   ```powershell
   streamlit run app.py
   ```

Streamlit will open the dashboard in your browser, usually at `http://localhost:8501`.

## Put it on GitHub

1. On GitHub, create a new empty repository named `crypto-compass`. Do **not** add a README or `.gitignore` there, because this project already has them.
2. In PowerShell, from this folder, run:

   ```powershell
   git init
   git add .
   git commit -m "Create Crypto Compass dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/crypto-compass.git
   git push -u origin main
   ```

3. Replace `YOUR-USERNAME` with your GitHub username. GitHub will ask you to sign in if needed.

## Important safety choices

- Your private journal file is excluded from Git using `.gitignore`.
- Do not put exchange API keys, passwords, or seed phrases in this project.
- Test strategies with paper trading before using real money.

## Next improvements

1. Add a paper-trading portfolio with fees and trade exits.
2. Add performance metrics: win rate, average gain/loss, and drawdown.
3. Add alerts with a secure notification provider.
4. Only after extensive testing, investigate an exchange integration with withdrawals disabled and strict trading limits.
