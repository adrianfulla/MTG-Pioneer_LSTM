import requests
import time
from bs4 import BeautifulSoup
import json
from datetime import datetime

# URL base para el torneo Pioneer Challenge
url_base = "https://www.mtggoldfish.com"
search_url_template = "https://www.mtggoldfish.com/tournament_searches/create?commit=Search&page={}&tournament_search%5Bdate_range%5D=01%2F01%2F2021+-+10%2F29%2F2024&tournament_search%5Bformat%5D=pioneer&tournament_search%5Bname%5D=Challenge&utf8=%E2%9C%93"

# Mapeo de colores para extraer nombres de colores desde 'aria-label'
color_map = {
    "white": "white",
    "blue": "blue",
    "black": "black",
    "red": "red",
    "green": "green"
}

def get_tournament_links(page_num):
    search_url = search_url_template.format(page_num)
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Extrae todos los enlaces de los torneos en la página de búsqueda
    return [url_base + a["href"] for a in soup.select("a[href*='/tournament/']")], bool(soup.select_one("a[rel='next']"))


def get_color_names_from_icons(icons):
    colors = []
    for icon in icons:
        aria_label = icon.get("aria-label", "")
        for color, name in color_map.items():
            if color in aria_label:
                colors.append(name)
    return colors

def extract_tournament_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    try:
        # Localiza el bloque <main> y luego extrae el título y la fecha del torneo
        main_content = soup.find("main")
        title = main_content.find("h2").text.strip()
        date_str = main_content.find("p").find_next("br").next_sibling.strip().split('Date: ')[1]
        date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        print(f"Error at main for link: {url}")    
    # Formatear la fecha en caso de que sea necesario
    
    try:
    # Lista para guardar posiciones
        positions = []

        # Extrae cada fila de la tabla
        table_content = soup.find("table").find_all("tr", class_=["tournament-decklist-odd", "tournament-decklist-event"])
        rows = table_content
        for row in rows:
            place = row.select_one("td.text-right").text.strip()
            deck_name = row.select_one("a").text.strip()
            
            # Extrae los colores
            color_icons = row.select("span.manacost")
            colors = get_color_names_from_icons(color_icons)
            
            positions.append({
                "place": place,
                "name": deck_name,
                "colors": colors
            })
    except:
        print(f"Error at table for link {url}")
        return None

    # Estructura del torneo
    tournament_data = {
        "name": title,
        "date": date,
        "positions": positions
    }
    # print(tournament_data)
    return tournament_data

def main():
    page_num = 1
    all_tournaments = []
    
    while True:
        print(page_num)
        tournament_links, has_next_page = get_tournament_links(page_num)
    
        for link in tournament_links:
            tournament_data = extract_tournament_data(link)
            if tournament_data:
                all_tournaments.append(tournament_data)
            time.sleep(10)

        if not has_next_page:
            break
        
        page_num += 1
        time.sleep(10)
        
        
    # Guardar los datos en un archivo JSON
    with open("pioneer_challenges.json", "w") as f:
        json.dump(all_tournaments, f, indent=4)
    print("Datos guardados en pioneer_challenges.json")

if __name__ == "__main__":
    main()
