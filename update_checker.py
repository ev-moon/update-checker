"""Simple script that uses hashlib to check website updates."""
import hashlib
import os
import re

import requests
from bs4 import BeautifulSoup

DATA_DIRECTORY = "site_data"
SITE_LIST = "site_list.txt"


def compare_hash(url):
    """
    Uses hashlib to create a hash for html body content and
    compares it with the hash created by the old content.
    If the two hashes differ, returns True; otherwise returns False.
    """
    response = requests.get(url)
    body = BeautifulSoup(response.text, "html.parser").find("body")
    byte_conversion = body.encode("UTF-8")
    new_hash = hashlib.sha256(byte_conversion).hexdigest()
    domain_name = re.split("//|www.", url)[-1]
    file_name = (
        domain_name.replace(".", "_").replace("/", "_").replace("?", "_")[:-1] + ".dat"
    )
    check_data_directory()
    file_path = os.path.join(os.getcwd(), DATA_DIRECTORY, file_name)
    if not os.path.isfile(file_path):
        with open(file_path, "w"):
            pass
    with open(file_path, "r+") as site_data:
        old_hash = site_data.read()
        if new_hash != old_hash:
            site_data.seek(0)
            site_data.write(new_hash)
            site_data.truncate()
            return True  # site has been updated
    return False  # no updates


def print_message(updates):
    """
    Prints corresponding message according to the existence and number of updated urls.
    """
    if not updates:
        print("There are no updates.")
    else:
        print(
            "There has(have) been {} update(s). The sites updated are".format(
                len(updates)
            ),
            end="\n",
        )
        print(*updates, sep="\n", end="\n")


def check_data_directory():
    """Checks existence of data directory and creates if needed."""
    try:
        if not os.path.exists(DATA_DIRECTORY):
            os.makedirs(DATA_DIRECTORY)
    except OSError:
        print("Error creating site data directory.")


def main():
    """
    Main function that brings everything together.
    """
    print("Welcome to PyUpdateFinder.")
    url_file_path = os.path.join(os.getcwd(), SITE_LIST)
    if os.path.isfile(url_file_path):
        with open(url_file_path) as url_file:
            updates = list()
            line = url_file.readline()

            while line:
                print("Currently reading...", line)
                if compare_hash(line):
                    updates.append(line)
                line = url_file.readline()
            print_message(updates)
    while True:
        add_sites = input("Would you like to add any websites to monitor? (y/n) ")
        if add_sites == "y":
            with open(os.path.join(os.getcwd(), SITE_LIST), "a+") as site_list:
                new_sites = input(
                    'Add a site you would like to monitor.'
                    'You can also enter multiple sites, separated by a space.\n'
                    'Please enter the whole url, starting with http. e.g. http://www.google.com \n'
                ).split()
                for site in new_sites:
                    compare_hash(site)
                    site_list.write(site + "\n")
            return
        if add_sites == "n":
            return
        print("Please type your answer as y for yes, or n for no.")


if __name__ == "__main__":
    main()
