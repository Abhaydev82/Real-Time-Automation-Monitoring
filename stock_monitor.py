import time
import sys
import subprocess
from datetime import datetime

# Try to import yfinance
try:
    import yfinance as yf
except ImportError:
    print("CRITICAL ERROR: 'yfinance' library is not installed.")
    print("Please run: pip install yfinance")
    sys.exit(1)

import requests

# --- CONFIGURATION (TELEGRAM) ---
# You can leave these empty if you only want console output
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_alert(message):
    """Sends a notification to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        # Silent return if not configured
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"  [!] Failed to send Telegram alert: {e}")

def get_real_time_price(ticker_symbol):
    """
    Fetches the latest price for the given ticker using yfinance.
    Returns (price, currency) or None if failed.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        # fast_info is efficient for real-time monitoring
        price = stock.fast_info.last_price
        currency = stock.fast_info.currency
        return price, currency
    except Exception as e:
        # Fallback or error handling
        return None, None

def get_user_preferences():
    """
    Interactive prompt to get user's choice of Exchange and Company.
    """
    while True:
        print("\n" + "="*40)
        print("  STOCK MONITOR SETTINGS")
        print("="*40)
        print("Select Exchange:")
        print("1. NASDAQ (US Markets)")
        print("2. BSE (Bombay Stock Exchange)")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == '1':
            exchange_suffix = ""
            exchange_name = "NASDAQ"
            example = "AAPL, TSLA, MSFT"
            break
        elif choice == '2':
            exchange_suffix = ".BO"
            exchange_name = "BSE"
            example = "RELIANCE, TCS, INFY"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    while True:
        company = input(f"\nEnter Stock Symbol for {exchange_name} (e.g., {example}): ").strip().upper()
        if company:
            # Append suffix if needed
            full_ticker = company if company.endswith(exchange_suffix) else company + exchange_suffix
            
            # Quick validation check
            print(f"Validating '{full_ticker}'...")
            price, _ = get_real_time_price(full_ticker)
            if price is not None:
                print(f"Success! Found {full_ticker} at {price}")
                return full_ticker, exchange_name
            else:
                print(f"Could not find data for '{full_ticker}'. Please check the symbol and try again.")
        else:
            print("Symbol cannot be empty.")

def main():
    print("Initializing Real-Time Stock Price Monitor...")
    
    # Initial Configuration
    current_ticker, current_exchange = get_user_preferences()
    
    print(f"\nStarted monitoring {current_ticker} on {current_exchange}...")
    print("Updates every 20 seconds.")
    print("Press Ctrl+C at any time to Change Settings or Exit.")
    
    while True:
        try:
            # Main Monitoring Loop
            timestamp = datetime.now().strftime("%H:%M:%S")
            price, currency = get_real_time_price(current_ticker)
            
            if price is not None:
                # Status message
                status_msg = f"[{timestamp}] {current_ticker}: {price:.2f} {currency}"
                print(status_msg)
                
                # Speak the price
                try:
                    # 'say' is built-in on macOS
                    subprocess.run(["say", f"The price of {current_ticker} is {int(price)} {currency}"], check=False)
                except Exception:
                    pass # Fail silently if 'say' doesn't work
                
                # Optional: Send Telegram alert on valid fetch (or only on specific conditions)
                # For now, we just delivering status as requested.
            else:
                print(f"[{timestamp}] Failed to fetch price for {current_ticker}")
            
            # Wait for 20 seconds
            time.sleep(20)

        except KeyboardInterrupt:
            # Handle User Interruption to Change Settings or Exit
            print("\n\n" + "!"*40)
            print("  PAUSED")
            print("!"*40)
            print("What would you like to do?")
            print("1. Change Exchange/Company")
            print("2. Exit Application")
            print("3. Resume")
            
            user_choice = input("Enter choice: ").strip()
            
            if user_choice == '1':
                current_ticker, current_exchange = get_user_preferences()
                print(f"\nResuming with new settings: {current_ticker}...")
            elif user_choice == '2':
                print("Exiting. Goodbye!")
                break
            else:
                print("Resuming...")
                
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
