# 🎓 Online Learning Portal

This is a web-based application designed for students to enroll in online courses and manage their learning activities. Built with a modern tech stack, the portal includes user authentication, course enrollment, and review features.

## Features
- 🔐 **User Authentication** allows login and registration.
- 📋 **Dashboard** displays available courses.
- 📚 **Course Enrollment** provides a personalized course list.
- ⚙️ **Settings** enable users to update their information.
- 🌟 **Reviews and Ratings** let users submit feedback for courses.
- 🧠 **Sentiment Analysis** analyzes reviews for course feedback.

## Tech Stack
- 💻 **Frontend technologies** include HTML, CSS, JavaScript, and Bootstrap.
- 🛠️ **Backend** is powered by Flask.
- 📂 **Database** is SQLite with SQLAlchemy ORM.

## Pages
- 🔑 `login.html` is the login page for user authentication.
- 📝 `register.html` is the user registration page.
- 🏠 `dashboard.html` displays the available courses.
- ⚙️ `settings.html` allows users to update their email and contact information.
- 📑 `my_courses.html` lists the courses the user is enrolled in.
- 👤 `profile.html` displays user profile details.

## Installation

### Prerequisites
- 🐍 Python 3.7+ is required.
- 🌐 A virtual environment is optional but recommended.

### Steps

1. 📦 Clone the repository:
    ```bash
    git clone https://github.com/your-username/online-learning-portal.git
    cd online-learning-portal
    ```

2. 🛡️ Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    ```

3. 🗂️ Install dependencies:
    ```bash
    pip install flask
    pip install flask-sqlalchemy
    pip install flask-migrate
    ```

4. 🗂️ Initialize the database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

5. ▶️ Run the application:
    ```bash
    flask run
    ```
    Access the application at `http://127.0.0.1:5000/`.

## Database Models
- 👥 **User**
- 📘 **Course**
- 📝 **Enrollment**
- ✍️ **Review**
- ⚙️ **UserSettings**

## API Routes
- `/`: Redirects to the login page.
- `/login`: Handles user login.
- `/register`: Manages user registration.
- `/dashboard`: Displays the courses dashboard.
- `/enroll/<int:course_id>`: Enrolls the user in a course.
- `/my_courses`: Shows the list of enrolled courses.
- `/settings`: Allows users to update personal settings.
- `/submit_review/<int:course_id>`: Allows users to submit a review for a course.

## 🛠️ Troubleshooting

If you encounter an Internal Server Error, follow these steps to reset the database:

1. Delete the existing database:
    ```bash
    rm instance/new_learning_portal.db
    ```

2. Reinitialize the database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

3. Restart the application:
    ```bash
    flask run
    ```
This should resolve the issue. Access the application at `http://127.0.0.1:5000/`.

## Future Enhancements
- 💳 Integration with a payment gateway for paid courses.
- 📊 Advanced analytics for course performance.
- 🎨 Enhanced UI/UX with React or Angular.
