import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
app = Flask(__name__)


# SQLAlchemy ऑब्जेक्ट को यहाँ initialize करें, लेकिन app से नहीं।
# इसे global scope में रखें ताकि models इसे एक्सेस कर सकें।
db = SQLAlchemy()

# ------------------ App Factory & Initialization ------------------

def create_app():
    """Flask app instance को initialize और कॉन्फ़िगर करता है।"""
    app = Flask(__name__)
    
    # --- App Configuration ---
    app.secret_key = os.environ.get('SECRET_KEY', "GreenTechSecretFallback")

    # --- Database Configuration ---
    
    # 1. DATABASE_URL एनवायरनमेंट वेरिएबल से URI लें, अगर न हो तो local SQLite का उपयोग करें।
    db_uri = os.getenv('DATABASE_URL', 'sqlite:///footprints.db')
    
    # 2. Modern SQLAlchemy (psycopg2) के लिए 'postgres://' को 'postgresql://' में बदलें।
    if db_uri.startswith('postgres://'):
        db_uri = db_uri.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. SQLAlchemy को App से जोड़ें
    db.init_app(app)

    # --- Routes Registration ---
    # Routes को यहाँ register करें (फंक्शन के बाहर परिभाषित हैं, इसलिए यहाँ उन्हें 
    # सीधे initialize करने की ज़रूरत नहीं है, लेकिन वे 'app' ऑब्जेक्ट का उपयोग करेंगे)।
    
    # सभी routes (home, donate, about, etc.) को सीधे app.route डेकोरेटर के तहत परिभाषित किया गया है, 
    # जो create_app() के बाहर होते हुए भी काम करेंगे। अगर आप Blueprints का उपयोग कर रहे होते, 
    # तो उन्हें यहाँ रजिस्टर करना होता: app.register_blueprint(my_blueprint)

    # 4. डेटाबेस टेबल सुनिश्चित करें
    with app.app_context():
        db.create_all()

    return app

# ------------------ Models ------------------
# Models को global scope में db.Model से inherit करना जारी रखें

class Footprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    electricity = db.Column(db.Float, nullable=False)
    water = db.Column(db.Float, nullable=False)
    travel = db.Column(db.Float, nullable=False)
    waste = db.Column(db.Float, nullable=False)
    total_co2 = db.Column(db.Float, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

class GameScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_played = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------ Routes (Functions) ------------------
# इन्हें create_app() के बाहर रखें, लेकिन 'app' के बजाय 'application' variable का उपयोग करें 
# (ताकि gunicorn सही endpoint को कॉल करे, हालांकि create_app() पैटर्न में यह कम महत्वपूर्ण है)।

# gunicorn के लिए मुख्य Entry Point
application = create_app()

@application.route('/')
def home():
    return render_template('index.html', hide_hero=False)


@application.route('/about')
def about():
    return render_template('about.html', hide_hero=False)

@application.route('/citations')
def citations():
    return render_template('citations.html', hide_hero=False)

@application.route('/tutorials')
def tutorials():
    return render_template('tutorials.html', hide_hero=False)

@application.route('/game', methods=['GET', 'POST'])
def game():
    if request.method == 'POST':
        name = request.form.get('name')
        score = int(request.form.get('score', 0))
        if name:
            new_score = GameScore(name=name, score=score)
            db.session.add(new_score)
            db.session.commit()
            flash("Your score has been saved!")
        return redirect(url_for('game'))

    leaderboard = GameScore.query.order_by(GameScore.score.desc()).limit(5).all()
    return render_template('game.html', hide_hero=True, leaderboard=leaderboard)

@application.route('/tutorials/e-waste-management')
def e_waste_management():
    return render_template('e_waste_management.html', hide_hero=False)

@application.route('/tutorials/energy-efficiency')
def energy_efficiency():
    return render_template('energy_efficiency.html', hide_hero=False)

@application.route('/tutorials/sustainable-hardware')
def sustainable_hardware():
    return render_template('sustainable_hardware.html', hide_hero=False)

@application.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # In a real app, you would send this to an email service
        print(f"New Feedback - Name: {name}, Email: {email}, Message: {message}")
        flash("Thank you for your feedback!")
        return redirect(url_for('contact'))
    return render_template('contact.html', hide_hero=False)

@application.route('/calculator', methods=['GET', 'POST'])
def calculator():
    result = None
    if request.method == 'POST':
        name = request.form.get('name')
        # Ensure name is provided, if required
        if not name:
             name = "Anonymous"
             
        electricity = float(request.form.get('electricity', 0))
        water = float(request.form.get('water', 0))
        travel = float(request.form.get('travel', 0))
        waste = float(request.form.get('waste', 0))

        # CO2 Calculations (using placeholder factors)
        co2_electricity = electricity * 0.82
        co2_water = water * 0.0003
        co2_travel = travel * 0.21
        co2_waste = waste * 1.9

        total_co2 = round(co2_electricity + co2_water + co2_travel + co2_waste, 2)

        # Save to DB
        new_entry = Footprint(
            name=name,
            electricity=electricity,
            water=water,
            travel=travel,
            waste=waste,
            total_co2=total_co2
        )
        db.session.add(new_entry)
        db.session.commit()

        flash("Your footprint has been calculated and saved!")
        result = total_co2

    # History/Leaderboard for the calculator page
    history = Footprint.query.order_by(Footprint.total_co2.asc()).limit(5).all()
    return render_template('calculator.html', result=result, history=history)


# ------------------ Run Local Server ------------------

if __name__ == '__main__':
    # लोकल रन के लिए application variable का उपयोग करें
    application.run(debug=True)
