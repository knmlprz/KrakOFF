import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin, urlencode, urlparse
import urllib3
import calendar
import os # Do operacji na plikach i folderach
# import re # Może nie być potrzebny w tej wersji

# Wyłącz ostrzeżenia o żądaniach bez weryfikacji SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Konfiguracja ---
BASE_URL_KARNET = 'https://karnet.krakowculture.pl'
EVENTS_PATH_KARNET = '/wydarzenia'
IMAGE_DOWNLOAD_FOLDER = 'obrazy_wydarzen_karnet' # Nazwa folderu na obrazy

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
}

CSV_FILE_KARNET_YEAR = f'wydarzenia_karnet_krakow_z_obrazkami_{time.strftime("%Y%m%d-%H%M%S")}.csv'
YEAR_TO_SCRAPE = 2025
BATCH_SAVE_SIZE = 20

CSV_HEADERS = [
    'id_strony', 'tytul', 'typ_wydarzenia_lista', 'data_lista', 'lokalizacja_lista',
    'link_do_obrazka_lista', # Dodana kolumna na URL obrazka
    'sciezka_do_pobranego_obrazka' # Dodana kolumna na lokalną ścieżkę
]

def fetch_page_content(url, is_image=False):
    # print(f"Pobieranie {'obrazka' if is_image else 'strony'}: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=25, verify=False, allow_redirects=True, stream=is_image)
        
        if not is_image: 
            if response.apparent_encoding:
                response.encoding = response.apparent_encoding
            else:
                response.encoding = 'utf-8'

        if response.status_code == 404:
            print(f"Błąd 404: Zasób nie znaleziony pod adresem {response.url}.")
            return None
        response.raise_for_status()
        
        if is_image:
            return response # Zwracamy cały obiekt odpowiedzi dla obrazków
        else:
            return response.text # Zwracamy tekst dla stron HTML
            
    except requests.exceptions.HTTPError as http_err:
        print(f"Błąd HTTP: {http_err} dla URL: {url} (finalnie {http_err.response.url if http_err.response else url})")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Błąd (inny) podczas pobierania {url}: {e}")
        return None

def download_image(image_url, event_id, folder_path):
    if not image_url or not event_id:
        return None

    try:
        os.makedirs(folder_path, exist_ok=True)

        parsed_url = urlparse(image_url)
        path_parts = os.path.splitext(parsed_url.path)
        extension = path_parts[1] if path_parts[1] else '.jpg'

        filename = f"{event_id}{extension}"
        filepath = os.path.join(folder_path, filename)

        # Sprawdź, czy plik już istnieje, aby uniknąć ponownego pobierania
        if os.path.exists(filepath):
            return filepath

        response = fetch_page_content(image_url, is_image=True)
        if response and response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024): 
                    f.write(chunk)
            # print(f"Zapisano obrazek: {filepath}")
            return filepath
        else:
            print(f"Nie udało się pobrać obrazka z {image_url}. Status: {response.status_code if response else 'Brak odpowiedzi'}")
            return None
    except Exception as e:
        print(f"Błąd podczas pobierania lub zapisywania obrazka {image_url}: {e}")
        return None


def parse_karnet_pl_event_list(html_content, base_url_for_absolute_paths, current_page_url):
    if not html_content: return [], None
    soup = BeautifulSoup(html_content, 'html.parser')
    events_data = []
    event_containers = soup.find_all('div', class_='event-item')

    if not event_containers: return [], None
    
    for event_container in event_containers:
        event = {header: '' for header in CSV_HEADERS}
        
        event_link_tag_img = event_container.find('a', class_='event-image')
        event_link_tag_content = event_container.find('a', class_='event-content')
        
        image_tag = event_link_tag_img.find('img') if event_link_tag_img else None
        event['link_do_obrazka_lista'] = image_tag['src'] if image_tag and image_tag.has_attr('src') else ""

        if event['link_do_obrazka_lista'] and not event['link_do_obrazka_lista'].startswith(('http://', 'https://')):
            event['link_do_obrazka_lista'] = urljoin(base_url_for_absolute_paths, event['link_do_obrazka_lista'])
        
        content_anchor = event_link_tag_content if event_link_tag_content else event_container
        title_element = content_anchor.find('h3', class_='event-title')
        event['tytul'] = title_element.text.strip() if title_element else ""
        type_element = content_anchor.find('span', class_='event-type')
        event['typ_wydarzenia_lista'] = type_element.text.strip() if type_element else ""
        location_element = content_anchor.find('p', class_='event-location')
        
        if location_element:
            icon_span = location_element.find('span', class_='icon-location')
            if icon_span: icon_span.decompose()
            event['lokalizacja_lista'] = location_element.text.strip()

        event_controls_tag = event_container.find('div', class_='event-controls')
        date_element_link = event_controls_tag.find('a', class_='event-date') if event_controls_tag else None
        date_span = date_element_link.find('span') if date_element_link else None
        event['data_lista'] = date_span.text.strip() if date_span else ""
        
        event['id_strony'] = event_container.get('data-id', '')
        
        events_data.append(event)
    
    next_page_url = None
    pagination_div = soup.find('div', class_='pagination')
    if pagination_div:
        next_link_tag = pagination_div.find('a', class_='button next')
        if next_link_tag and next_link_tag.has_attr('href'):
            next_page_href = next_link_tag['href']
            if next_page_href and next_page_href != '#':
                next_page_url = urljoin(current_page_url, next_page_href)
    
    return events_data, next_page_url

def save_to_csv(data_list, filename, headers):
    if not data_list: return
    file_exists_and_not_empty = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8-sig') as f_check:
            if f_check.readline(): file_exists_and_not_empty = True
    except FileNotFoundError: file_exists_and_not_empty = False
    
    if not data_list: return
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8-sig') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=headers, quoting=csv.QUOTE_ALL)
            if not file_exists_and_not_empty:
                dict_writer.writeheader()
            for row_dict in data_list:
                full_row = {header: row_dict.get(header, '') for header in headers}
                dict_writer.writerow(full_row)
        # print(f"Dane ({len(data_list)} wierszy) dopisano do: {filename}")
    except IOError as e: print(f"Błąd zapisu CSV {filename}: {e}")
    except Exception as e: print(f"Inny błąd zapisu CSV: {e}")

def main_karnet_pl_yearly_scraper(year_to_scrape, start_month=1, end_month=12):
    print(f"Rozpoczynam scrapowanie (z obrazkami) roku {year_to_scrape} (miesiące: {start_month}-{end_month}) dla {BASE_URL_KARNET}{EVENTS_PATH_KARNET}")
    
    # Utwórz główny folder na obrazy, jeśli nie istnieje
    os.makedirs(IMAGE_DOWNLOAD_FOLDER, exist_ok=True)
    print(f"Obrazki będą zapisywane w folderze: ./{IMAGE_DOWNLOAD_FOLDER}/")

    try:
        with open(CSV_FILE_KARNET_YEAR, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, quoting=csv.QUOTE_ALL)
            writer.writeheader()
        print(f"Plik {CSV_FILE_KARNET_YEAR} został utworzony z nagłówkami.")
    except IOError:
        print(f"Nie można było utworzyć pliku {CSV_FILE_KARNET_YEAR}.")
        return

    total_events_processed_for_year = 0
    event_batch_to_save = []

    for month in range(start_month, end_month + 1):
        month_str = f"{month:02d}"
        date_start_str = f"{year_to_scrape}-{month_str}-01"
        num_days_in_month = calendar.monthrange(year_to_scrape, month)[1]
        date_end_str = f"{year_to_scrape}-{month_str}-{num_days_in_month:02d}"
        query_params = {
            'date_start': date_start_str, 'date_end': date_end_str,
            'query': '', 'choosenArea': '', 'radius': '1000', 'category_id': '',
            'order': '', 'latitude': '', 'longitude': '', 'location_name': ''
        }
        monthly_start_url = f"{BASE_URL_KARNET}{EVENTS_PATH_KARNET}?{urlencode(query_params)}"
        print(f"\n Rozpoczynam scrapowanie dla: {date_start_str} do {date_end_str}")
        current_page_url_for_month = monthly_start_url
        page_in_month_count = 0
        max_pages_per_month = 50 

        while current_page_url_for_month and page_in_month_count < max_pages_per_month:
            page_in_month_count += 1
            html_content = fetch_page_content(current_page_url_for_month)
            
            if html_content:
                extracted_event_summaries, next_page_url = parse_karnet_pl_event_list(html_content, BASE_URL_KARNET, current_page_url_for_month)
                
                if extracted_event_summaries:
                    print(f"  Znaleziono {len(extracted_event_summaries)} wydarzeń na str. {page_in_month_count} (miesiąc {month_str}).")
                    for event_summary in extracted_event_summaries:
                        image_url = event_summary.get('link_do_obrazka_lista')
                        event_id = event_summary.get('id_strony')
                        
                        if image_url and event_id:
                            print(f"    Próba pobrania obrazka dla id {event_id} z {image_url}")
                            saved_image_path = download_image(image_url, event_id, IMAGE_DOWNLOAD_FOLDER)
                            if saved_image_path:
                                event_summary['sciezka_do_pobranego_obrazka'] = saved_image_path
                                print(f"      Zapisano: {saved_image_path}")
                            time.sleep(0.3) # Małe opóźnienie między pobieraniem obrazków
                        
                        event_batch_to_save.append(event_summary)
                        total_events_processed_for_year +=1

                        if len(event_batch_to_save) >= BATCH_SAVE_SIZE:
                            save_to_csv(event_batch_to_save, CSV_FILE_KARNET_YEAR, CSV_HEADERS)
                            event_batch_to_save.clear()
                
                current_page_url_for_month = next_page_url
                if current_page_url_for_month: time.sleep(1.0) 
                else: break 
            else:
                if page_in_month_count == 1: print(f"Nie udało się pobrać strony startowej dla {date_start_str}-{date_end_str}")
                else: print(f"Nie udało się pobrać strony paginacji dla {date_start_str}-{date_end_str}")
                break
        
        if page_in_month_count >= max_pages_per_month:
            print(f"Osiągnięto limit {max_pages_per_month} stron dla {date_start_str}-{date_end_str}.")
        
        if event_batch_to_save:
            save_to_csv(event_batch_to_save, CSV_FILE_KARNET_YEAR, CSV_HEADERS)
            event_batch_to_save.clear()
            
        print(f"Zakończono {date_start_str}-{date_end_str}. Czekam 2 sekundy.")
        time.sleep(2)

    if event_batch_to_save:
        save_to_csv(event_batch_to_save, CSV_FILE_KARNET_YEAR, CSV_HEADERS)
        event_batch_to_save.clear()

    print(f"\nZakończono scrapowanie (z obrazkami) dla roku {year_to_scrape} (miesiące {start_month}-{end_month}).")
    if total_events_processed_for_year > 0:
        print(f"Całkowita liczba przetworzonych wydarzeń: {total_events_processed_for_year}")
    else:
        print(f"Nie zescrapowano żadnych wydarzeń dla roku {year_to_scrape}.")
    print(f"Dane CSV zapisano do: {CSV_FILE_KARNET_YEAR}")
    print(f"Obrazki powinny być zapisane w folderze: ./{IMAGE_DOWNLOAD_FOLDER}/")

if __name__ == '__main__':
    main_karnet_pl_yearly_scraper(year_to_scrape=2025, start_month=1, end_month=12) 