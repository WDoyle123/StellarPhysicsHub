import requests
import pandas as pd

def download_csv(url, target_path):
    # Send a GET request to the URL
    response = requests.get(url, allow_redirects=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content to a file
        with open(target_path, 'wb') as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

# URL of the raw CSV file on GitHub
csv_url = "https://raw.githubusercontent.com/WDoyle123/StarScholar3D/main/data/all_constellations_and_their_stars.csv"

# Local path where you want to save the file
save_path = "all_constellations_and_their_stars.csv"

# Call the function with the URL and the desired save path
download_csv(csv_url, save_path)

from app import app
from models import Constellation, Star, db

df = pd.read_csv(save_path)

# Create an application context
with app.app_context():  
    # Extract unique constellations
    unique_constellations = df['constellation_common_name'].unique()

    for constellation_name in unique_constellations:
        constellation = Constellation.query.filter_by(name=constellation_name).first()
        if not constellation:
            constellation = Constellation(name=constellation_name)
            db.session.add(constellation)
    db.session.commit()

    for _, row in df.iterrows():
        # Find the corresponding constellation
        constellation = Constellation.query.filter_by(name=row['constellation_common_name']).first()
        
        # Create a new Star object
        star = Star(
            alt_name=row['alt_name'],
            hr_name=row['hr'],
            common_name=row['iau_name'],
            right_acension=row['ra_simbad'],
            declination=row['dec_simbad'],  
            bv_colour=row['bv_color'],
            vmag=row['vmag'],
            parsecs=row['distance'],  
            note=row['note'],
            source=row['source'],
            constellation_id=constellation.id if constellation else None
        )

        db.session.add(star)
    db.session.commit()
