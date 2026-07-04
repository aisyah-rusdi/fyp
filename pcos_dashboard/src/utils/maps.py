import requests
import pandas as pd
import streamlit as st

CLINIC_DATA = [
    {
        "name": "UMMC Gynecology",
        "lat": 3.1185, "lon": 101.6541,
        "type": "Hospital", "specialists": 4,
        "city": "Selangor", "district": "Petaling Jaya",
        "address": "Jalan Universiti, 46200 Petaling Jaya",
        "contact": "+60 3-7949 4422",
        "website": "https://ummc.edu.my",
        "services": "OB-GYN, PCOS Management, Fertility",
    },
    {
        "name": "Pantai Hospital KL",
        "lat": 3.1029, "lon": 101.6766,
        "type": "Hospital", "specialists": 3,
        "city": "Kuala Lumpur", "district": "Bangsar",
        "address": "8, Jalan Bukit Pantai, 59100 Kuala Lumpur",
        "contact": "+60 3-2296 0888",
        "website": "https://pantai.com.my",
        "services": "OB-GYN, Women's Health, Endocrinology",
    },
    {
        "name": "Klinik Wanita Cheras",
        "lat": 3.0816, "lon": 101.7325,
        "type": "Clinic", "specialists": 2,
        "city": "Kuala Lumpur", "district": "Cheras",
        "address": "12, Jalan Midah, 56000 Cheras",
        "contact": "+60 3-9132 8888",
        "website": "https://example.com",
        "services": "OB-GYN, PCOS Screening",
    },
    {
        "name": "Sunway Medical Gynae",
        "lat": 3.0673, "lon": 101.6041,
        "type": "Hospital", "specialists": 5,
        "city": "Selangor", "district": "Subang Jaya",
        "address": "5, Jalan Lagoon Selatan, 47500 Bandar Sunway",
        "contact": "+60 3-7491 9191",
        "website": "https://sunwaymedical.com",
        "services": "OB-GYN, PCOS Management, Fertility, Endocrinology",
    },
    {
        "name": "Prince Court Medical Centre",
        "lat": 3.1538, "lon": 101.7168,
        "type": "Hospital", "specialists": 6,
        "city": "Kuala Lumpur", "district": "KLCC",
        "address": "39, Jalan Kia Peng, 50450 Kuala Lumpur",
        "contact": "+60 3-2160 0000",
        "website": "https://princecourt.com",
        "services": "OB-GYN, PCOS Management, Fertility, Minimally Invasive Surgery, Women's Health",
    },
]

def get_backup_data():
    return pd.DataFrame(CLINIC_DATA)

@st.cache_data(ttl=3600)
def get_free_clinics_data():
    url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json][timeout:30];
    area["name"="Malaysia"]->.searchArea;
    (
      nwr["healthcare:speciality"~"gynaecology|obstetrics"](area.searchArea);
    );
    out center;
    """

    try:
        response = requests.get(url, params={'data': query}, timeout=25)
        data = response.json()

        results = []
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')

            if lat and lon:
                results.append({
                    'name': tags.get('name', 'Specialist Center'),
                    'lat': float(lat),
                    'lon': float(lon),
                    'type': tags.get('healthcare', 'Clinic'),
                    'specialists': 0,
                    'city': tags.get('addr:city') or tags.get('addr:state') or 'Kuala Lumpur',
                    'district': tags.get('addr:suburb') or tags.get('addr:district') or '',
                    'address': tags.get('addr:full') or tags.get('addr:street') or 'N/A',
                    'contact': tags.get('phone') or 'N/A',
                    'website': tags.get('website', 'https://www.moh.gov.my/'),
                    'services': tags.get('healthcare:speciality', 'Gynaecology'),
                })

        if results:
            # Merge API results with our curated list, curated list takes priority
            api_df = pd.DataFrame(results)
            backup_df = get_backup_data()
            merged = pd.concat([backup_df, api_df], ignore_index=True)
            merged = merged.drop_duplicates(subset='name', keep='first')
            return merged

        return get_backup_data()

    except Exception:
        return get_backup_data()