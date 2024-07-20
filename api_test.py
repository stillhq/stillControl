import requests
import json

def query_gnome_extensions(query, page=1, n_per_page=10):
    url = "https://extensions.gnome.org/extension-query/"
    params = {
        "n_per_page": n_per_page,
        "sort": "updated",  # or "downloads" or "updated
        "page": 1,
        "search": query,
        # "shell_version": "46.2"  # replace with your GNOME shell version
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Request failed with status code {response.status_code}")
        return None



# Usage
extensions = query_gnome_extensions("t")
if extensions is not None:
    print(extensions)