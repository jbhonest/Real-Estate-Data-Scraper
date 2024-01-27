import peewee
import local_settings
import re
import argparse
import requests
import warnings
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from bs4 import BeautifulSoup
from database_manager import DatabaseManager


BASE_URL = ("https://www.homegate.ch/{type}/real-estate/"
            "city-{city}/matching-list?{price_param}={price}&ep={page}")

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE['database_name'],
    user=local_settings.DATABASE['user'],
    password=local_settings.DATABASE['password'],
    host=local_settings.DATABASE['host'],
    port=local_settings.DATABASE['port'],
)

# Define the Apartment model
class Apartment(peewee.Model):
    rooms = peewee.FloatField()
    space = peewee.IntegerField()
    price = peewee.IntegerField()
    title = peewee.CharField()
    address = peewee.CharField()
    city = peewee.CharField()
    type = peewee.CharField()

    class Meta:
        database = database_manager.db


# Function to save data to database
def save_to_db(df):
    try:
        # Create Apartment table in the database
        database_manager.create_tables(models=[Apartment])
        for _, row in df.iterrows():
            rooms = row.rooms
            space = row.space
            price = row.price
            title = row.title
            address = row.address
            city = row.city
            type = row.type

            Apartment.create(rooms=rooms, space=space, price=price, title=title, address=address,
                             city=city, type=type)

        print(f"{len(df.index)} records successfully inserted into database.")

    except Exception as exp:
        print(exp)


def get_user_input():
    parser = argparse.ArgumentParser(
        description='Get city, price, and type from user using command-line arguments')
    parser.add_argument('-c', '--city', type=str,
                        help='Specify the city', required=True)
    parser.add_argument('-t', '--type', type=str, choices=[
                        'buy', 'rent'], help='Specify the type (buy or rent)', required=True)
    parser.add_argument('-p', '--price', type=int,
                        help='Specify the maximum price', required=True)

    args = parser.parse_args()

    if not args.city or not args.type:
        print("Please provide city, type, and price using the --city, --type, and --price arguments.")
        return None, None, None

    return args.city, args.type, args.price


def scrape_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        return {}

    rooms_list = []
    price_list = []
    space_list = []
    address_list = []
    title_list = []

    soup = BeautifulSoup(response.text, 'html.parser')

    prices_span = soup.find_all(
        'span', class_='HgListingCard_price_JoPAs')
    rooms_space_div = soup.find_all(
        'div', class_='HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq')

    address_div = soup.find_all(
        'div', class_='HgListingCard_address_JGiFv')

    title_p_tag = soup.find_all(
        'p', class_='HgListingDescription_title_NAAxy')

    for i in range(len(prices_span)):
        # Extract number from text
        price = re.sub(r'\D', '', prices_span[i].text)
        if price:
            price_list.append(int(price))
        else:
            price_list.append(None)

        address_list.append(address_div[i].text)
        title_list.append(title_p_tag[i].text)

        span_tags = rooms_space_div[i].find_all('span')

        if len(span_tags) == 2:  # There is data for room and space.
            rooms_text = span_tags[0].text
            # Extract number from text
            match = re.search(r'\d+(\.\d+)?', rooms_text)
            rooms = float(match.group()) if '.' in match.group() else int(
                match.group())
            rooms_list.append(rooms)

            space_text = span_tags[1].text
            # Extract number from text
            space = re.sub(r'\D', '', space_text)
            space = int(space)
            space_list.append(space)

        # There is data only for room or space (not both).
        elif len(span_tags) == 1:
            if 'room' in span_tags[0].text:
                rooms_text = span_tags[0].text
                # Extract number from text
                match = re.search(r'\d+(\.\d+)?', rooms_text)
                rooms = float(match.group()) if '.' in match.group() else int(
                    match.group())
                rooms_list.append(rooms)
                space_list.append(None)
            if 'space' in span_tags[0].text:
                space_text = span_tags[0].text
                # Extract number from text
                space = re.sub(r'\D', '', space_text)
                space = int(space)
                rooms_list.append(None)
                space_list.append(space)

        else:  # There is no data for either room or space.
            rooms_list.append(None)
            space_list.append(None)

    data = {"rooms": rooms_list, "space": space_list,
            "price": price_list, "address": address_list,
            "title": title_list}
    df = pd.DataFrame(data)
    return df


def show_plots(df):
    df.sort_values(by='space', inplace=True)
    plt.figure(figsize=(14, 6))

    # Subplot for relationship between space and price of apartments
    plt.subplot(1, 2, 1)
    plt.scatter(df['space'], df['price'])
    plt.title('Relationship Between Space and Price of Apartments')
    plt.xlabel('Space (Square Meter)')
    plt.ylabel('Price')
    plt.grid(True)

    # Subplot for distribution of prices based on number of rooms
    plt.subplot(1, 2, 2)
    sns.boxplot(x='rooms', y='price', data=df)
    plt.title(
        'Distribution of Prices Based on Number of Rooms')
    plt.xlabel('Number of Rooms')
    plt.ylabel('Price')
    plt.tight_layout(pad=5)
    plt.show()


if __name__ == "__main__":
    try:
        # Get user input via arguments
        ad_city, ad_type, ad_price = get_user_input()
        if ad_city and ad_type and ad_price:
            ad_city = ad_city.lower()

        # Initialize final DataFrame
        data = {"rooms": [], "space": [],
                "price": [], "address": [], "title": []}
        final_df = pd.DataFrame(data)

        # Ignore pandas warnings
        pd.options.mode.chained_assignment = None
        warnings.simplefilter(action='ignore', category=FutureWarning)

        page = 1
        while True:
            price_param = 'aj' if ad_type == 'buy' else 'ah'
            url = BASE_URL.format(type=ad_type, city=ad_city,
                                  price_param=price_param, price=ad_price, page=page)

            response = requests.get(url)

            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            list_items = soup.find_all('div', {'role': 'listitem'})

            if not list_items:
                break

            print(f"Extracting data from {url}")

            # Scrape the url
            df = scrape_url(url)
            final_df = pd.concat([final_df, df], ignore_index=True)
            time.sleep(1)
            page += 1

        # Clean the data
        final_df_cleaned = final_df.dropna(subset=['rooms', 'space', 'price'])

        # Add city and type
        final_df_cleaned["city"] = ad_city
        final_df_cleaned["type"] = ad_type

        if len(final_df_cleaned.index) > 0:
            # Save data to database
            save_to_db(final_df_cleaned)

            # Show plots
            show_plots(final_df_cleaned)

        else:
            print('No apartment found.')

    except Exception as exp:
        print(exp)
