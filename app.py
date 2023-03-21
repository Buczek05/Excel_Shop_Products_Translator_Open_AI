import openai
import pandas as pd
import numpy as np
import math
from bs4 import BeautifulSoup
import time

#######################
OPEN_AI_ORGANIZATION_ID = ""
OPEN_AI_KEY = ""
DICT_LIBRARY = r""
EXCEL_FILE_PATH = r""
OUTPUT_EXEL_PATH = r""
TEST_EXCEL_COLUMNS_LEN = 0
TEST_EXCEL_ROWS_LEN = 0
TEST_EXCEL_FIRST_COL = 0
LANGUAGE = "English"
#######################
#######################
openai.organization = OPEN_AI_ORGANIZATION_ID
openai.api_key = OPEN_AI_KEY
#######################


def open_excel_to_numpy_list(excel_path: str = EXCEL_FILE_PATH) -> np:
    print("Opening Excel...")
    df = pd.read_excel(excel_path)
    numpy_list = df.to_numpy()
    print("Excel opened")
    return numpy_list


def save_excel_from_numpy_list(numpy_list: np) -> None:
    df = pd.DataFrame(numpy_list)
    df.to_excel(OUTPUT_EXEL_PATH, index=False)
    print("Excel saved to:", OUTPUT_EXEL_PATH)


def change_price_from_pln_to_euro(price: float) -> float:
    return math.ceil(price / 4 + 0.1) - 0.1


def get_list_from_html(html_code: str) -> list:
    soup = BeautifulSoup(html_code, "html.parser")
    text_list = soup.get_text().split("\n")
    cleared_text_list = []
    for text in text_list:
        if text not in [
            "",
            '"',
            " ",
            "\xa0",
        ] and any(char.isalnum() for char in text):
            try:
                float(text)
            except:
                text = text.replace('"', "")
                cleared_text_list.append(text)
    return cleared_text_list


def html_replace_code(html_code: str, my_dict: dict) -> str:
    text_list = get_list_from_html(html_code)
    for text in text_list:
        if " " == text[0]:
            text = text[1:]
        if " " == text[-1]:
            text = text[:-1]
        try:
            new_text = my_dict[text.replace("\xa0", " ").strip()]
            while "." in new_text:
                new_text = new_text.replace(".", ",")
            before_html_code = html_code
            html_code = html_code.replace(text, new_text)
            if before_html_code == html_code and not text.replace(",", "").isdigit():
                html_code = translate_text(html_code)
                print("Extra html translating")
                return html_code
        except:
            print("I don't find it in dictionary:", text)

    return html_code


def save_dict_to_file(my_dict: dict, path: str = DICT_LIBRARY) -> None:
    with open(path, "w", encoding="utf-8") as file:
        for key, value in my_dict.items():

            file.write(key.replace("\xa0", " ") + "\n")
            file.write(value + "\n")
    print("Saving the dictionary")


def read_dict_from_file(path: str = DICT_LIBRARY) -> dict:
    my_dict = {}
    with open(path, "r", encoding="utf-8") as file:
        read_lines = file.readlines()
        for i in range(0, len(read_lines), 2):
            if read_lines[i] != "":
                my_dict[read_lines[i].strip()] = read_lines[i + 1].strip()
    print("Reading the dictionary")
    return my_dict


def make_a_big_facking_dict(numpy_list: np) -> dict:
    big_facking_dict = {}
    print("Start making a big fucking dictionary")
    for row in numpy_list:
        if (
            type(row[0]) == str
            and any(char.isalnum() for char in row[0])
            and row[0] not in big_facking_dict.keys()
            and row[0] != "\ufeff"
        ):
            big_facking_dict[row[0]] = ""

    for row in numpy_list:
        for i in [1, 2, 5, 6, 8, 9, 10, 11, 12, 13]:
            if (
                i != 2
                and type(row[i]) == str
                and any(char.isalnum() for char in row[i])
                and row[i] not in big_facking_dict.keys()
                and row[i] != "\ufeff"
            ):
                big_facking_dict[row[i]] = ""
            elif type(row[i]) == str:
                for text in get_list_from_html(row[i]):
                    if text not in big_facking_dict.keys():
                        big_facking_dict[text] = ""
    return big_facking_dict


def translate_text(text: str) -> str:
    i = 0
    while i < 5:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": f"""Translate it to {LANGUAGE}, don't change text format, every question are split by "\n\n" If in text not are '-', don't add it. Take into account the order of input, preserve it, and return the data in the same order. """,
                    },
                    {
                        "role": "user",
                        "content": """elegancki-damski-zegarek-na-bransolecie-z-kolorowa-tarcza

Elegancki damski zegarek na bransolecie

Dostępny w trzech wariantach kolorystycznych: zielony, czarny, brązowy

Cechy produktu

Okrągła tarcza

Złoto-biały""",
                    },
                    {
                        "role": "assistant",
                        "content": """elegant-ladies-watch-on-a-bracelet-with-a-colorful-dial

Elegant ladies watch on a bracelet

Available in three color variations: green, black, brown

Product features

Round dial

Golded-white""",
                    },
                    {"role": "user", "content": text},
                ],
            )
            break
        except:
            i += 1
            print("Error with translating")
    ready_text = response["choices"][0]["message"]["content"]
    return ready_text


def translate_dict(my_dict: dict, items_per_question: int = 50) -> dict:
    non_clear_dict = {}
    for key, value in my_dict.items():
        if len(key) < 2:
            my_dict[key] = key
            continue
        if value == "" and key != "":
            non_clear_dict[key] = ""
    len_dict = len(non_clear_dict.keys())
    print("Dictionary length:", len_dict)
    for i in range(0, len(non_clear_dict.keys()), items_per_question):
        text_list = []
        a = 0
        if i < len_dict - items_per_question:
            list_of_text = list(non_clear_dict.keys())[i : i + items_per_question]
        else:
            list_of_text = list(non_clear_dict.keys())[i:]
        if len(list_of_text) > 1:
            text = "\n\n".join(list_of_text)
        else:
            text = list_of_text[0]
        while len(text_list) != len(list_of_text) and a < 2:
            text_list = translate_text(text)
            if len(list_of_text) > 1:
                text_list = text_list.split("\n\n")
            else:
                text_list = [text_list]
            print(f"List size: {len(text_list)}, that should be {len(list_of_text)}")
            a += 1
        if a < 2:
            for j, text in enumerate(text_list):
                non_clear_dict[list(non_clear_dict.keys())[i + j]] = text

        print("Translating...", str(round((i / len_dict) * 100, 2)) + "%")
        time.sleep(3)  # OpenAI have limit for 20 question per 1 minut
        for key, value in my_dict.items():
            if value == "" and key != "":
                my_dict[key] = non_clear_dict[key]
        save_dict_to_file(my_dict)
    return my_dict


def prepare_link(text: str) -> str:
    while " - " in text:
        text = text.replace(" - ", "-")
    while "'s" in text:
        text = text.replace("'s", "")
    while "." in text:
        text = text.replace(".", "")
    while " " in text:
        text = text.replace(" ", "-")
    return text


def fill_list(numpy_list: np, my_dict: dict) -> np:
    print("Start filling the numpy list")
    for j in range(0, len(numpy_list)):
        for i in [19, 20]:
            if (
                type(numpy_list[j][i]) == float
                and not np.isnan(numpy_list[j][i])
                and numpy_list[j][i]
            ):
                numpy_list[j][i] = change_price_from_pln_to_euro(
                    float(numpy_list[j][i])
                )
        for i in [0, 1, 2, 5, 6, 8, 9, 10, 11, 12, 13]:
            try:
                if i not in (0, 2) and type(numpy_list[j][i]) == str:
                    numpy_list[j][i] = my_dict[numpy_list[j][i]]
                elif i == 0:
                    my_dict[numpy_list[j][i]] = prepare_link(my_dict[numpy_list[j][i]])
                    numpy_list[j][i] = my_dict[numpy_list[j][i]]
            except:
                print("I don't find it in dictionary:", numpy_list[j][i])
            if i == 2 and type(numpy_list[j][i]) == str:
                numpy_list[j][i] = html_replace_code(numpy_list[j][i], my_dict)
    return numpy_list


def main() -> None:
    numpy_list = open_excel_to_numpy_list()
    my_dict = make_a_big_facking_dict(numpy_list)
    save_dict_to_file(my_dict)
    my_dict = translate_dict(my_dict, 10)
    my_dict = translate_dict(my_dict, 5)
    my_dict = translate_dict(my_dict, 1)
    save_dict_to_file(my_dict)
    ready_excel = fill_list(numpy_list, my_dict)
    save_excel_from_numpy_list(ready_excel)


#######################
class TestClass:
    def test_connect_to_ai(self) -> None:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Just do it."},
                {"role": "user", "content": "Write 'OK'"},
            ],
        )
        assert "OK" in response["choices"][0]["message"]["content"]

    def test_open_exel_to_numpy_list(self) -> None:
        x = open_excel_to_numpy_list()

        assert (
            len(x) == TEST_EXCEL_COLUMNS_LEN
            and len(x[0]) == TEST_EXCEL_ROWS_LEN
            and x[0][0] == TEST_EXCEL_FIRST_COL
        )

    def test_save_exel_from_numpy_list(self) -> None:
        numpy_list = np.array([["aaa", "aaa"], ["fwafaw", "fawfaw"]])
        save_excel_from_numpy_list(numpy_list)
        x = open_excel_to_numpy_list(OUTPUT_EXEL_PATH)
        assert len(numpy_list) == len(x)

    def test_change_price_from_pln_to_euro(self) -> None:
        list_of_test = [
            [79.0, 19.9],
            [39.9, 10.9],
            [55.12, 13.9],
            [15.6, 3.9],
            [15.64, 4.9],
        ]
        for test in list_of_test:
            assert change_price_from_pln_to_euro(test[0]) == test[1]

    def test_get_list_from_html_1(self) -> None:
        x = [
            "Cechy produktu",
            "Damski zegarek",
            "Okrągła tarcza ",
            "Minimalistyczny, elegancki design",
            "Bransoleta ze stali nierdzewnej",
            "Długość bransolety: 20 cm",
            "Średnica tarczy: 2,6 cm",
            "Materiał: stal",
            "Dostępny w trzech wariantach kolorystycznych: zielony, czarny, brązowy.",
        ]
        test_html = """"<h3 data-mce-fragment=""1"">Cechy produktu</h3>
<ul data-mce-fragment=""1"">
<li data-mce-fragment=""1"">Damski zegarek</li>
<li data-mce-fragment=""1"">Okrągła tarcza </li>
<li data-mce-fragment=""1"">Minimalistyczny, elegancki design</li>
<li data-mce-fragment=""1"">Bransoleta ze stali nierdzewnej</li>
<li data-mce-fragment=""1"">Długość bransolety: 20 cm<br data-mce-fragment=""1"">
</li>
<li data-mce-fragment=""1"">Średnica tarczy: 2,6 cm</li>
<li data-mce-fragment=""1"">Materiał: stal</li>
<li data-mce-fragment=""1"">Dostępny w trzech wariantach kolorystycznych: zielony, czarny, brązowy.</li>
</ul>"
    """
        for test_line, x_line in zip(get_list_from_html(test_html), x):
            assert test_line == x_line

    def test_get_list_from_html_2(self) -> None:
        x = [
            "Cechy produktu",
            "Damski zegarek",
            "Z okrągłą tarczą",
            "Minimalistyczny design",
            "Pasek z eko-skóry",
            "Zapięcie na sprzączkę",
            "Długość paska: 22 cm",
            "Materiał: stal",
            "Dostępny w trzech wariantach kolorystycznych: szary, czerwony i czarny",
        ]
        test_html = """""<h3>Cechy produktu</h3>
<ul>
<li>Damski zegarek</li>
<li>Z okrągłą tarczą</li>
<li>Minimalistyczny design</li>
<li>Pasek z eko-skóry</li>
<li>Zapięcie na sprzączkę</li>
<li>Długość paska: 22 cm</li>
<li>Materiał: stal</li>
<li>Dostępny w trzech wariantach kolorystycznych: szary, czerwony i czarny</li>
</ul>"
"""
        for test_line, x_line in zip(get_list_from_html(test_html), x):
            assert test_line == x_line

    def test_html_replace_code(self) -> None:
        ready_html = """<h3>Product features</h3>
<ul>
<li>Women's watch</li>
<li>With a round dial</li>
<li>Minimalistic design</li>
<li>Eco-leather strap</li>
<li>Buckle closure</li>
<li>Strap length: 22 cm</li>
<li>Material: steel</li>
<li>Available in three color variants: gray, red, and black</li>
</ul>
"""
        test_html = """<h3>Cechy produktu</h3>
<ul>
<li>Damski zegarek</li>
<li>Z okrągłą tarczą</li>
<li>Minimalistyczny design</li>
<li>Pasek z eko-skóry</li>
<li>Zapięcie na sprzączkę</li>
<li>Długość paska: 22 cm</li>
<li>Materiał: stal</li>
<li>Dostępny w trzech wariantach kolorystycznych: szary, czerwony i czarny</li>
</ul>
"""
        test_dict = {
            "Cechy produktu": "Product features",
            "Damski zegarek": "Women's watch",
            "Z okrągłą tarczą": "With a round dial",
            "Minimalistyczny design": "Minimalistic design",
            "Pasek z eko-skóry": "Eco-leather strap",
            "Zapięcie na sprzączkę": "Buckle closure",
            "Długość paska: 22 cm": "Strap length: 22 cm",
            "Materiał: stal": "Material: steel",
            "Dostępny w trzech wariantach kolorystycznych: szary, czerwony i czarny": "Available in three color variants: gray, red, and black",
        }
        assert html_replace_code(test_html, test_dict) == ready_html

    def test_saving_and_reading_dict(self) -> None:
        test_path = "test_dict_save.txt"
        my_test_dict = {"1": "a", "2": "faw", "412rfawfawf21": "4124124"}
        save_dict_to_file(my_test_dict, test_path)
        assert my_test_dict == read_dict_from_file(test_path)

    def test_make_a_big_facking_dict(self) -> None:
        clear_dict = {
            "elegancki-damski-zegarek-na-bransolecie-z-kolorowa-tarcza": "",
            "elegancki-damski-zegarek-na-bransolecie-1": "",
            "Elegancki damski zegarek na bransolecie z kolorową tarczą": "",
            "Elegancki damski zegarek na bransolecie": "",
            "Cechy produktu": "",
            "Damski zegarek": "",
            "Okrągła tarcza ": "",
            "Minimalistyczny, elegancki design": "",
            "Bransoleta ze stali nierdzewnej": "",
            "Długość bransolety: 20 cm": "",
            "Średnica tarczy: 2,6 cm": "",
            "Materiał: stal": "",
            "Dostępny w trzech wariantach kolorystycznych: zielony, czarny, brązowy.": "",
            "Zegarki": "",
            "Kolor": "",
            "Czarny": "",
            "Zielony": "",
            "Brązowy": "",
            "Srebrny": "",
            "Złoty": "",
            "Różowe złoto": "",
            "Długość bransolety: 22 cm": "",
            "Średnica tarczy: 3,8 cm": "",
            "Materiał: stal": "",
            "Dostępny w czterech wariantach kolorystycznych": "",
        }
        test_numpy_list = open_excel_to_numpy_list()[:10]
        assert make_a_big_facking_dict(test_numpy_list) == clear_dict

    def test_translate_text(self) -> None:
        x_text = "elegant-ladies-watch-on-a-bracelet-with-a-colorful-dial"
        test_text = "elegancki-damski-zegarek-na-bransolecie-z-kolorowa-tarcza"
        translate_text(test_text) == x_text

    def test_translate_dict(self) -> None:
        clear_dict = {
            "elegancki-damski-zegarek-na-bransolecie-z-kolorowa-tarcza": "",
            "elegancki-damski-zegarek-na-bransolecie-1": "",
            "Elegancki damski zegarek na bransolecie z kolorową tarczą": "",
            "Elegancki damski zegarek na bransolecie": "",
            "Cechy produktu": "",
            "Damski zegarek": "",
            "Okrągła tarcza ": "",
            "Minimalistyczny, elegancki design": "",
            "Bransoleta ze stali nierdzewnej": "",
            "Długość bransolety: 20 cm": "",
            "Średnica tarczy: 2,6 cm": "",
            "Materiał: stal": "",
            "Dostępny w trzech wariantach kolorystycznych: zielony, czarny, brązowy.": "",
            "Zegarki": "",
            "Kolor": "",
            "Czarny": "",
            "Zielony": "",
            "Brązowy": "",
            "Srebrny": "",
            "Złoty": "",
            "Różowe złoto": "",
            "Długość bransolety: 22 cm": "",
            "Średnica tarczy: 3,8 cm": "",
            "Materiał: stal": "",
            "Dostępny w czterech wariantach kolorystycznych": "",
        }
        for x in translate_dict(clear_dict):
            assert x

    def test_prepare_link(self) -> None:
        test_link = "asd - asd's-a aa."
        x_link = "asd-asd-a-aa"
        assert prepare_link(test_link) == x_link
