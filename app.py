from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re  

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open("User Data").sheet1

# 📌 Updated home route: Show login/register options
@app.route("/")
def index():
    return render_template("index.html")

# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age = request.form.get("age")
        grade = request.form.get("grade")
        password = request.form.get("password")
        profile_picture = request.form.get("profile_picture", "")

        # Validate name
        if not re.match(r"^[A-Za-z\s]+$", name):
            return jsonify({"error": "Name must contain only letters and spaces"}), 400

        if not profile_picture:
            profile_picture = "No image provided"

        # Insert data into Google Sheets
        row = [name, email, age, grade, password, profile_picture]
        sheet.append_row(row)

        session["user"] = {"name": name, "email": email, "age": age, "grade": grade, "profile_picture": profile_picture}

        return redirect(url_for("profile"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = sheet.get_all_records()
        print("Fetched users from Google Sheets:", users)  # Debugging

        for user in users:
            print("Checking user:", user)  # Debugging
            print("User dictionary keys:", user.keys())  # Debugging

            # Use the correct column name for email
            email_key = next((key for key in user.keys() if "email" in key.lower()), None)
            password_key = next((key for key in user.keys() if "password" in key.lower()), None)

            if email_key and password_key:
                if user[email_key] == email:
                    if user[password_key] == password:
                        session["user"] = {
                            "name": user.get("Name", ""),
                            "email": user[email_key],
                            "age": user.get("Age", ""),
                            "grade": user.get("Grade", ""),
                            "profile_picture": user.get("profile_pic_url", ""),
                        }
                        print("User session data:", session["user"])  # Debugging
                        return redirect(url_for("profile"))
                    else:
                        error = "Incorrect password"
                        print(error)  # Debugging
                        break  # Stop checking further since the email was found

        if not error:
            error = "User not found"
            print(error)  # Debugging

    return render_template("login.html", error=error)





# Profile Route
@app.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))
    return render_template("profile.html", user=user)

# Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/")
def home():
    return render_template("Home.html")


if __name__ == "__main__":
    app.run(debug=True)




