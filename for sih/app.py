from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

users = {}  


def classify_waste_model(image_data):
    """
    A dummy function to simulate a machine learning model for waste classification.
    The classification is based on the length of the image data.
    """
    if len(image_data) % 3 == 0:
        return {"category": "recyclable", "confidence": 0.95}
    elif len(image_data) % 2 == 0:
        return {"category": "organic", "confidence": 0.88}
    else:
        return {"category": "hazardous", "confidence": 0.75}

@app.route("/")
def root():
    """Redirects the user to the registration page upon initial visit."""
    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "Username already exists! <a href='/register'>Try Again</a>"

        # Initialize incentives for the new user
        users[username] = {"password": password, "points": 0}
        return "Registration successful! <a href='/login'>Go to Login</a>"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password <a href='/login'>Try Again</a>"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """
    Displays the user dashboard.
    Redirects to the login page if the user is not authenticated.
    """
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = users.get(username, {})
    points = user_data.get("points", 0)

    return render_template("index.html", username=username, points=points)

@app.route("/map")
def google_map():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("map.html")


@app.route("/logout")
def logout():
    """Clears the user's session and redirects to the registration page."""
    session.clear()
    return redirect(url_for("register"))

@app.route("/classify-waste", methods=["POST"])
def classify():
    """
    Receives an image, classifies the waste, and updates user points if it's recyclable.
    Returns a JSON response with the classification result and new point total.
    """
    if "username" not in session:
        return jsonify({"status": "error", "message": "User not logged in"})

    data = request.json.get("image", "")
    result = classify_waste_model(data)

   
    if result["category"] == "recyclable":
        users[session["username"]]["points"] += 10  # +10 points for recycling

    return jsonify({
        "status": "success",
        "classification": result,
        "points": users[session["username"]]["points"]
    })

if __name__ == "__main__":
    app.run(debug=True)