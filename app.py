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
            if row[1]: #second column containing referrers email
                referral_map.setdefault(row[1], []).append(row[0])
    return referral_map
  
@app.route('/', methods = ['GET', 'POST'])
def index():
    app.logger.debug('Accessed the main page')
    referral_map = build_referral()
    app.logger.debug(f'Referral Map: {referral_map}')
    if request.method == 'POST':
        email = request.form['email']
        app.logger.debug(f'Form submitted with email: {email}')
        referrals = referral_map.get(email, [])
        app.logger.debug(f'Referrals found: {referrals}')
        return render_template('index.html', referrals=referrals, email=email)
    return render_template('index.html', referrals=[], email='')


@app.route('/test/referrals')
def test_referrals():
    referral_map = build_referral()
    return jsonify(referral_map)

    

if __name__ == '__main__':
    app.run(debug=True)

