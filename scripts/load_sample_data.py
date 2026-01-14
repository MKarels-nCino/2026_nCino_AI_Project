"""
Load sample data into SQLite database using SQLAlchemy
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from database import db
from models import Location, Board
import uuid

def load_sample_data():
    """Load sample locations and boards"""
    app = create_app()
    
    with app.app_context():
        # Check if data already exists
        locations = Location.find_all()
        boards = Board.query.all() if hasattr(Board, 'query') else []
        
        if len(locations) > 0:
            print(f"✓ Found {len(locations)} existing location(s)")
            for loc in locations:
                print(f"  - {loc.name}")
            if len(boards) > 0:
                print(f"✓ Found {len(boards)} existing board(s)")
            return
        
        print("Loading sample data...")
        
        # Create Lake Shore Location
        location = Location(
            id=str(uuid.uuid4()),
            name='Lake Shore Location',
            timezone='America/Chicago',
            address='123 Lake Shore Drive, Chicago, IL'
        )
        location.save()
        print(f"✓ Created location: {location.name} (ID: {location.id})")
        
        # Create sample boards
        boards_data = [
            {'name': 'The Windy City Wipeout', 'brand': 'Beginner Friendly', 'size': '9\'0', 'status': 'available', 'condition': 'excellent'},
            {'name': 'Da Bears Board', 'brand': 'Chicago Special', 'size': '8\'6', 'status': 'available', 'condition': 'good'},
            {'name': 'Lake Michigan Dreamer', 'brand': 'Great Lakes', 'size': '9\'6', 'status': 'available', 'condition': 'excellent'},
            {'name': 'The Fall Classic', 'brand': 'Autumn Collection', 'size': '8\'0', 'status': 'available', 'condition': 'good'},
            {'name': 'Movie Night Special', 'brand': 'Entertainment Series', 'size': '7\'6', 'status': 'available', 'condition': 'good'},
            {'name': 'Beginner\'s Luck', 'brand': 'First Timer', 'size': '10\'0', 'status': 'available', 'condition': 'excellent'},
            {'name': 'The Wipeout Warrior', 'brand': 'Adventure Line', 'size': '8\'6', 'status': 'available', 'condition': 'good'},
            {'name': 'Chicago Pride', 'brand': 'Windy City', 'size': '9\'0', 'status': 'available', 'condition': 'excellent'},
            {'name': 'The October Surfer', 'brand': 'Fall Collection', 'size': '8\'0', 'status': 'available', 'condition': 'good'},
            {'name': 'Film Buff Board', 'brand': 'Cinema Series', 'size': '7\'6', 'status': 'available', 'condition': 'good'}
        ]
        
        # Check if Board model exists and is SQLAlchemy model
        try:
            from models.board import Board
            if hasattr(Board, '__table__'):  # It's a SQLAlchemy model
                for board_data in boards_data:
                    board = Board(
                        id=str(uuid.uuid4()),
                        location_id=location.id,
                        **board_data
                    )
                    board.save()
                    print(f"  ✓ Created board: {board.name}")
                print(f"\n✓ Created {len(boards_data)} boards")
            else:
                print("⚠ Board model not converted to SQLAlchemy yet - skipping boards")
        except ImportError:
            print("⚠ Board model not found - skipping boards")
        
        print("\n✓ Sample data loaded successfully!")
        print(f"\nDatabase now contains:")
        print(f"  - {len(Location.find_all())} location(s)")
        if hasattr(Board, 'query'):
            print(f"  - {len(Board.query.all())} board(s)")

if __name__ == '__main__':
    load_sample_data()
