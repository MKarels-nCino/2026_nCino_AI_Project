"""
Load company data into SQLite database
This loads the actual company data from the migration files
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from database import db
from models import Location, Board
import uuid


def load_company_data():
    """Load company locations and boards"""
    app = create_app()

    with app.app_context():
        # Check if data already exists
        locations = Location.find_all()
        boards = Board.query.all() if hasattr(Board, "query") else []

        if len(locations) > 0 and len(boards) > 0:
            print(f"✓ Company data already loaded:")
            print(f"  - {len(locations)} location(s)")
            for loc in locations:
                loc_boards = Board.find_by_location(loc.id)
                print(f"    * {loc.name}: {len(loc_boards)} boards")
            print(f"  - {len(boards)} total board(s)")
            return

        print("Loading company data...")

        # Create distinct locations
        location_data = [
            {
                "name": "Lake Shore Location",
                "timezone": "America/Chicago",
                "address": "123 Lake Shore Drive, Chicago, IL",
            },
            {
                "name": "San Diego Location",
                "timezone": "America/Los_Angeles",
                "address": "456 Ocean Blvd, San Diego, CA",
            },
            {
                "name": "Miami Location",
                "timezone": "America/New_York",
                "address": "789 Beachfront Ave, Miami, FL",
            },
            {
                "name": "Wrightsville Beach Location",
                "timezone": "America/New_York",
                "address": "101 Causeway Dr, Wrightsville Beach, NC",
            },
        ]

        created_locations = []
        for data in location_data:
            existing_location = Location.query.filter_by(name=data["name"]).first()
            if not existing_location:
                location = Location(id=str(uuid.uuid4()), **data)
                location.save()
                created_locations.append(location)
                print(f"✓ Created: {location.name}")
            else:
                created_locations.append(existing_location)
                print(f"✓ Location already exists: {existing_location.name}")

        # Board data organized by location theme with local surfboard images
        # Images are stored in static/img/ as surfboard_1.webp, surfboard_2.jpg, etc.
        import os
        static_img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img')
        image_files = sorted([f for f in os.listdir(static_img_dir) if f.startswith('surfboard_')]) if os.path.exists(static_img_dir) else []
        image_paths = [f'img/{img}' for img in image_files] if image_files else []
        
        boards_by_location = {
            "Lake Shore Location": [
                {
                    "name": "The Windy City Wipeout",
                    "brand": "Beginner Friendly",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Da Bears Board",
                    "brand": "Chicago Special",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Lake Michigan Dreamer",
                    "brand": "Great Lakes",
                    "size": "9'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "The Fall Classic",
                    "brand": "Autumn Collection",
                    "size": "8'0",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Chicago Pride",
                    "brand": "Windy City",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "The October Surfer",
                    "brand": "Fall Collection",
                    "size": "8'0",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Beginner's Luck",
                    "brand": "First Timer",
                    "size": "10'0",                    "status": "available",
                    "condition": "excellent",
                },
            ],
            "San Diego Location": [
                {
                    "name": "Pacific Sunset",
                    "brand": "West Coast",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "San Diego Swell",
                    "brand": "SoCal Special",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Mission Beach Cruiser",
                    "brand": "Beach Life",
                    "size": "9'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "La Jolla Legend",
                    "brand": "Premium Line",
                    "size": "8'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Coronado Classic",
                    "brand": "Island Style",
                    "size": "7'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Pacific Beach Pro",
                    "brand": "Pro Series",
                    "size": "8'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Del Mar Dreamer",
                    "brand": "Luxury Collection",
                    "size": "9'0",                    "status": "available",
                    "condition": "good",
                },
            ],
            "Miami Location": [
                {
                    "name": "South Beach Star",
                    "brand": "Miami Vice",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Art Deco Dream",
                    "brand": "Vintage Style",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Ocean Drive Cruiser",
                    "brand": "Beach Party",
                    "size": "9'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Key Biscayne",
                    "brand": "Tropical",
                    "size": "8'0",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Coconut Grove",
                    "brand": "Island Vibes",
                    "size": "7'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Miami Heat",
                    "brand": "Hot Waves",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Biscayne Bay",
                    "brand": "Bay Rider",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
            ],
            "Wrightsville Beach Location": [
                {
                    "name": "Carolina Classic",
                    "brand": "East Coast",
                    "size": "9'0",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Wrightsville Wave",
                    "brand": "NC Special",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Crystal Coast Cruiser",
                    "brand": "Beach Ready",
                    "size": "9'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Cape Fear Rider",
                    "brand": "Adventure",
                    "size": "8'0",                    "status": "available",
                    "condition": "good",
                },
                {
                    "name": "Outer Banks",
                    "brand": "OBX Style",
                    "size": "7'6",                    "status": "available",
                    "condition": "excellent",
                },
                {
                    "name": "Wilmington Wave",
                    "brand": "Port City",
                    "size": "8'6",                    "status": "available",
                    "condition": "good",
                },
            ],
        }

        # Assign boards to locations
        total_boards = 0
        image_index = 0
        for location in created_locations:
            location_boards = boards_by_location.get(location.name, [])
            if location_boards:
                for board_data in location_boards:
                    # Add image URL if available
                    if image_paths and image_index < len(image_paths):
                        board_data["image_url"] = image_paths[image_index]
                        image_index += 1
                    
                    # Check if board already exists to prevent duplicates
                    existing_board = Board.query.filter_by(
                        name=board_data["name"], location_id=location.id
                    ).first()
                    if not existing_board:
                        board = Board(
                            id=str(uuid.uuid4()), location_id=location.id, **board_data
                        )
                        board.save()
                        total_boards += 1
                        print(f"  ✓ Created board: {board.name} at {location.name}")
                    else:
                        print(
                            f"  ✓ Board already exists: {existing_board.name} at {location.name}"
                        )

        print(f"\n✓ Company data loaded successfully!")
        print(f"\nDatabase now contains:")
        all_locations = Location.find_all()
        print(f"  - {len(all_locations)} location(s)")
        for loc in all_locations:
            loc_boards = Board.find_by_location(loc.id)
            print(f"    * {loc.name}: {len(loc_boards)} boards")
        all_boards = Board.query.all()
        print(f"  - {len(all_boards)} total board(s)")


if __name__ == "__main__":
    load_company_data()
