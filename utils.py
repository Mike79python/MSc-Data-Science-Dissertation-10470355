from bs4 import BeautifulSoup
import requests


def process_name(name: str):
    name = name.lower()
    name = (
        name.replace(" ", "-")
        .replace("'", "")
        .replace("nyck-de-vries", "nick-de-vries")
        .replace("kimi-räikkönen", "kimi-raikkonen")
        .replace("zhou-guanyu", "guanyu-zhou")
        .replace("--", "-")
    )
    return name


def get_names_from_table(html):
    soup = BeautifulSoup(html, "html.parser")

    table = None
    tables = soup.find_all("table")

    for t in tables:
        # Check the structure or other identifying elements of the table
        # For example, check if the table has at least 4 columns
        if len(t.find_all("th")) >= 4 or len(t.find_all("td")) >= 4:
            table = t
            break

    if table is None:
        raise ValueError("Table not found in HTML.")

    names_list = []
    rows = table.find_all("tr")

    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 2:
            name = columns[2].text.strip()
            name_parts = name.split("\n")
            name_parts = name_parts[:-1]
            name = " ".join(name_parts)
            names_list.append(name)

    return names_list


def get_all_player_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    div_element = soup.find("div", id="main")
    if div_element:
        all_links = div_element.find_all("a")
        link_urls = [link["href"] for link in all_links]
        return set(link_urls)
    return None


def separate_formula1_driver_link(url):
    links = get_all_player_links(url)
    if links == None:
        return None
    for l in links:
        response = requests.get(l)
        current_url = response.url
        if current_url.__contains__("formula1"):
            return current_url


def get_yearly_salaries(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "earningstable"})
        tbody = table.find("tbody")
        data = []
        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                year = cells[0].text.strip()
                salary = cells[1].text.strip()
                salary = salary.splitlines()[0].replace("$", "").replace(",", "")
                if (
                    year and salary and not year.startswith("Est.")
                ):  # Exclude rows with empty year or salary, and cumulative earnings row
                    data.append((year, int(salary)))
        yearly_salaries = {year: salary for year, salary in data}
        return yearly_salaries
    except Exception:
        return None
