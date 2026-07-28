import json
import yfinance as yf
from datetime import datetime

# Exakt deine 30 ausgewählten Ticker mit sauberen Klarnamen
TICKERS = {
    "SAP.DE": "SAP",
    "SY1.DE": "Symrise",
    "FPE.DE": "Fuchs SE",
    "G24.DE": "Scout24",
    "DWS.DE": "DWS Group",
    "SIE.DE": "Siemens",
    "SHL.DE": "Siemens Healthineers",
    "BC8.DE": "Bechtle",
    "KWS.DE": "KWS Saat",
    "NEM.DE": "Nemetschek",
    "ALV.DE": "Allianz",
    "ACT.DE": "Alzchem Group",
    "ELG.DE": "Elmos Semiconductor",
    "MRK.DE": "Merck",
    "DHL.DE": "DHL Group",
    "G1A.DE": "GEA Group",
    "HNR1.DE": "Hannover Rück",
    "TLX.DE": "Talanx",
    "MUV2.DE": "Münchener Rück",
    "AOF.DE": "ATOSS Software",
    "RAA.DE": "Rational",
    "HEI.DE": "Heidelberg Materials",
    "JEN.DE": "Jenoptik",
    "RHM.DE": "Rheinmetall",
    "DB1.DE": "Deutsche Börse",
    "BEI.DE": "Beiersdorf",
    "KRN.DE": "Krones",
    "KSB3.DE": "KSB (Vorzug)",
    "DTE.DE": "Deutsche Telekom",
    "RWE.DE": "RWE"
}

def get_dividend_data(symbol, clean_name):
    print(f"Lade Daten für: {clean_name} ({symbol})...")
    ticker = yf.Ticker(symbol)
    
    # 1. Aktueller Preis & Dividendenrendite
    info = ticker.info
    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
    
    divs = ticker.dividends
    if divs.empty or current_price == 0:
        return None

    # Dividenden nach Jahren gruppieren
    divs.index = divs.index.tz_localize(None)
    annual_divs = divs.groupby(divs.index.year).sum()
    
    current_year = datetime.now().year
    completed_years = [y for y in annual_divs.index if y < current_year]
    
    if len(completed_years) < 2:
        return None
        
    recent_divs = [annual_divs[y] for y in sorted(completed_years, reverse=True)]
    
    latest_div = recent_divs[0]
    dividend_yield = round((latest_div / current_price) * 100, 2)

    # 2. Jahre ohne Senkung zählen
    years_no_cut = 0
    for i in range(len(recent_divs) - 1):
        if recent_divs[i] >= recent_divs[i+1] * 0.995:
            years_no_cut += 1
        else:
            break

    # 3. Jahre in Folge gesteigert zählen
    years_increased = 0
    for i in range(len(recent_divs) - 1):
        if recent_divs[i] > recent_divs[i+1] * 1.001:
            years_increased += 1
        else:
            break

    # 4. 10-Jahres CAGR berechnen
    cagr_10y = "-"
    if len(recent_divs) >= 10 and recent_divs[9] > 0:
        cagr = ((recent_divs[0] / recent_divs[9]) ** (1/9) - 1) * 100
        cagr_10y = round(cagr, 2)
    elif len(recent_divs) >= 5 and recent_divs[4] > 0:
        cagr = ((recent_divs[0] / recent_divs[4]) ** (1/4) - 1) * 100
        cagr_10y = round(cagr, 2)

    return {
        "name": clean_name,
        "symbol": symbol,
        "yield": dividend_yield,
        "years_no_cut": years_no_cut,
        "years_increased": years_increased,
        "cagr_10y": cagr_10y
    }

def main():
    champions_list = []
    
    for symbol, name in TICKERS.items():
        try:
            data = get_dividend_data(symbol, name)
            if data:
                champions_list.append(data)
        except Exception as e:
            print(f"Fehler bei {symbol}: {e}")

    # Nach Dividendenrendite absteigend sortieren
    champions_list.sort(key=lambda x: x['yield'], reverse=True)

    # JSON-Datei speichern
    with open('champions.json', 'w', encoding='utf-8') as f:
        json.dump(champions_list, f, ensure_ascii=False, indent=2)

    print(f"\nFertig! Genau {len(champions_list)} Unternehmen in champions.json gespeichert.")

if __name__ == "__main__":
    main()
