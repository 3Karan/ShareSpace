**ShareSpace**
ShareSpace is a Flask-based web application designed to manage shared workspaces. It allows users to book workspaces, manage bookings, and handle payments. Admins can manage workspaces and user bookings. The application integrates with MongoDB for data storage and provides features like user authentication, user and admin dashboards, booking functionalities, and payment processing.

**Features**
User Authentication: Sign up, login, and manage profiles.
Workspace Management: View available workspaces with details like name, description, location, price plan, availability status, maintenance status, and category.
Booking System: Users can book workspaces, and admins can manage these bookings.
Payment Processing: Users can make payments and view payment history.
Admin Dashboard: Manage users, workspaces, and bookings.
**Technologies Used**
Backend: Flask
Database: MongoDB (using MongoDB Atlas)
Frontend: HTML, CSS, Bootstrap
Other Libraries: Flask-Session, Flask-WTF, pymongo, dnspython
**Installation**

Clone the repository:
git clone https://github.com/yourusername/ShareSpace.git
cd ShareSpace

Create a virtual environment:
python3 -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`

Install dependencies:
pip install -r requirements.txt

Set up MongoDB:
Create a MongoDB cluster on MongoDB Atlas.
Replace the connection string in the Flask application configuration with your MongoDB Atlas connection string.

Run the application:
flask run

**Configuration**
Update the MongoDB connection string in the application configuration file (config.py or similar) with your MongoDB Atlas connection string.

**Usage**
User:
Sign up and log in to access the user dashboard.
View available workspaces and make bookings.
Proceed to checkout and make payments.
View booking and payment history.

Admin:
Log in to access the admin dashboard.
Manage users, workspaces, and bookings.
Approve or reject user bookings and handle payment verification.


Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code follows the project’s coding guidelines and includes appropriate tests.

Contact
For any questions or issues, please open an issue in the repository or contact the maintainer at kabiranavghan2454@gmail.com
