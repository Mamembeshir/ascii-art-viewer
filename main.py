import requests
from html.parser import HTMLParser
import argparse

class GoogleDocParser(HTMLParser):
    
    def __init__(self):
        super().__init__()
        self.in_table = False   
        self.in_td = False 
        self.current_row = []   
        self.rows = []    
        self.current_data = ''  

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.current_row = []
        
        elif tag == 'td' and self.in_table:
            self.in_td = True
            self.current_data = ''

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_table:
            self.in_td = False
            self.current_row.append(self.current_data.strip())
        elif tag == 'tr' and self.in_table:
            if self.current_row:
                self.rows.append(self.current_row)
        
        elif tag == 'table':
            self.in_table = False

    def handle_data(self, data):
        if self.in_td:
            self.current_data += data


def fetch_and_parse(url):
    response = requests.get(url)
    response.raise_for_status()  
    parser = GoogleDocParser()
    parser.feed(response.text)
    return parser.rows

def render_ascii(rows):
    coords = []

    for row in rows[1:]:
        if len(row) >= 3:
            try:
                x = int(row[0])
                char = row[1] or " "  
                y = int(row[2])
                coords.append((x, y, char))
            except ValueError:
                pass 

    if not coords:
        print("No valid coordinates found.")
        return

    max_x = max(x for x, y, _ in coords)
    max_y = max(y for x, y, _ in coords)
    grid = [[" " for _ in range(max_x + 1)] for _ in range(max_y + 1)]

    for x, y, char in coords:
        grid[y][x] = char

    # Invert the Y-axis 
    grid.reverse()

    for row in grid:
        print("".join(row))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ASCII Art Viewer from Google Docs")
    parser.add_argument("--url", required=True, help="Published Google Docs URL")
    args = parser.parse_args()

    print("Fetching data...")
    rows = fetch_and_parse(args.url)
    print("\nRendering ASCII art:\n")
    render_ascii(rows)
