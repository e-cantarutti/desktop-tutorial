import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import os

def get_mt5_data():
    """Connects to MetaTrader 5, downloads historical OHLCV data for specified symbols and timeframes,
    and saves it to CSV files.
    """
    # --- User Configuration ---
    # Please fill in your MetaTrader 5 credentials and server name
    # It's recommended to run this script in an environment where you can input these securely.
    login = input("Enter your MT5 Login: ")
    password = input("Enter your MT5 Password: ")
    server = input("Enter your MT5 Server: ")

    symbols = ["GBPUSD", "EURUSD", "USDCHF", "USDJPY"]
    # MT5 Timeframe constants
    timeframes_mt5 = {
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }

    # Data range: 10 years from today
    date_to = datetime.now()
    date_from = date_to - timedelta(days=10*365)

    output_directory = "mt5_historical_data"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")

    # --- Connect to MetaTrader 5 ---
    print("\nConnecting to MetaTrader 5...")
    if not mt5.initialize(login=int(login), password=password, server=server):
        print(f"initialize() failed, error code = {mt5.last_error()}")
        print("Please ensure MetaTrader 5 terminal is running and credentials are correct.")
        return
    else:
        print("Successfully connected to MetaTrader 5.")

    # --- Data Collection ---
    for symbol in symbols:
        print(f"\nProcessing symbol: {symbol}")
        # Ensure symbol is available
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Symbol {symbol} not found, skipping.")
            continue
        
        if not mt5.symbol_select(symbol, True):
            print(f"Failed to select symbol {symbol}, skipping. Error: {mt5.last_error()}")
            continue
        else:
            print(f"Symbol {symbol} selected.")

        for tf_name, tf_mt5 in timeframes_mt5.items():
            print(f"  Fetching data for timeframe: {tf_name}...")
            try:
                # Request historical data
                rates = mt5.copy_rates_range(symbol, tf_mt5, date_from, date_to)

                if rates is None or len(rates) == 0:
                    print(f"    No data obtained for {symbol} - {tf_name}. Error: {mt5.last_error()}")
                    continue

                # Convert to pandas DataFrame
                rates_df = pd.DataFrame(rates)
                # Convert time in seconds to datetime format
                rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
                rates_df.set_index('time', inplace=True)
                
                # Select and rename columns to standard OHLCV + Volume
                rates_df = rates_df[['open', 'high', 'low', 'close', 'tick_volume']]
                rates_df.rename(columns={'tick_volume': 'volume'}, inplace=True)

                # Save to CSV
                file_name = f"{symbol}_{tf_name}_data.csv"
                file_path = os.path.join(output_directory, file_name)
                rates_df.to_csv(file_path)
                print(f"    Data saved to {file_path} ({len(rates_df)} rows)")

            except Exception as e:
                print(f"    An error occurred while fetching/processing {symbol} - {tf_name}: {e}")

    # --- Shutdown MetaTrader 5 connection ---
    mt5.shutdown()
    print("\nMetaTrader 5 connection closed.")
    print(f"All requested data has been attempted to be downloaded to the '{output_directory}' folder.")
    print("Please check the folder for the CSV files.")

if __name__ == "__main__":
    print("-------------------------------------------------------------------------")
    print("MetaTrader 5 Historical Data Downloader")
    print("-------------------------------------------------------------------------")
    print("This script will connect to your MetaTrader 5 account to download")
    print("historical OHLCV data for specified Forex pairs and timeframes.")
    print("The data will be saved as CSV files in a 'mt5_historical_data' subfolder.")
    print("\nIMPORTANT:")
    print("- Ensure your MetaTrader 5 terminal is running before executing this script.")
    print("- You will be prompted to enter your MT5 login, password, and server.")
    print("- This script does NOT store your credentials after execution.")
    print("-------------------------------------------------------------------------")
    get_mt5_data()

