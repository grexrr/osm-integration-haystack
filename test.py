from haystack import Document

element = {
    "type": "node",
    "id": 13093263681,
    "lat": 51.8976739,
    "lon": -8.475463,
    "tags": {
    "addr:city": "Cork",
    "addr:housenumber": "76",
    "addr:street": "Grand Parade",
    "check_date": "2025-08-24",
    "contact:facebook": "https://www.facebook.com/grandsiammassage",
    "level": "2",
    "name": "Grand Siam Massage Centre",
    "opening_hours": "Mo-Su 11:00-20:00",
    "phone": "+353868496423",
    "shop": "massage",
    "toilets": "yes",
    "website": "https://www.grandsiammassage.com",
    "wheelchair": "no"
    }
}
  
# goal

data =   {
    "id": "55984f3a935d3c6f2fd9037f1f07f40f1d3e710d531523ac5c43b2cd5a157174",
    "content": 'Massage: Grand Siam Massage Centre, 76 Grand Parade, Cork. Tags: opening_hours=Mo-Su 11:00-20:00, wh...', 
    "meta": {
        "source": "openstreetmap",
        "osm_id": 13093263681,
        "osm_type": "node",
        "name": "Grand Siam Massage Centre",
        "category": "massage",
        "lat": 51.8971558,
        "lon": -8.4754237,
        "bbox": None,
        "address": { "street": "Grand Parade", "housenumber": "76", "city": "Cork" },

        "tags_norm": {
            "shop": "massage",
            "opening_hours": "Mo-Su 11:00-20:00",
            "toilets": True,
            "website": "https://www.grandsiammassage.com",
            "phone": "+353868496423",
            "wheelchair": False,
            "contact_facebook": "https://www.facebook.com/grandsiammassage",
            "level": "2",
            "check_date": "2025-08-24"
        },

        "tags_raw": {
            "shop": "massage",
            "opening_hours": "Mo-Su 11:00-20:00",
            "toilets": "yes",
            "website": "https://www.grandsiammassage.com",
            "phone": "+353868496423",
            "wheelchair": "no",
            "contact:facebook": "https://www.facebook.com/grandsiammassage",
            "level": "2",
            "check_date": "2025-08-24"
        },

        "overpass_query": None,
        "retrieved_at": "2025-10-16T00:00:00Z",
        "distance_m": None
    }
}


print(Document.from_dict(data))

{
    "id":"55984f3a935d3c6f2fd9037f1f07f40f1d3e710d531523ac5c43b2cd5a157174", 
    
    "content": 'Massage: Grand Siam Massage Centre, 76 Grand Parade, Cork. Tags: opening_hours=Mo-Su 11:00-20:00, wh...', 
    
    "meta": {
        'source': 
        'openstreetmap', 
        'osm_id': 5812648456, 
        'osm_type': 'node', 
        'name': 'Grand Siam Massage Centre', 
        'category': 'massage', 
        'lat': 51.8971558, 
        'lon': -8.4754237, 
        'address': {
            'street': 
            'Grand Parade', 
            'housenumber': '76', 
            'city': 'Cork'}, 
        'tags': {
            'shop': 
            'massage', 
            'opening_hours': 
            'Mo-Su 11:00-20:00', 
            'toilets': 
            'yes', 
            'website': 'https://www.grandsiammassage.com', 
            'phone': '+353868496423', 
            'wheelchair': 'no', 
            'contact:facebook': 'https://www.facebook.com/grandsiammassage', 
            'level': '2', 
            'check_date': '2025-08-24'
        },
        'tags_norm': {
            'shop': 
            'massage', 
            'opening_hours': 
            'Mo-Su 11:00-20:00', 
            'toilets': 
            'yes', 
            'website': 'https://www.grandsiammassage.com', 
            'phone': '+353868496423', 
            'wheelchair': 'no', 
            'contact:facebook': 'https://www.facebook.com/grandsiammassage', 
            'level': '2', 
            'check_date': '2025-08-24'
        }
    }
}

