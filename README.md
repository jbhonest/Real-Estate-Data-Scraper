# Real Estate Data Scraper

This Python script scrapes real estate data from Homegate.ch based on user-specified city, type (buy or rent), and maximum price. The extracted data includes information on the number of rooms, space (square meter), price, address, and title of the listings. The script also generates plots to visualize the relationship between space and price, as well as the distribution of prices based on the number of rooms.

## Table of Contents

- [Real Estate Data Scraper](#real-estate-data-scraper)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Configuration](#configuration)
  - [Usage](#usage)

## Description

The script utilizes BeautifulSoup for web scraping and pandas for data manipulation. It iterates through the pages of Homegate.ch matching listings for the specified city, type, and maximum price, extracting relevant details and storing them in a database. Additionally, the script generates plots using matplotlib and seaborn to visualize key aspects of the data.

## Features

- Scrapes real estate data from Homegate.ch
- Supports both buying and renting options
- Stores extracted data in a database
- Generates plots to visualize data relationships

## Prerequisites
Make sure you have the following libraries installed:
- requests
- beautifulsoup4 
- pandas
- matplotlib
- seaborn
- peewee
- psycopg2



You can install them using:

```bash
pip install requests beautifulsoup4 pandas matplotlib seaborn peewee psycopg2
```

## Configuration
Make sure to configure your local settings by creating a local_settings.py file with the required database details.
```bash
# local_settings.py

DATABASE = {
    'database_name': 'your_database_name',
    'user': 'your_database_user',
    'password': 'your_database_password',
    'host': 'your_database_host',
    'port': 'your_database_port',
}
```


## Usage

Run the script from the command line, providing the required arguments:

```bash
python main.py -c CITY -t TYPE -p MAX_PRICE
```
---
Developed by Jamal Badiee (jbhonest@yahoo.com)

