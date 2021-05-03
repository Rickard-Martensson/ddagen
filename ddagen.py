# author: Rickard Mårtensson (rmarte@kth.se) 2021

"""
    ____        ____                                             _ __     __        _       __ 
   / __ \      / __ \____ _____ ____  ____     ____ ___  ___    (_/ /____/ /_______(_)___  / /_
  / / / /_____/ / / / __ `/ __ `/ _ \/ __ \   / __ `__ \/ _ \  / / / ___/ //_/ ___/ / __ \/ __/
 / /_/ /_____/ /_/ / /_/ / /_/ /  __/ / / /  / / / / / /  __/ / / (__  ) ,< / /  / / /_/ / /_  
/_____/     /_____/\__,_/\__, /\___/_/ /_/  /_/ /_/ /_/\___/_/ /_/____/_/|_/_/  /_/ .___/\__/  
                        /____/                            /___/                  /_/           


ett program som tar in en lista med epostadresser och mejlmallar
och skickar iväg rätt mejl till rätt person

var noga med att kolla igenom alla configfiler osv, annars kan det bli knas
jag har 0 ansvar bram, livet är ditt ostron

jag är mellanstadiedisco på tjack!

========================Instruktioner=======================

1. Installera en chromedriver, och länka till den i 'PATH'-variabeln nere i inställnigar
2. Skriv in ditt eget namn i 'NAMN'- variablen
3. Skriv in användarnamn och lösenord till ditt ddagen-konto.
Kan va en idé att stänga av tvåfaktorautkorisering också
4. Kopiera in de eposter du vill skicka till i 'matris' filen
5. Kör programmet:
    a. först kan du behöva svara på hurvida vissa företag ska ha en svensk eller engelsk mejlmall,
    om du inte redan stängt av det
    b. sedan kommer ett fönster öppnas. du behöver inte klicka någonstans
    c. låt programmer köra bram


========================Bra att veta========================
'SÄKERT_LÄGE' innebär att man måste trycka send manuellt.
Rekomenderar att ha på det, kan bli strul annars


Ibland kommer det upp ett fel:
'Failed to read descriptor from node 
connection: En enhet som õr ansluten till datorn fungerar inte. (0x1F)'
Det gör ingenting.

"""
from typing import Type
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


"""
========================Inställningar======================
path: path till chromedrivern, (tex "C:\Program Files\Selenium\chromedriver.exe")
namn: namn på dig att skriva i mejlen, (tex Rickard Mårtensson")

epost: din epostadress (tex rickard@ddagen.se)
lösen: ditt lösenord (tex password1234)

säkert_läge: Hurvida programmet ska skicka mejlen, eller vänta på att användaren trycker enter. (True/False)
default_svenska_företag: hurvida vi ska anta att ett företag är svenskt om inget annat uppges (True/False)

mejlmall_vanlig: path till mejlmall för nya företag (tex "mm_startup_ny")
mejlmall_återkommande: path till mejlmall för företag som var tillfrågade 2020 (tex "mm_startup_ater")
mejlmall_engelska: gör en kvalificerad gissning (tex "mm_startup_ny")
"""

PATH = "C:\Program Files\Selenium\chromedriver.exe"
NAMN = "Rickard Mårtensson"
EPOST = "rickard@ddagen.se"
LOSEN = "MannenJagKommerInteSkrivaMittLösenHärÄrDuSkönEller"
SAKERT_LAGE = False
DEFAULT_SVENSKA_FORETAG = True

MM_NY = "mm_startup_ny"
MM_ATERKOMMANDE = "mm_startup_ater"
MM_ENGELSK = "mm_startup_ny"

"""
========================Globala Variabler==================
(RÖR INTE!!)
"""
LANK = "https://mail.google.com/mail/u/3/?pli=1#inbox?compose=new"
T_KORT = 0.2
T_MED = 0.8
T_LANG = 3.0


def logga_in():
    pass


def skicka_mejl(driver, namn, titel, text, epost):
    """
    skickar mejl
    """
    driver.get(LANK)
    time.sleep(T_LANG)

    mottagar_fält = driver.find_element_by_name("to")
    mottagar_fält.send_keys(epost)

    time.sleep(T_KORT)

    titel_fält = driver.find_element_by_name("subjectbox")
    titel_fält.send_keys(titel)

    time.sleep(T_KORT)

    titel_fält.send_keys(Keys.TAB)
    time.sleep(T_KORT)
    aktivt_element = driver.switch_to.active_element
    time.sleep(T_KORT)
    aktivt_element.send_keys(text)

    time.sleep(T_LANG)
    if SAKERT_LAGE:
        input("klicka på 'skicka mejl' i fönstret som öppnats. när du är klar kan du trycka enter här:")
    else:
        aktivt_element.send_keys(Keys.CONTROL, Keys.ENTER)

    print("mejlade", namn, " " * max(1, 15 - len(namn)), "via", epost)

    with open("kontaktade_företag", "a", encoding="utf-8") as fixade_företag:
        fixade_företag.write(namn)
        fixade_företag.write("\n")
    time.sleep(T_KORT)
    pass


def main():
    global driver

    matris = läs_matris()

    driver = webdriver.Chrome(PATH)
    driver.get(LANK)
    time.sleep(T_KORT)
    email, lösen = "rickard@ddagen.se", "WtfGeMigEttLosenIgen"

    email_fält = driver.find_element_by_id("identifierId")
    email_fält.send_keys(email)
    email_fält.send_keys(Keys.ENTER)

    time.sleep(T_MED)

    lösen_fält = driver.find_element_by_name("password")
    lösen_fält.send_keys(lösen)
    lösen_fält.send_keys(Keys.ENTER)

    time.sleep(T_LANG)

    for företag in matris:
        namn = företag[0]
        epost = företag[2]
        titel, text = läs_mall(företag[1])
        skicka_mejl(driver, namn, titel, text, epost)

    print("Alla företag är kontaktade!")
    # skicka_mejl(driver)

    time.sleep(99999)


def läs_mall(mall_namn):
    """
    läser in en mejlmall från mejlmallar-mappen.

    det är väldigt viktigt att namnet står som [FÖRNAMN EFTERNAMN] eller [FIRSTNAME LASTNAME]
    samma sak gäller [SUBJECT: %titel%] eller [ÄMNE: %titel%]

    inga felstavningar! >:(

    kom ihåg att ta bort %signatur% i slutet om ni lägger till nya filer, det står så ibland

    """
    NAMN = "Rickard Mårtensson"
    mall_path = "mejlmallar\\"
    mall_path += mall_namn
    f = open("mejlmallar\mm_startup_ny", "r", encoding="utf-8")
    ofixad_text = f.read()

    splittad_text = ofixad_text.split("\n", 2)

    titel = splittad_text[0].replace("[ÄMNE: ", "").replace("[SUBJECT: ", "").replace("]", "")
    textmassa = splittad_text[2].replace("[FÖRNAMN EFTERNAMN]", NAMN).replace("[FIRSTNAME LASTNAME]", NAMN)

    return titel, textmassa


def läs_matris():
    """
    läser in data som användaren kopierat in i matris- filen

    returnerar namn, epost och hurvida vi kontaktade företaget 2020.
    sistnämnda är för om vi ska använda nya eller återkommande mejlmallen.

    kopiera så pass mycket så att både namnet kommer med, och åt minstonde mailadressen till kontaktperson 1.
    du kan såklart kopiera in mer.

    throwar en exception om det inte finns någon epost.
    Kommer välja att kontakta den sista epostadressen

    skriver ut de företag som blivit kontaktade till filen 'kontaktade_företag'.
    Kollar den varje gång innan programmet körs så att man inte råkar skicka dubbla mejl.

    kollar också hurvida företaget verkar vara svenskt eller engelskt,
    alltså vilken mejlmall som skall användas. Tester går till som följande:
    1. Om det står 'ja' eller 'Ja' på raden engelska, alltså på kolonn 24 (bokstav Z), så är företaget engelskt
    2. Om det står 'nej' eller 'Nej' på raden engelska, alltså på kolonn 24 (bokstav Z) så är företaget svenskt
    3. Slutar epostdomänen på .se så är företaget svenskt.
    4. Innehåller kontaktpersonens namn, alltså namnet på kolonn 25 (bokstan AA), å,ä,ö så är företaget svenskt.
    5. Om inga av föregående krav är uppfyllda så frågar programmet. Svara 'sv' eller 'en'
    """
    utdata = []
    f = open("matris", "r", encoding="utf-8")
    rad = 0
    for line in f:

        splittad_lista = line.split("\t")
        # print(splittad_lista)
        namn = splittad_lista[0]
        # kontaktad = "Kontaktad" in splittad_lista or "Ja" in splittad_lista or "ja" in splittad_lista
        kontaktad = any(svar in splittad_lista[5] for svar in ["Ja", "ja", "Kontaktad"])
        kontaktperson = splittad_lista[25]
        epost = "knas"
        språk = ""
        mall = ""

        for i in splittad_lista:
            if "@" in i:
                epost = i.strip()

        with open("kontaktade_företag", "r", encoding="utf-8") as fixade_företag:
            fixade_företag_lista = fixade_företag.readlines()
            # print(fixade_företag_lista)
            # print(namn, fixade_företag_lista)
            if namn + "\n" in fixade_företag_lista:
                print(namn, " " * max(1, 15 - len(namn)), "är redan kontaktade!")
                continue

        if splittad_lista[24] == "Ja" or splittad_lista[24] == "ja":
            språk = "en"
        elif splittad_lista[24] == "Nej" or splittad_lista[24] == "nej":
            språk = "sv"
        elif epost.endswith(".se"):
            språk = "sv"
        elif any(bokstav in kontaktperson for bokstav in ["å", "ä", "ö"]):
            språk = "sv"
        else:
            if DEFAULT_SVENSKA_FORETAG:
                språk = "sv"
            else:
                while True:
                    språk = input(
                        "är företaget: " + namn + " med kontaktperson: " + kontaktperson + " och epost: " + epost + " svenskt eller engeslkt? svara 'sv'/'en':"
                    )
                    if språk == "sv":
                        break
                    elif språk == "en":
                        break
                    else:
                        print("du skrev inte 'sv' eller 'en', utan", språk, "försök igen.")

        if språk == "en":
            mall = MM_ENGELSK
        elif kontaktad:
            mall = MM_ATERKOMMANDE
        else:
            mall = MM_NY
        if epost == "knas":
            raise TypeError("tyvärr, hittade ingen epost till", namn, "på rad", rad, "\nInga mejl har skickats")

        # print(splittad_lista)
        print(namn, " " * max(1, 15 - len(namn)), "kontaktad:", kontaktad, " " * max(1, 10 - len(str(kontaktad))), epost)

        rad += 1
        utdata.append([namn, mall, epost])

    print(utdata)
    return utdata


main()