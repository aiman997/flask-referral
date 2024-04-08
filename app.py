from flask import Flask, request, render_template, jsonify
import logging
import csv

app = Flask(__name__)

# Set up logger to console with level DEBUG
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.DEBUG)

if not app.debug:
    # Configure file logging
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

#read CSV and build referral relationships
def build_referral():
    app.logger.debug('Building referral map.')
    referral_map = {}
    with open('data/client.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  #skip header row
        for row in reader:
            referrer_email = row[1].strip().lower()
            referral_email = row[0].strip()
            if referrer_email: #Check if referrer email is not empty
                referral_map.setdefault(referrer_email, []).append(referral_email)
    return referral_map

def get_all_referrals(email, referral_map, depth=0, seen=None):
    if seen is None:
        seen = set()
    lines = []
    lower_email = email.lower()
    # Prevent processing if we've already seen this email
    if lower_email in seen:
        return lines
    seen.add(lower_email)

    referrals = referral_map.get(lower_email, [])
    for referral in referrals:
        indent = '>>>> ' * depth if depth > 0 else ''
        lines.append(f"{indent}{referral}")
        lines.extend(get_all_referrals(referral, referral_map, depth + 1, seen))
    return lines

  
@app.route('/', methods = ['GET', 'POST'])
def index():
    app.logger.debug('Accessed the main page')
    referral_map = build_referral()
    app.logger.debug(f'Referral Map: {referral_map}')
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        app.logger.debug(f'Form submitted with email: {email}')
        # referrals = referral_map.get(email, [])
        all_referrals = get_all_referrals(email, referral_map)
        app.logger.debug(f'Referrals found: {all_referrals}')
        return render_template('index.html', referrals=all_referrals, email=email)
    return render_template('index.html', referrals=[], email='')


@app.route('/test/referrals')
def test_referrals():
    referral_map = build_referral()
    return jsonify(referral_map)

    

if __name__ == '__main__':
    app.run(debug=True)

