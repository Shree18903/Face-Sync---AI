import os
import base64
from io import BytesIO
from PIL import Image
import qrcode
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.config['SECRET_KEY'] = 'e58a5aa93f8c49a10f4ab4b5bd40553a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'shreerambabu18903@gmail.com'
app.config['MAIL_PASSWORD'] = 'zgnyutogfhzrdubd'
mail = Mail(app)


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    photo_path = db.Column(db.String(200))
    camera_photo_path = db.Column(db.String(200))
    seat_number = db.Column(db.Integer, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

def generate_qr_code(data):
    """Generates a QR code image from the provided data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

def send_email_with_qr(user):
    """Sends an email with the seat details and QR code."""
    msg = Message('Your Event Registration Details',
                  sender='your-email@gmail.com',
                  recipients=[user.email])

    # Email body
    msg.body = f"""
    Dear {user.name},

    Thank you for registering! Here are your event details:

    Name: {user.name}
    Email: {user.email}
    Phone: {user.phone}
    Address: {user.address}
    DOB: {user.dob}
    Gender: {user.gender}
    Course: {user.course}
    Year: {user.year}
    Seat Number: {user.seat_number}

    Please find your QR code attached. Show this at the event for entry.

    Regards,
    Event Team
    """

    # Generate QR code with user details
    qr_data = f"Name: {user.name}, Seat Number: {user.seat_number}, Email: {user.email}"
    qr_img = generate_qr_code(qr_data)

    # Save QR code image to bytes
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    # Attach QR code to the email
    msg.attach(f"{user.name}_QR_Code.png", "image/png", img_io.read())

    # Send the email
    mail.send(msg)

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check available seats
        seat_count = User.query.count()
        if seat_count >= 100:
            return "Sorry, all seats are booked!"

        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob']
        gender = request.form['gender']
        course = request.form['course']
        year = request.form['year']
        photo_choice = request.form['photo_choice']
        photo = request.files.get('photo')
        camera_photo_data = request.form.get('camera_photo')

        # Create folder for user's photos
        person_folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
        if not os.path.exists(person_folder):
            os.makedirs(person_folder)

        photo_path = None
        camera_photo_path = None

        # Handle uploaded photo or camera photo
        if photo_choice == 'upload' and photo:
            photo_path = os.path.join(person_folder, photo.filename)
            photo.save(photo_path)
        elif photo_choice == 'capture' and camera_photo_data:
            image_data = base64.b64decode(camera_photo_data.split(',')[1])
            image = Image.open(BytesIO(image_data))
            camera_photo_path = os.path.join(person_folder, 'captured_photo.png')
            image.save(camera_photo_path)

        # Assign seat number based on the count
        seat_number = seat_count + 1

        # Create and save new user
        user = User(name=name, email=email, phone=phone, address=address, dob=dob, gender=gender, course=course, year=year,
                    photo_path=photo_path, camera_photo_path=camera_photo_path, seat_number=seat_number)
        db.session.add(user)
        db.session.commit()

        # Send email with QR code
        send_email_with_qr(user)

        # Redirect to success page with seat number
        return redirect(url_for('success', seat_number=seat_number))
    return render_template('register.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('aboutus.html')


@app.route('/success')
def success():
    seat_number = request.args.get('seat_number')
    return render_template('success.html', seat_number=seat_number)
# Route to display seating chart
@app.route('/seating-chart')
def seating_chart():
    # Get all users with booked seats
    booked_seats = [user.seat_number for user in User.query.all()]
    
    # Assume total seats are 100
    total_seats = 100
    seats = [{'number': i, 'booked': i in booked_seats} for i in range(1, total_seats + 1)]
    
    return render_template('seating_chart.html', seats=seats)
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
