import hashlib
import json
from time import time
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for
from uuid import uuid4
import os
from werkzeug.utils import secure_filename
import yagmail
from datetime import datetime

# Configuration
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'voter_photos')
VOTERS_DATA_FILE = os.path.join(basedir, 'data', 'voters_data.json')
SAMPLE_VOTERS_FILE = os.path.join(basedir, 'data', 'sample_voters.json')

class Voter:
    def __init__(self):
        self.voters_file = VOTERS_DATA_FILE
        self.sample_file = SAMPLE_VOTERS_FILE
        self.voters = {}
        self.reset_voting_status()  # Reset voting status on initialization

    def reset_voting_status(self):
        """Reset all voting statuses to False on server start"""
        try:
            # Load the original sample data
            with open(self.sample_file, 'r') as f:
                self.voters = json.load(f)

            # Reset all voting statuses to False
            for uin in self.voters:
                self.voters[uin]['has_voted'] = False

            # Save the reset state
            self.save_voters()
            print("All voting statuses have been reset")
        except FileNotFoundError:
            print("Sample voters file not found")
            self.create_sample_voters()

    def save_voters(self):
        """Save current voter state to the active voters file"""
        with open(self.voters_file, 'w') as f:
            json.dump(self.voters, f, indent=4)

    def mark_as_voted(self, uin):
        """Mark a voter as having voted (only in current session)"""
        if self.is_valid_voter(uin):
            self.voters[uin]['has_voted'] = True
            self.save_voters()
            print(f"Marked UIN {uin} as voted")

    def register_voter(self, data, photo_filename):
        uin = str(uuid4())
        self.voters[uin] = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data['email'],
            'phone': data['phone'],
            'age': data['age'],
            'birth_place': data['birth_place'],
            'photo': photo_filename,
            'has_voted': False,
            'registration_date': datetime.now().strftime('%Y-%m-%d')
        }
        self.save_voters()
        return uin

    def is_valid_voter(self, uin):
        return uin in self.voters

    def has_voted(self, uin):
        if not self.is_valid_voter(uin):
            return False
        return self.voters[uin]['has_voted']

    def get_voter_details(self, uin):
        return self.voters.get(uin)

    def get_sample_uins(self):
        return list(self.voters.keys())

# Create a separate sample_voters.json file

# Update the initialization in your main app code
voter_system = Voter()

# Add this at the end of your file
def reset_all_votes():
    """Function to reset all votes"""
    voter_system.reset_voting_status()

if __name__ == '__main__':
    reset_all_votes()
    app.run(debug=True)