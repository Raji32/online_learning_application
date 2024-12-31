from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
from flask_migrate import Migrate
import logging
# from textblob import TextBlob


logging.basicConfig(level=logging.DEBUG)

secret_key = secrets.token_hex(16)
print(f"Generated secret key: {secret_key}")

app = Flask(__name__)
app.secret_key = secret_key

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "new_learning_portal.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#DB Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    contact_number = db.Column(db.String(15), nullable=True)

  
    enrolled_courses = db.relationship('Enrollment', back_populates='user')
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)
    reviews = db.relationship('Review', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    video_url = db.Column(db.String(255), nullable=False)
    avg_rating = db.Column(db.Float, default=0.0) 

    enrolled_users = db.relationship('Enrollment', back_populates='course')
    reviews = db.relationship('Review', back_populates='course')

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    user = db.relationship('User', back_populates='enrolled_courses')
    course = db.relationship('Course', back_populates='enrolled_users')



class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    contact_number = db.Column(db.String(15), nullable=True)

    user = db.relationship('User', back_populates='settings')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)

    course = db.relationship('Course', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

@app.before_first_request
def populate_courses():
    if Course.query.count() == 0:
        print("No courses found, populating...")  
        courses = [
            Course(
                title="Python for Beginners",
                description="Master the basics of Python programming with this comprehensive course.",
                image_url="static/images/python1.jpg",
                video_url="static/videos/python_video.mp4"
            ),
            Course(
                title="Web Development with Flask",
                description="Learn to build modern web applications with Flask and Python.",
                image_url="static/images/flask.jpg",
                video_url="static/videos/flask_video.mp4"
            ),
            Course(
                title="Java Essentials",
                description="Get started with Java basics!",
                image_url="static/images/java.jpg",
                video_url="static/videos/java_videos.mp4"
            )
        ]
        db.session.add_all(courses)
        db.session.commit()
        print("Courses populated.") 

        reviews = [
            Review(course_id=1, rating=5, comment="Great course for beginners!"),
            Review(course_id=1, rating=4, comment="Very detailed and easy to understand."),
            Review(course_id=2, rating=5, comment="Excellent Flask tutorials!"),
            Review(course_id=2, rating=3, comment="Good course but could use more examples."),
            Review(course_id=3, rating=4, comment="Java basics covered well."),
            Review(course_id=3, rating=5, comment="Perfect for Java newbies.")
        ]
        db.session.add_all(reviews)
        db.session.commit()
        print("Courses and default reviews populated.")  



# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            print(f"User session: {session['user_id']}")  
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        email = request.form['email']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
       
        elif User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
        else:
            try:
                new_user = User(username=username, password=password, email=email)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()  
                flash(f"An error occurred: {e}", 'danger')
                return redirect(url_for('register'))

    return render_template('register.html')

#sentiment analysis function 
def summarize_reviews_and_sentiment(reviews):
    """
    Summarize reviews by calculating sentiment and providing a textual summary.
    """
    if not reviews:
        return {
            "sentiment": {"positive": 0, "neutral": 0, "negative": 0},
            "summary": "No reviews available."
        }

    positive = sum(1 for r in reviews if r.rating >= 4)
    neutral = sum(1 for r in reviews if r.rating == 3)
    negative = sum(1 for r in reviews if r.rating <= 2)
    total = len(reviews)

    sentiment = {
        "positive": round((positive / total) * 100),
        "neutral": round((neutral / total) * 100),
        "negative": round((negative / total) * 100),
    }

    if positive / total > 0.6:
        summary = "This course is highly recommended by users, with overwhelmingly positive feedback."
    elif neutral / total > 0.6:
        summary = "Users found this course to be good, but there is room for improvement."
    elif negative / total > 0.6:
        summary = "Most users were dissatisfied with this course."
    else:
        summary = "This course has mixed reviews, with varied opinions from users."

    return {
        "sentiment": sentiment,
        "summary": summary
    }


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('login'))

    courses = Course.query.all()
    course_data = []
    for course in courses:
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(course_id=course.id).scalar() or 0
        reviews = Review.query.filter_by(course_id=course.id).all()
        for review in reviews:
            print(f"Review ID: {review.id}, Course ID: {review.course_id}, User ID: {review.user_id}, Rating: {review.rating}, Comment: {review.comment}")

        sentiment_and_summary = summarize_reviews_and_sentiment(reviews)  

        course_data.append({
            'course': course,
            'avg_rating': round(avg_rating, 1),
            'reviews': reviews,
            'sentiment': sentiment_and_summary['sentiment'],
            'summary': sentiment_and_summary['summary']
        })
    
    return render_template('dashboard.html', user=user, course_data=course_data)


@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if not Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first():
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('my_courses'))

@app.route('/my_courses')
def my_courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    return render_template('my_courses.html', enrollments=enrollments)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    settings = UserSettings.query.filter_by(user_id=user.id).first()

    if request.method == 'POST':
        email = request.form['email']
        contact_number = request.form['contact_number']

        if settings:
            settings.email = email if email else settings.email
            settings.contact_number = contact_number if contact_number else settings.contact_number
        else:
            new_settings = UserSettings(user_id=user.id, email=email, contact_number=contact_number)
            db.session.add(new_settings)

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('profile'))  

    return render_template('settings.html', user=user, settings=settings)



@app.route('/submit_review/<int:course_id>', methods=['POST'])
def submit_review(course_id):
    try:
        comment = request.form.get('comment')
        rating = request.form.get('rating')
        if not comment or not rating:
            flash("Comment and rating are required!", 'danger')
            return redirect(url_for('course_detail', course_id=course_id))

        rating = int(rating)  

        review = Review(course_id=course_id, user_id=session.get('user_id'), rating=rating, comment=comment)

        # review = Review(course_id=course_id, comment=comment, rating=rating)
        db.session.add(review)
        db.session.commit()

        avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(course_id=course_id).scalar() or 0
        course = Course.query.get(course_id)
        course.avg_rating = round(avg_rating, 1)
        
        db.session.commit()
        sentiment_data = summarize_reviews_and_sentiment(comment=comment)

        flash(f'Your review is submitted! Sentiment: {sentiment_data["sentiment"]}', 'success')
        return redirect(url_for('dashboard', course_id=course_id))

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('dashboard', course_id=course_id))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    user = User.query.get(session['user_id']) 
    settings = UserSettings.query.filter_by(user_id=user.id).first()  

    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    # enrolled_courses = Course.query.join(Enrollment).filter(Enrollment.user_id == user.id).all()

    return render_template('profile.html', user=user, settings=settings, enrollments=enrollments)



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
