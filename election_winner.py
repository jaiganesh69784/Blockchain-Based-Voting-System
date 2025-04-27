import hashlib
import json
from time import time
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
from uuid import uuid4
import yagmail
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'static/voter_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "election.id.sender@gmail.com"
MAIL_PASSWORD = "bzjayebdfzyckukr"  # Your App Password without spaces

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key-here'  # Required for flash messages
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size 16MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/img', exist_ok=True)

class Voter:
    def __init__(self):
        self.voters_file = 'voters_data.json'
        # Initialize with default voters and their status set to False (Not Voted Yet)
        self.default_voters = {
            "550e8400-e29b-41d4-a716-446655440000": {
                "first_name": "Rahul", "last_name": "Sharma",
                "email": "rahul.s@example.com", "has_voted": False,
                "phone": "1234567890", "age": "25",
                "birth_place": "Delhi",
                "photo": "default.jpg",
                "registration_date": "2024-01-01"
            },
            "650e8400-e29b-41d4-a716-446655440001": {
                "first_name": "Priya", "last_name": "Patel",
                "email": "priya.p@example.com", "has_voted": False,
                "phone": "2345678901", "age": "28",
                "birth_place": "Mumbai",
                "photo": "default.jpg",
                "registration_date": "2024-01-01"
            },
            "750e8400-e29b-41d4-a716-446655440002": {
                "first_name": "Amit", "last_name": "Kumar",
                "email": "amit.k@example.com", "has_voted": False,
                "phone": "3456789012", "age": "32",
                "birth_place": "Bangalore",
                "photo": "default.jpg",
                "registration_date": "2024-01-01"
            },
            "850e8400-e29b-41d4-a716-446655440003": {
                "first_name": "Sneha", "last_name": "Reddy",
                "email": "sneha.r@example.com", "has_voted": False,
                "phone": "4567890123", "age": "29",
                "birth_place": "Hyderabad",
                "photo": "default.jpg",
                "registration_date": "2024-01-01"
            },
            "950e8400-e29b-41d4-a716-446655440004": {
                "first_name": "Vikram", "last_name": "Singh",
                "email": "vikram.s@example.com", "has_voted": False,
                "phone": "5678901234", "age": "35",
                "birth_place": "Chandigarh",
                "photo": "default.jpg",
                "registration_date": "2024-01-01"
            }
        }
        self.load_voters()

    def load_voters(self):
        try:
            with open(self.voters_file, 'r') as f:
                self.voters = json.load(f)
                # Reset all voting status to False
                for voter in self.voters.values():
                    voter['has_voted'] = False
        except FileNotFoundError:
            # If file doesn't exist, use default voters
            self.voters = self.default_voters
            self.save_voters()

    def save_voters(self):
        with open(self.voters_file, 'w') as f:
            json.dump(self.voters, f, indent=4)

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
        print(f"Registered voter with UIN: {uin}")
        return uin

    def is_valid_voter(self, uin):
        return uin in self.voters

    def has_voted(self, uin):
        if not self.is_valid_voter(uin):
            return False
        return self.voters[uin]['has_voted']

    def mark_as_voted(self, uin):
        if self.is_valid_voter(uin):
            self.voters[uin]['has_voted'] = True
            self.save_voters()
            print(f"Marked UIN {uin} as voted")

    def get_voter_details(self, uin):
        return self.voters.get(uin)

    def get_sample_uins(self):
        return list(self.voters.keys())

# Initialize voter system
voter_system = Voter()

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.candidate_votes = {}  # To track votes for each candidate
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_votes = []
        self.chain.append(block)
        return block

    def new_vote(self, voter_id, candidate):
        self.current_votes.append({
            'voter_id': voter_id,
            'candidate': candidate,
        })
        if candidate in self.candidate_votes:
            self.candidate_votes[candidate] += 1
        else:
            self.candidate_votes[candidate] = 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Function to get the candidate with the highest votes
    def get_winner(self):
        if not self.candidate_votes:
            return None
        winner = max(self.candidate_votes, key=self.candidate_votes.get)
        return winner, self.candidate_votes[winner]

    # Function to get all candidates with their vote counts
    def get_all_candidates_votes(self):
        return [{"candidate": candidate, "votes": votes} for candidate, votes in self.candidate_votes.items()]


# Instantiate the Node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_uin_email(email, uin):
    try:
        yag = yagmail.SMTP(MAIL_USERNAME, MAIL_PASSWORD)

        # Get voter's name from the system
        voter_details = next((details for uin_key, details in voter_system.voters.items() if details['email'] == email), None)
        voter_name = f"{voter_details['first_name']} {voter_details['last_name']}" if voter_details else "Voter"
        voting_place = voter_details['birth_place'] if voter_details else "Your registered location"

        # HTML email template with inline CSS
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Your Voting Registration Confirmation</h2>
            
            <p>Dear {voter_name},</p>
            
            <p>Thank you for registering in our Voting System!</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #2c3e50; margin-top: 0;">Your Unique Identification Number (UIN):</h3>
                <p style="font-size: 18px; font-weight: bold; color: #2980b9;">{uin}</p>
            </div>
            
            <p>Your designated voting place: <strong>{voting_place}</strong></p>
            
            <p style="color: #e74c3c; font-weight: bold;">Please keep this UIN safe and confidential, as it is required to cast your vote. Do not share this number with anyone.</p>
            
            <p>If you have any questions, feel free to contact us.</p>
            
            <p>Best regards,<br>Election Team</p>
        </div>
        """

        # Send email with HTML content only
        yag.send(
            to=email,
            subject="Your Voting Registration Confirmation",
            contents=html_content
        )

        print(f"Email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        logger.error(f"Email sending failed: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            age = request.form.get('age')
            birth_place = request.form.get('birth_place')

            # Validate required fields
            if not all([first_name, last_name, email, phone, age, birth_place]):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))

            # Validate age
            try:
                age = int(age)
                if age < 18:
                    flash('You must be 18 or older to register', 'error')
                    return redirect(url_for('register'))
            except ValueError:
                flash('Invalid age', 'error')
                return redirect(url_for('register'))

            # Handle photo upload
            if 'photo' not in request.files:
                flash('No photo uploaded', 'error')
                return redirect(url_for('register'))

            photo = request.files['photo']
            if photo.filename == '':
                flash('No photo selected', 'error')
                return redirect(url_for('register'))

            if photo and allowed_file(photo.filename):
                filename = secure_filename(f"{first_name}_{last_name}_{uuid4().hex[:8]}.{photo.filename.rsplit('.', 1)[1].lower()}")
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)

                # Generate UIN and register voter
                uin = voter_system.register_voter({
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'age': age,
                    'birth_place': birth_place
                }, filename)

                # Send email with UIN
                if send_uin_email(email, uin):
                    flash('Registration successful! Please check your email for your UIN.', 'success')
                else:
                    flash('Registration successful but email delivery failed. Please contact support.', 'warning')

                return redirect(url_for('home'))
            else:
                flash('Invalid file type. Please upload a valid image file.', 'error')

        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')

    return render_template('register.html')

@app.route('/vote', methods=['POST'])
def vote():
    values = request.get_json()
    required = ['voter_id', 'candidate']

    if not all(k in values for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    uin = values['voter_id']

    # Validate voter
    if not voter_system.is_valid_voter(uin):
        return jsonify({'error': 'Invalid UIN Number'}), 400

    if voter_system.has_voted(uin):
        return jsonify({'error': 'Already voted'}), 400

    try:
        # Record the vote directly without face verification
        voter_system.mark_as_voted(uin)
        blockchain.new_vote(uin, values['candidate'])

        # Create new block
        last_block = blockchain.chain[-1]
        proof = blockchain.proof_of_work(last_block['proof'])
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        return jsonify({
            'message': "Vote recorded successfully!",
            'index': block['index'],
            'voter_id': uin,
            'candidate': values['candidate']
        }), 200

    except Exception as e:
        logger.error(f"Error processing vote: {str(e)}")
        return jsonify({'error': 'Error processing vote'}), 500

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/winner', methods=['GET'])
def winner():
    winner, votes = blockchain.get_winner()
    if winner is None:
        return jsonify({'message': 'No votes cast yet'}), 200
    return jsonify({'winner': winner, 'votes': votes}), 200

@app.route('/candidates', methods=['GET'])
def candidates():
    candidates = blockchain.get_all_candidates_votes()
    return jsonify({'candidates': candidates}), 200

@app.route('/results')
def results():
    candidates = blockchain.get_all_candidates_votes()
    total_votes = sum(candidate['votes'] for candidate in candidates)

    # Calculate percentages
    for candidate in candidates:
        candidate['percentage'] = round((candidate['votes'] / total_votes * 100), 2) if total_votes > 0 else 0

    return render_template('results.html', candidates=candidates, total_votes=total_votes)

# Add a route to check voter registration status
@app.route('/check_registration/<uin>', methods=['GET'])
def check_registration(uin):
    voter_details = voter_system.get_voter_details(uin)
    if voter_details:
        return jsonify({
            'registered': True,
            'has_voted': voter_details['has_voted']
        }), 200
    return jsonify({'registered': False}), 404

# Add a new route to display sample UINs
@app.route('/sample_uins')
def sample_uins():
    uins = voter_system.get_sample_uins()
    voters = voter_system.voters
    return render_template('sample_uins.html', uins=uins, voters=voters)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
