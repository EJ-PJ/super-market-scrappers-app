import json
import unicodedata
from pathlib import Path

POSTAL_CODE_FILE = Path(__file__).parent / "postal_code.json"


def _normalize(text: str) -> str: # Lowercase and remove accents so "Sacatepéquez" matches "sacatepequez"
    text = unicodedata.normalize("NFD", text.strip())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.casefold()


def _get_key(data: dict, name: str):
    normalized_name = _normalize(name)
    for key in data:
        if _normalize(key) == normalized_name:
            return key
    return None


class PostalCode():

    # Constructor
    def __init__(self):
        self.deparment : str = ""
        self.municipality : str = ""
        self.postal_code : str = ""

    def find_postal_code(self, department: str, municipality: str, area: str | None = None) -> str | None:
        with open(POSTAL_CODE_FILE, encoding="utf-8") as file:
            postal_codes = json.load(file)

        department_key = _get_key(postal_codes, department)
        if department_key is None:
            return None

        municipalities = postal_codes[department_key]
        municipality_key = _get_key(municipalities, municipality)
        if municipality_key is None:
            return None

        result = municipalities[municipality_key]

        # Municipalities split by zones (Guatemala, Mixco, Villa Nueva) are nested dicts.
        # Only Villa Nueva has a code for the whole municipality, stored under its own name.
        if isinstance(result, dict):
            result_key = _get_key(result, area if area is not None else municipality)
            if result_key is None:
                return None
            result = result[result_key]

        self.deparment = department_key
        self.municipality = municipality_key
        self.postal_code = result

        return result

""" 
def main():
    postal_code = PostalCode()
    exit = True

    while exit:
        deparment = input("Ingresa Departamento: ")
        municipio = input("Ingresa Municipio: ")
        area = input("Ingresa Area (Zona 1, o Zona 2, Zona 15, etc) (Opcional): ")

        print("postal_code: ", postal_code.find_postal_code(deparment, municipio, area))

        print("Department: ", postal_code.deparment)
        print("Municipality: ", postal_code.municipality)
        print("Postal Code: ", postal_code.postal_code)

main()
"""
