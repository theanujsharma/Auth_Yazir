# Flask Authentication Example

A complete Flask authentication system with user registration, login, and logout functionality.

## Features

- User registration with email and username validation
- Secure password hashing
- User login with remember me functionality
- User logout
- Flash messages for user feedback
- Responsive and modern UI
- SQLite database for user storage
- Compatible with older Python versions (3.6+)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

**Alternative setup (recommended for older Python versions):**
```bash
python setup.py
```

## Compatibility Notes

This application is configured to work with Python 3.6+ and older versions by:
- Using `pbkdf2:sha256` hashing method instead of scrypt
- Using compatible versions of Flask and Werkzeug
- Explicitly setting the hashing method for better compatibility

If you encounter the "module 'hashlib' has no attribute 'scrypt'" error, the application has been configured to automatically use an alternative hashing method.

## Running the Application

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

## Usage

### Registration
- Visit `/register` or click "Register" on the home page
- Fill in your username, email, and password
- Click "Register" to create your account

### Login
- Visit `/login` or click "Login" on the home page
- Enter your email and password
- Optionally check "Remember Me" to stay logged in
- Click "Login" to access your account

### Logout
- Click "Logout" when you're logged in to sign out

## Project Structure

```
Auth_Yazir/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script for compatibility
├── README.md             # This file
├── templates/            # HTML templates
│   ├── landing_page.html # Home page
│   ├── login.html        # Login form
│   └── register.html     # Registration form
└── site.db              # SQLite database (created automatically)
```

## Database

The application uses SQLite as the database. The database file (`site.db`) will be created automatically when you first run the application.

## Security Features

- Password hashing using Werkzeug's security functions (pbkdf2:sha256)
- CSRF protection (disabled for simplicity in this example)
- Session management with Flask-Login
- Input validation with WTForms

## Troubleshooting

### Hashlib Scrypt Error
If you see the error "module 'hashlib' has no attribute 'scrypt'", this means you're using an older Python version. The application has been configured to automatically use an alternative hashing method. Simply run:

```bash
python setup.py
```

This will install compatible versions and configure the application properly.

## Customization

You can customize the application by:
- Modifying the CSS styles in the HTML templates
- Adding additional user fields to the User model
- Implementing email verification
- Adding password reset functionality
- Changing the database to PostgreSQL or MySQL

## Dependencies

- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: User session management
- Flask-WTF: Form handling and CSRF protection
- WTForms: Form validation
- Werkzeug: Security utilities 