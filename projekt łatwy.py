from numpy._core.defchararray import index

import pandas as pd
import io
import zipfile as zip
import requests as req


# ===================================================================================================================================
# K R O K   1 :   I M P O R T   S U R O W Y C H   D A N Y C H
# ===================================================================================================================================

sezony = ["2627", "2526", "2425"]                                                 # pobieramy liste sezonów

dane_mecze_surowe = []                                                            # tworzymy pustą liste

for sezon in sezony:

    url = f"https://www.football-data.co.uk/mmz4281/{sezon}/data.zip"

    odpowiedz = req.get(url, timeout=30)
    odpowiedz.raise_for_status()

    with zip.ZipFile(io.BytesIO(odpowiedz.content)) as archiwum:

        pliki_csv = [plik for plik in archiwum.namelist()
                     if plik.lower().endswith(".csv")]

        for nazwa_pliku in pliki_csv:

            with archiwum.open(nazwa_pliku) as plik:

                dane_ligi = pd.read_csv(plik)

            dane_ligi["Sezon"] = sezon

            dane_mecze_surowe.append(dane_ligi)


dane_mecze_surowe = pd.concat(dane_mecze_surowe, ignore_index=True)

tlumaczenia = {
    "Div": "Liga",
    "Date": "Data",
    "Time": "Godzina",
    "HomeTeam": "Gospodarze",
    "AwayTeam": "Goscie",
    "Referee": "Sedzia",

    "FTHG": "Gole_gospodarzy",
    "FTAG": "Gole_gosci",
    "FTR": "Wynik_koncowy",
    "HTHG": "Gole_gospodarzy_do_przerwy",
    "HTAG": "Gole_gosci_do_przerwy",
    "HTR": "Wynik_do_przerwy",

    "HS": "Strzaly_gospodarzy",
    "AS": "Strzaly_gosci",
    "HST": "Strzaly_celne_gospodarzy",
    "AST": "Strzaly_celne_gosci",
    "HF": "Faule_gospodarzy",
    "AF": "Faule_gosci",
    "HC": "Rozne_gospodarzy",
    "AC": "Rozne_gosci",
    "HY": "Zolte_kartki_gospodarzy",
    "AY": "Zolte_kartki_gosci",
    "HR": "Czerwone_kartki_gospodarzy",
    "AR": "Czerwone_kartki_gosci",
    "HxG": "Oczekiwane_gole_gospodarzy",
    "AxG": "Oczekiwane_gole_gosci",

    "B365H": "Bet365_wygrana_gospodarzy",
    "B365D": "Bet365_remis",
    "B365A": "Bet365_wygrana_gosci",
    "B365CH": "Bet365_koncowy_kurs_gospodarze",
    "B365CD": "Bet365_koncowy_kurs_remis",
    "B365CA": "Bet365_koncowy_kurs_goscie",

    "BWH": "Betwin_wygrana_gospodarzy",
    "BWD": "Betwin_remis",
    "BWA": "Betwin_wygrana_gosci",
    "BWHCH": "Betwin_koncowy_kurs_gospodarze",
    "BWCD": "Betwin_koncowy_kurs_remis",
    "BWCA": "Betwin_koncowy_kurs_goscie",

    "PSH": "Pinnacle_wygrana_gospodarzy",
    "PSD": "Pinnacle_remis",
    "PSA": "Pinnacle_wygrana_gosci",
    "PSCH": "Pinnacle_koncowy_kurs_gospodarze",
    "PSCD": "Pinnacle_koncowy_kurs_remis",
    "PSCA": "Pinnacle_koncowy_kurs_goscie",

    "MaxH": "Maksymalny_kurs_gospodarze",
    "MaxD": "Maksymalny_kurs_remis",
    "MaxA": "Maksymalny_kurs_goscie",
    "AvgH": "Sredni_kurs_gospodarze",
    "AvgD": "Sredni_kurs_remis",
    "AvgA": "Sredni_kurs_goscie",

    "MaxCH": "Maksymalny_kurs_koncowy_gospodarze",
    "MaxCD": "Maksymalny_kurs_koncowy_remis",
    "MaxCA": "Maksymalny_kurs_koncowy_goscie",
    "AvgCH": "Sredni_kurs_koncowy_gospodarze",
    "AvgCD": "Sredni_kurs_koncowy_remis",
    "AvgCA": "Sredni_kurs_koncowy_goscie",

    "B365>2.5": "Bet365_powyzej_2_5_gola",
    "B365<2.5": "Bet365_ponizej_2_5_gola",
    "B365C>2.5": "Bet365_koncowy_powyzej_2_5_gola",
    "B365C<2.5": "Bet365_koncowy_ponizej_2_5_gola",

    "P>2.5": "Pinnacle_powyzej_2_5_gola",
    "P<2.5": "Pinnacle_ponizej_2_5_gola",
    "PC>2.5": "Pinnacle_koncowy_powyzej_2_5_gola",
    "PC<2.5": "Pinnacle_koncowy_ponizej_2_5_gola",

    "Max>2.5": "Maksymalny_kurs_powyzej_2_5_gola",
    "Max<2.5": "Maksymalny_kurs_ponizej_2_5_gola",
    "Avg>2.5": "Sredni_kurs_powyzej_2_5_gola",
    "Avg<2.5": "Sredni_kurs_ponizej_2_5_gola",

    "MaxC>2.5": "Maksymalny_kurs_koncowy_powyzej_2_5",
    "MaxC<2.5": "Maksymalny_kurs_koncowy_ponizej_2_5",
    "AvgC>2.5": "Sredni_kurs_koncowy_powyzej_2_5",
    "AvgC<2.5": "Sredni_kurs_koncowy_ponizej_2_5",

    "AHh": "Handicap_azjatycki_gospodarzy",
    "B365AHH": "Bet365_handicap_azjatycki_gospodarze",
    "B365AHA": "Bet365_handicap_azjatycki_goscie",
    "PAHH": "Pinnacle_handicap_azjatycki_gospodarze",
    "PAHA": "Pinnacle_handicap_azjatycki_goscie",

    "AHCh": "Koncowy_handicap_azjatycki_gospodarzy",
    "B365CAHH": "Bet365_koncowy_handicap_gospodarze",
    "B365CAHA": "Bet365_koncowy_handicap_goscie",
    "PCAHH": "Pinnacle_koncowy_handicap_gospodarze",
    "PCAHA": "Pinnacle_koncowy_handicap_goscie"
}

dane_mecze = dane_mecze_surowe.rename(columns=tlumaczenia)

dane_mecze = dane_mecze.loc[:, dane_mecze.isna().mean() <= 0.10]

display(dane_mecze)

print("Liczba wszystkich kolumn:", len(dane_mecze.columns))
print("Liczba przetlumaczonych kolumn:", sum(k in dane_mecze_surowe.columns for k in tlumaczenia))
print("Kolumny bez tlumaczenia:")
print([k for k in dane_mecze_surowe.columns if k not in tlumaczenia])
display(dane_mecze_surowe)

print("Liczba wierszy:", dane_mecze_surowe.shape[0])
print("Liczba kolumn:", dane_mecze_surowe.shape[1])
print("Liczba lig:", dane_mecze_surowe["Div"].nunique())
print("Liczba sezonów:", dane_mecze_surowe["Sezon"].nunique())
print("Liczba meczów:", dane_mecze_surowe.shape[0])
print("Liczba wszystkich Nan:", dane_mecze_surowe.isna().sum().sum())
print("Liczba Nan w poszczególnych kolumnach:"),display(dane_mecze_surowe.isna().sum().sort_values(ascending=False))

print("Liczba wszystkich kolumn:", len(dane_mecze.columns))
print("Liczba przetlumaczonych kolumn:", sum(k in dane_mecze_surowe.columns and tlumaczenia[k] in dane_mecze.columns for k in tlumaczenia))
print("Kolumny bez tlumaczenia:")
print([k for k in dane_mecze.columns if k not in tlumaczenia.values()])

display(dane_mecze)

print("Liczba wierszy:", dane_mecze.shape[0])
print("Liczba kolumn:", dane_mecze.shape[1])
print("Liczba lig:", dane_mecze["Liga"].nunique())
print("Liczba sezonów:", dane_mecze["Sezon"].nunique())
print("Liczba meczów:", dane_mecze.shape[0])
print("Liczba wszystkich NaN:", dane_mecze.isna().sum().sum())
print("Liczba NaN w poszczególnych kolumnach:")
display(dane_mecze.isna().sum().sort_values(ascending=False))

braki = dane_mecze[dane_mecze["Rozne_gosci"].isna()]

display(braki.groupby(["Sezon", "Liga"]).size().reset_index(name="Brakujace_mecze"))