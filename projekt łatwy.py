

from datetime import date, timedelta                                                # ściągamy moduł dat i moduł liczenia na datach
import pandas as pd                                                                 # do analizy danych
import yfinance as yf                                                               # do pobierania danych z yahoo finance
import streamlit as st                                                              # do tworzenia list rozwijanych, suwaków  itp
import plotly.express as px                                                         # do tworzenia wykresów

st.set_page_config(                                                                # konfigurujemy aplikację przed elementami Streamlit
    page_title="Panel analizy akcji",                                            # tytuł karty w przeglądarce
    layout="wide"                                                                  # pełna szerokość ekranu
)


# =============================================================================================================================================================================================================================
# K R O K   1 :   I M P O R T   S U R O W Y C H   D A N Y C H   ( 1 0   L A T   +   8 0   D N I   W S T E C Z )
# =============================================================================================================================================================================================================================


end_date = date.today()                                                             # ustawiamy datę końcową na dzisiaj
start_date = end_date - timedelta(days=(365 * 10) + 80)                             # ustawiamy zakres 10 lat i 80 dni wstecz

dane_spolki_surowe_list = [                                                         # pobieramy dane spółek
    "NVDA", "MSFT", "GOOGL", "META", "AAPL", "AMZN", "TSM", "AMD", "AVGO", "PLTR",
    "TSLA", "NFLX", "ORCL", "ADBE", "CRM", "INTC", "QCOM", "MU", "ASML", "PANW"
]

nazwy_spolek = {                                                                    # pełne nazwy spółek
    "NVDA": "NNVIDIA (Procesory graficzne)",
    "MSFT": "MICROSOFT (Windows)",
    "GOOGL": "ALPHABET (Wyszukiwarka, Youtube)",
    "META": "MMETA (Facebook, Instagram itp)",
    "AAPL": "AAPPLE (Iphone)",
    "AMZN": "AMAZON (Handel internetowy)",
    "TSM": "TTSMC (Układy scalone)",
    "AMD": "ADVANCED MICRO DEVICES (Procesory, karty graficzne)",
    "AVGO": "BBROADCOM (Półprzewodniki, sieć, oprogramowanie)",
    "PLTR": "PALANTIR TECHNOLOGIES (Platformy analizy danych, AI dla firm)",
    "TSLA": "TTESLA (Samochody elektryczne",
    "NFLX": "NETFLIX (Platforma streamingowa)",
    "ORCL": "ORACLE (Oprogramowanie, bazy danych)",
    "ADBE": "ADOBE (Photoshop, oprogramowanie)",
    "CRM": "SaSALESFORCE (Systemy CRM, oprogramowanie dla firm)",
    "INTC": "INTEL (Procesory, półprzewodniki)",
    "QCOM": "QUALCOMM (Procesory mobilne, 5G)",
    "MU": "MICRON TECHNOLOGY (Pamięć RAM, pamięć NAND)",
    "ASML": "ASML (Maszyny do produkcji półprzewodników)",
    "PANW": "PALO ALTO NETWORKS (Cyberbezpieczeństwo)"
}


dane_spolki_surowe = yf.download(                                                   # pobierany spółki
    dane_spolki_surowe_list,                                                        # tworzymy dane spółki surowe
    start=start_date,                                                               # ustaiwamy date początkową
    end=end_date,                                                                   # ustawiamy date końcową
    auto_adjust=True,                                                               # uwzględniamy korekty cen
    group_by="column"                                                              # kolumny grupujemy według rodzaju danych
)

print("Dane surowe pobrane")


# =============================================================================================================================================================================================================================
# K R O K   2 :   O B R Ó B K A   D A N Y C H   S P Ó Ł E K   +   W S K A Ź N I K I   T E C H N I C Z N E
# =============================================================================================================================================================================================================================


# OBRÓBKA DANYCH SPÓŁEK -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

dane_spolki = dane_spolki_surowe.stack(level="Ticker", future_stack=True).reset_index()                # zmieniamy tabelę szeroką na długą

dane_spolki = dane_spolki.rename(columns={                                          # zmieniamy nazwy na polskie
    "Date": "Data",
    "Ticker": "Symbol giełdowy",
    "Open": "Cena otwarcia",
    "Close": "Cena zamknięcia",
    "Low": "Cena najniższa",
    "High": "Cena najwyższa",
    "Volume": "Wolumen"
    })

dane_spolki = dane_spolki.sort_values(["Symbol giełdowy", "Data"])                  # sortujemy dane według symbolu giełdowego i daty

dane_spolki["Nazwa spółki"] = dane_spolki["Symbol giełdowy"].map(nazwy_spolek)      # dodajemy pełne nazwy spółek

dane_spolki["Data"] = dane_spolki["Data"].dt.date                                   # usuwamy godzinę 00:00:00 z daty

dane_spolki = dane_spolki[[                                                         # ustawiamy swoją kolejność kolumn
    "Data",
    "Symbol giełdowy",
    "Nazwa spółki",
    "Cena otwarcia",
    "Cena zamknięcia",
    "Cena najniższa",
    "Cena najwyższa",
    "Wolumen"
    ]]


# WSKAŹNIKI TECHNICZNE -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

dane_spolki["Zmiana dzienna (%)"] = (                                               # tworzymy nową kolumnę "zmiana dzienna (%)"
    dane_spolki.groupby("Symbol giełdowy")["Cena zamknięcia"].pct_change(fill_method=None) * 100)   # grupujemy spółki i liczymy zmiane wartości ceny zamkniecia względem poprzedniego dnia (pct_change) w procentach)

for okres in [10, 20, 50]:                                                          # wybieramy okresy do liczenie średnich cen zamknięcia
    dane_spolki[f"Średnia {okres}"] = (                                             # tworzymy kolumny z wartosci w okresie
        dane_spolki.groupby("Symbol giełdowy")["Cena zamknięcia"]                   # grupujemy społki i bierzemy "cena zamknięcia"
        .transform(lambda x, okres=okres: x.rolling(okres).mean()))                 # liczymy średnia z wartości w okresie

dane_spolki["Zmienność 20 (%)"] = (                                                 # tworzymy nową kolumnę "zmienność 20 (%)"
    dane_spolki.groupby("Symbol giełdowy")["Zmiana dzienna (%)"]                    # grupujemy społki i bierzemy "zmiana dzienna (%)
    .transform(lambda x: x.rolling(20).std()))                                      # obliczamy odchylenie standarowe (miara rozproszenia dziennych zmian)

dane_spolki = dane_spolki.dropna().reset_index(drop=True)                           # usuwamy wszystkie NaN i resetujemy indeks

dane_spolki.insert(0, "Lp.", range(1, len(dane_spolki) + 1))                        # dodajemy kolumnę Lp. z numeracją od 1




# =========================================================================================================================================
# K R O K  3 :  F U N K C J E  E L E M E N T Ó W  D A S H B O A R D U
# =========================================================================================================================================


#------------------------------------------------------------------------------------------------------------------------------------------
# WYBÓR SPÓŁKI
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_wybor_spolki():                                                                       # funkcja wyboru spółek
    return st.multiselect(                                                                      # zwracamy wybrane symbole
        "Symbol giełdowy:",                                                                     # etykieta pola
        options=sorted(dane_spolki["Symbol giełdowy"].unique()),                                # dostępne spółki
        format_func=lambda x: f"{x} — {nazwy_spolek.get(x, x)}"                                 # pełne nazwy
    )


#------------------------------------------------------------------------------------------------------------------------------------------
# WYBÓR WSKAŹNIKA
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_wybor_wskaznika():                                                                    # funkcja wyboru wskaźnika
    return st.selectbox(                                                                        # zwracamy wybrany wskaźnik
        "Wskaźniki:",                                                                           # etykieta pola
        options=[                                                                               # dostępne wskaźniki
            "Cena otwarcia",
            "Cena zamknięcia",
            "Cena najniższa",
            "Cena najwyższa",
            "Wolumen",
            "Zmiana dzienna (%)",
            "Średnia 10",
            "Średnia 20",
            "Średnia 50",
            "Zmienność 20 (%)"
        ],
        index=1                                                                                 # domyślnie wybrana cena zamknięcia
    )


#------------------------------------------------------------------------------------------------------------------------------------------
# WYBÓR OKRESU
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_wybor_okresu():                                                                       # funkcja wyboru okresu
    return st.slider(                                                                           # zwracamy liczbę dni
        "Okres dni:",                                                                           # etykieta suwaka
        min_value=1,                                                                            # minimum 1 dzień
        max_value=3650,                                                                         # maksimum 3650 dni
        value=365,                                                                              # początkowo 365 dni
        step=1                                                                                  # przesuwamy co jeden dzień
    )


#------------------------------------------------------------------------------------------------------------------------------------------
# WYBÓR RODZAJU WYKRESU
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_wybor_wykresu():                                                                      # funkcja wyboru wykresu
    return st.selectbox(                                                                        # zwracamy wybrany rodzaj
        "Wykres:",                                                                              # etykieta pola
        options=["Liniowy", "Słupkowy"]                                                         # dwa rodzaje wykresu
    )


#------------------------------------------------------------------------------------------------------------------------------------------
# PRZYGOTOWANIE DANYCH DO WYKRESU
#------------------------------------------------------------------------------------------------------------------------------------------

def przygotuj_dane_wykres(wybor_spolki, wybor_okresu):                                          # funkcja filtrująca dane

    dane_wykres = dane_spolki[                                                                  # wybieramy odpowiednie wiersze
        dane_spolki["Symbol giełdowy"].isin(wybor_spolki)                                       # pozostawiamy wybrane spółki
    ].copy()                                                                                    # tworzymy kopię danych

    if dane_wykres.empty:                                                                       # sprawdzamy, czy są dane
        return dane_wykres                                                                      # zwracamy pustą tabelę

    data_koncowa = pd.to_datetime(                                                              # pobieramy ostatnią datę
        dane_wykres["Data"].max()                                                               # najpóźniejsza data
    )

    data_poczatkowa = (                                                                         # obliczamy datę początkową
        data_koncowa - pd.Timedelta(days=wybor_okresu)                                          # cofamy się o wybraną liczbę dni
    )

    dane_wykres = dane_wykres[                                                                  # filtrujemy dane według daty
        pd.to_datetime(dane_wykres["Data"]) >= data_poczatkowa                                  # pozostawiamy wybrany okres
    ]

    return dane_wykres                                                                          # zwracamy przefiltrowane dane


#------------------------------------------------------------------------------------------------------------------------------------------
# WYKRES
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_wykres_ceny(dane_wykres, wybor_wskaznika, wybor_okresu, wybor_wykresu):               # funkcja wyświetlania wykresu

    if dane_wykres.empty:                                                                       # sprawdzamy, czy tabela jest pusta
        st.info("Brak danych dla wybranego okresu.")                                            # wyświetlamy informację
        return                                                                                  # kończymy działanie funkcji

    if wybor_wykresu == "Liniowy":                                                              # sprawdzamy rodzaj wykresu
        fig = px.line(                                                                          # tworzymy wykres liniowy
            dane_wykres,                                                                        # źródło danych
            x="Data",                                                                           # oś pozioma
            y=wybor_wskaznika,                                                                  # oś pionowa
            color="Symbol giełdowy",                                                            # osobny kolor dla spółki
            title=f"{wybor_wskaznika} — {wybor_okresu} dni"                                     # tytuł wykresu
        )

    else:                                                                                       # gdy wybrano wykres słupkowy
        fig = px.bar(                                                                           # tworzymy wykres słupkowy
            dane_wykres,                                                                        # źródło danych
            x="Data",                                                                           # oś pozioma
            y=wybor_wskaznika,                                                                  # oś pionowa
            color="Symbol giełdowy",                                                            # osobny kolor dla spółki
            title=f"{wybor_wskaznika} — {wybor_okresu} dni",                                    # tytuł wykresu
            barmode="group"                                                                     # słupki obok siebie
        )

    st.plotly_chart(fig, width="stretch")                                                       # wyświetlamy gotowy wykres


#------------------------------------------------------------------------------------------------------------------------------------------
# PODSUMOWANIE CEN AKCJI
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_podsumowanie(dane_wykres, wybor_spolki):                                              # funkcja podsumowania

    for spolka in wybor_spolki:                                                                 # analizujemy każdą wybraną spółkę

        dane_podsumowanie = dane_wykres[                                                         # wybieramy dane konkretnej spółki
            dane_wykres["Symbol giełdowy"] == spolka
        ].sort_values("Data")                                                                   # sortujemy chronologicznie

        if dane_podsumowanie.empty:                                                              # pomijamy spółkę bez danych
            continue

        cena_minimalna = dane_podsumowanie["Cena zamknięcia"].min()                              # najniższa cena
        cena_maksymalna = dane_podsumowanie["Cena zamknięcia"].max()                             # najwyższa cena
        cena_ostatnia = dane_podsumowanie["Cena zamknięcia"].iloc[-1]                            # ostatnia cena
        cena_pierwsza = dane_podsumowanie["Cena zamknięcia"].iloc[0]                             # pierwsza cena
        zmiana_dzienna = dane_podsumowanie["Zmiana dzienna (%)"].iloc[-1]                        # ostatnia zmiana

        zmiana_okres = (                                                                         # obliczamy zmianę w okresie
            (cena_ostatnia - cena_pierwsza) / cena_pierwsza
        ) * 100

        kolor_dzien = "green" if zmiana_dzienna >= 0 else "red"                                  # kolor zmiany dziennej
        kolor_okres = "green" if zmiana_okres >= 0 else "red"                                    # kolor zmiany okresowej

        st.subheader(                                                                           # pokazujemy nazwę spółki
            f"{spolka} — {nazwy_spolek.get(spolka, spolka)}"
        )

        kol1, kol2, kol3, kol4, kol5 = st.columns(5)                                            # tworzymy pięć kolumn

        kol1.markdown("**Min. cena zamknięcia**")                                               # nazwa pierwszej wartości
        kol1.markdown(f"#### {cena_minimalna:.2f} USD")                                         # minimalna cena

        kol2.markdown("**Maks. cena zamknięcia**")                                              # nazwa drugiej wartości
        kol2.markdown(f"#### {cena_maksymalna:.2f} USD")                                        # maksymalna cena

        kol3.markdown("**Ostatnia cena zamknięcia**")                                           # nazwa trzeciej wartości
        kol3.markdown(f"#### {cena_ostatnia:.2f} USD")                                          # ostatnia cena

        kol4.markdown("**Zmiana w okresie**")                                                   # nazwa czwartej wartości
        kol4.markdown(f"#### :{kolor_okres}[{zmiana_okres:+.2f}%]")                             # zmiana procentowa w okresie

        kol5.markdown("**Zmiana dzienna**")                                                     # nazwa piątej wartości
        kol5.markdown(f"#### :{kolor_dzien}[{zmiana_dzienna:+.2f}%]")                           # zmiana procentowa dzienna


#------------------------------------------------------------------------------------------------------------------------------------------
# TABELA DANYCH SPÓŁEK
#------------------------------------------------------------------------------------------------------------------------------------------

def pokaz_tabele_spolek(dane_wykres):                                                           # funkcja wyświetlania tabeli
    st.dataframe(dane_wykres, width="stretch")                                                  # pokazujemy wybrane spółki i okres z suwaka


# =========================================================================================================================================
# K R O K  4 :  U C Z E N I E  M A S Z Y N O W E
# =========================================================================================================================================

# Na razie pozostawiamy ten krok pusty.


# =========================================================================================================================================
# K R O K  5 :  U K Ł A D  D A S H B O A R D U
# =========================================================================================================================================

def pokaz_dashboard():                                                                          # funkcja układająca dashboard

    st.markdown(                                                                                # wyświetlamy tytuł dashboardu
        "<h1 style='text-align: center; font-size: 40px; width: 100%;'>Panel analizy akcji</h1>", # ustawiamy środek i rozmiar
        unsafe_allow_html=True                                                                  # pozwalamy na użycie HTML i CSS
    )

    kol1, kol2 = st.columns([1, 3])                                                             # tworzymy wąską i szeroką kolumnę

    with kol1:                                                                                  # elementy lewej kolumny
        wybor_spolki = pokaz_wybor_spolki()                                                      # wyświetlamy wybór spółek
        wybor_wskaznika = pokaz_wybor_wskaznika()                                                # wyświetlamy wybór wskaźnika
        wybor_okresu = pokaz_wybor_okresu()                                                      # wyświetlamy suwak okresu
        wybor_wykresu = pokaz_wybor_wykresu()                                                    # wyświetlamy wybór wykresu

    with kol2:                                                                                  # elementy prawej kolumny

        if wybor_spolki:                                                                        # sprawdzamy, czy wybrano spółkę

            dane_wykres = przygotuj_dane_wykres(                                                 # przygotowujemy dane dla spółek i okresu
                wybor_spolki, wybor_okresu
            )

            pokaz_wykres_ceny(                                                                   # wyświetlamy wykres
                dane_wykres,
                wybor_wskaznika,
                wybor_okresu,
                wybor_wykresu
            )

        else:                                                                                   # gdy nie wybrano żadnej spółki
            st.warning("Wybierz przynajmniej jedną spółkę.")                                    # pokazujemy komunikat

    if wybor_spolki:                                                                            # jeśli wybrano spółki
        pokaz_podsumowanie(dane_wykres, wybor_spolki)                                            # pokazujemy podsumowanie

        st.subheader("Tabela danych spółek")                                                     # wyświetlamy nagłówek tabeli
        pokaz_tabele_spolek(dane_wykres)                                                         # pokazujemy spółki i okres z suwaka

    st.markdown(                                                                                # dodajemy podpis autora
        """
        <div style="
            position: fixed;
            bottom: 10px;
            right: 20px;
            font-size: 13px;
            color: gray;
            z-index: 999;
        ">
            Autor: Grzegorz Żuchowski
        </div>
        """,
        unsafe_allow_html=True                                                                  # pozwalamy użyć HTML i CSS
    )


pokaz_dashboard()                                                                               # uruchamiamy nasz dashboard
