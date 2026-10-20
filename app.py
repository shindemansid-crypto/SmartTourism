"""
Smart Tourism & Local Culture Discovery Platform
Flask + MySQL (mysql-connector-python) + Jinja2 templates.

Flow a student can explain in viva:
  HTML form  ->  Flask route  ->  parameterised MySQL query  ->  Jinja2 page
"""
import re
from functools import wraps

import mysql.connector
from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

LANGUAGES = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
CATEGORIES = [
    "Heritage", "Historical", "Nature", "Hill Station",
    "Beach", "Religious", "Adventure", "Cultural",
]
CULTURE_TYPES = [
    "Festival", "Folk Arts", "Folk Dance", "Traditional Clothing",
    "Handicraft", "Architecture", "Historical Heritage", "Local Tradition",
]
SPECIALITY_TYPES = ["Food", "Craft"]
BUSINESS_TYPES = [
    "Local Guide", "Restaurant", "Handicraft", "Handloom",
    "Artisan", "Cultural Service", "Tourism Service",
]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[0-9+\- ]{7,20}$")


# ---------------------------------------------------------------
# 1. Database helpers
# ---------------------------------------------------------------
def get_db():
    """Open one MySQL connection per request and reuse it."""
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=config.DB_HOST, user=config.DB_USER,
            password=config.DB_PASSWORD, database=config.DB_NAME,
            charset="utf8mb4")
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def fetch_all(sql, params=()):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    """Run INSERT / UPDATE / DELETE, commit, and return the new row id."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql, params)
        db.commit()
        return cursor.lastrowid
    except mysql.connector.Error:
        db.rollback()
        raise
    finally:
        cursor.close()


# ---------------------------------------------------------------
# 2. Language-aware queries (selected language, then English fallback)
# ---------------------------------------------------------------
DESTINATION_SQL = """
    SELECT d.DestinationID, d.Name, d.State, d.Region, d.Category, d.ImageURL,
           COALESCE(t.Description, e.Description) AS Description
    FROM Destinations d
    LEFT JOIN DestinationTranslations t
           ON t.DestinationID = d.DestinationID AND t.LanguageCode = %s
    LEFT JOIN DestinationTranslations e
           ON e.DestinationID = d.DestinationID AND e.LanguageCode = 'en'
"""

ATTRACTION_SQL = """
    SELECT a.AttractionID, a.Name, a.Category, a.Latitude, a.Longitude,
           a.ImageURL, a.DestinationID, d.Name AS DestinationName, d.State,
           COALESCE(t.Description, e.Description) AS Description,
           COALESCE(t.LocalSpecialities, e.LocalSpecialities) AS LocalSpecialities,
           (SELECT ROUND(AVG(r.Rating), 1) FROM Reviews r
             WHERE r.AttractionID = a.AttractionID) AS AvgRating,
           (SELECT COUNT(*) FROM Reviews r
             WHERE r.AttractionID = a.AttractionID) AS ReviewCount
    FROM Attractions a
    JOIN Destinations d ON d.DestinationID = a.DestinationID
    LEFT JOIN AttractionTranslations t
           ON t.AttractionID = a.AttractionID AND t.LanguageCode = %s
    LEFT JOIN AttractionTranslations e
           ON e.AttractionID = a.AttractionID AND e.LanguageCode = 'en'
"""

CULTURE_SQL = """
    SELECT c.CultureID, c.Title, c.ItemType, c.ImageURL, c.DestinationID,
           d.Name AS DestinationName, d.State,
           COALESCE(t.Description, e.Description) AS Description
    FROM CultureItems c
    JOIN Destinations d ON d.DestinationID = c.DestinationID
    LEFT JOIN CultureTranslations t
           ON t.CultureID = c.CultureID AND t.LanguageCode = %s
    LEFT JOIN CultureTranslations e
           ON e.CultureID = c.CultureID AND e.LanguageCode = 'en'
"""

SPECIALITY_SQL = """
    SELECT s.SpecialityID, s.Name, s.SpecialityType, s.ImageURL, s.DestinationID,
           d.Name AS DestinationName, d.State,
           COALESCE(t.Description, e.Description) AS Description
    FROM Specialities s
    JOIN Destinations d ON d.DestinationID = s.DestinationID
    LEFT JOIN SpecialityTranslations t
           ON t.SpecialityID = s.SpecialityID AND t.LanguageCode = %s
    LEFT JOIN SpecialityTranslations e
           ON e.SpecialityID = s.SpecialityID AND e.LanguageCode = 'en'
"""

BUSINESS_SQL = """
    SELECT b.BusinessID, b.Name, b.BusinessType, b.Address, b.Phone,
           b.Description, b.ImageURL, b.DestinationID,
           d.Name AS DestinationName, d.State, u.Username AS OwnerName
    FROM Businesses b
    JOIN Destinations d ON d.DestinationID = b.DestinationID
    JOIN Users u ON u.UserID = b.OwnerID
"""


def current_language():
    lang = session.get("lang", "en")
    return lang if lang in LANGUAGES else "en"


def run_translated(base_sql, where, params, order, limit):
    sql = base_sql
    if where:
        sql += " WHERE " + where
    sql += " ORDER BY " + order
    if limit:
        sql += " LIMIT " + str(int(limit))
    return fetch_all(sql, (current_language(),) + tuple(params))


def get_destinations(where="", params=(), order="d.Name", limit=None):
    return run_translated(DESTINATION_SQL, where, params, order, limit)


def get_attractions(where="", params=(), order="a.Name", limit=None):
    return run_translated(ATTRACTION_SQL, where, params, order, limit)


def get_culture(where="", params=(), order="c.CultureID", limit=None):
    return run_translated(CULTURE_SQL, where, params, order, limit)


def get_specialities(where="", params=(), order="s.SpecialityID", limit=None):
    return run_translated(SPECIALITY_SQL, where, params, order, limit)


def get_businesses(where="", params=(), order="b.Name", limit=None):
    sql = BUSINESS_SQL
    if where:
        sql += " WHERE " + where
    sql += " ORDER BY " + order
    if limit:
        sql += " LIMIT " + str(int(limit))
    return fetch_all(sql, tuple(params))


def destination_choices():
    return fetch_all("SELECT DestinationID, Name, State FROM Destinations ORDER BY State, Name")


def state_choices():
    return [row["State"] for row in fetch_all(
        "SELECT DISTINCT State FROM Destinations ORDER BY State")]


# ---------------------------------------------------------------
# 3. Template helpers
# ---------------------------------------------------------------
def image_src(path):
    """Return a usable image URL (local static file or full web URL)."""
    if not path:
        return url_for("static", filename="images/fallback.svg")
    if path.startswith(("http://", "https://")):
        return path
    return url_for("static", filename=path)


def stars(value):
    count = int(round(float(value or 0)))
    count = max(0, min(5, count))
    return "★" * count + "☆" * (5 - count)


def short_date(value):
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y")
    return str(value)[:10]


app.jinja_env.globals["image_src"] = image_src
app.jinja_env.filters["stars"] = stars
app.jinja_env.filters["short_date"] = short_date


@app.context_processor
def inject_globals():
    return {"lang": current_language(), "LANGUAGES": LANGUAGES}


def safe_target(target, default):
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return default


# ---------------------------------------------------------------
# 4. Login / role protection
# ---------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "Admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def home_url():
    if session.get("role") == "Admin":
        return url_for("admin_dashboard")
    return url_for("dashboard")


# ---------------------------------------------------------------
# 5. Auth pages — login is the first screen
# ---------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") == "Admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(home_url())
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        language = request.form.get("language", "en")

        errors = []
        if not 3 <= len(username) <= 50:
            errors.append("Username must be 3 to 50 characters long.")
        if not EMAIL_PATTERN.match(email) or len(email) > 120:
            errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm:
            errors.append("Password and confirm password do not match.")
        if language not in LANGUAGES:
            language = "en"
        if not errors and fetch_one("SELECT UserID FROM Users WHERE Email = %s", (email,)):
            errors.append("This email is already registered. Please log in.")
        if not errors and fetch_one("SELECT UserID FROM Users WHERE Username = %s", (username,)):
            errors.append("This username is already taken. Please choose another.")

        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("register.html", form=request.form)

        execute(
            "INSERT INTO Users (Username, Email, PasswordHash, Role, PreferredLanguage) "
            "VALUES (%s, %s, %s, %s, %s)",
            (username, email, generate_password_hash(password, method="pbkdf2:sha256"),
             "Tourist", language))
        flash("Registration successful. You can log in now.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form={})


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session and request.method == "GET":
        return redirect(home_url())
    if request.method == "POST":
        identity = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = fetch_one(
            "SELECT * FROM Users WHERE Email = %s OR Username = %s",
            (identity.lower(), identity))
        if user and check_password_hash(user["PasswordHash"], password):
            session.clear()
            session["user_id"] = user["UserID"]
            session["username"] = user["Username"]
            session["role"] = user["Role"]
            session["lang"] = user["PreferredLanguage"]
            flash("Welcome back, " + user["Username"] + "!", "success")
            default = home_url()
            return redirect(safe_target(request.form.get("next"), default))
        flash("Incorrect username/email or password.", "error")
        return render_template("login.html", email=identity, next=request.form.get("next", ""))
    return render_template("login.html", email="", next=request.args.get("next", ""))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/language/<code>")
def set_language(code):
    if code in LANGUAGES:
        session["lang"] = code
        if "user_id" in session:
            execute("UPDATE Users SET PreferredLanguage = %s WHERE UserID = %s",
                    (code, session["user_id"]))
    default = url_for("login") if "user_id" not in session else home_url()
    return redirect(safe_target(request.args.get("next"), default))


# ---------------------------------------------------------------
# 6. User dashboard and discovery pages
# ---------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    states = fetch_all(
        "SELECT State, COUNT(*) AS Total FROM Destinations GROUP BY State ORDER BY State")
    return render_template(
        "dashboard.html",
        destinations=get_destinations(order="d.DestinationID", limit=8),
        featured=get_attractions(order="AvgRating DESC, ReviewCount DESC, a.Name", limit=8),
        popular=get_attractions(order="ReviewCount DESC, AvgRating DESC, a.Name", limit=6),
        hidden=get_attractions(
            "a.Category IN ('Nature', 'Adventure', 'Hill Station')",
            order="ReviewCount ASC, a.Name", limit=6),
        culture=get_culture(limit=6),
        foods=get_specialities("s.SpecialityType = 'Food'", limit=6),
        crafts=get_specialities("s.SpecialityType = 'Craft'", limit=4),
        businesses=get_businesses(limit=4),
       top_rated=get_attractions(
    "EXISTS (SELECT 1 FROM Reviews r2 WHERE r2.AttractionID = a.AttractionID)",
    order="AvgRating DESC, ReviewCount DESC",
    limit=4
),
        recent_reviews=fetch_all(
            """SELECT r.ReviewID, r.Rating, r.Comment, r.`Timestamp`, u.Username,
                      a.AttractionID, a.Name AS AttractionName, a.ImageURL
               FROM Reviews r
               JOIN Users u ON u.UserID = r.UserID
               JOIN Attractions a ON a.AttractionID = r.AttractionID
               ORDER BY r.`Timestamp` DESC, r.ReviewID DESC LIMIT 4"""),
        states=states,
        categories=CATEGORIES)


@app.route("/destinations")
@login_required
def destinations():
    q = request.args.get("q", "").strip()
    state = request.args.get("state", "").strip()
    category = request.args.get("category", "").strip()
    conditions, params = [], []
    if q:
        conditions.append("(d.Name LIKE %s OR d.State LIKE %s OR d.Category LIKE %s OR d.Region LIKE %s)")
        params += ["%" + q + "%"] * 4
    if state:
        conditions.append("d.State = %s")
        params.append(state)
    if category:
        conditions.append("d.Category = %s")
        params.append(category)
    return render_template(
        "destinations.html",
        destinations=get_destinations(" AND ".join(conditions), params),
        states=state_choices(), categories=CATEGORIES,
        q=q, state=state, category=category)


@app.route("/destination/<int:destination_id>")
@login_required
def destination_detail(destination_id):
    found = get_destinations("d.DestinationID = %s", (destination_id,))
    if not found:
        abort(404)
    destination = found[0]
    related = get_destinations(
        "d.State = %s AND d.DestinationID <> %s",
        (destination["State"], destination_id), limit=3)
    params = (destination_id,)
    return render_template(
        "destination_detail.html",
        destination=destination,
        attractions=get_attractions("a.DestinationID = %s", params),
        culture=get_culture("c.DestinationID = %s", params),
        specialities=get_specialities("s.DestinationID = %s", params),
        businesses=get_businesses("b.DestinationID = %s", params),
        related=related)


@app.route("/attractions")
@login_required
def attractions():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    state = request.args.get("state", "").strip()
    destination_id = request.args.get("destination", type=int)

    conditions, params = [], []
    if q:
        conditions.append(
            "(a.Name LIKE %s OR a.Category LIKE %s OR d.Name LIKE %s OR d.State LIKE %s)")
        params += ["%" + q + "%"] * 4
    if category:
        conditions.append("a.Category = %s")
        params.append(category)
    if state:
        conditions.append("d.State = %s")
        params.append(state)
    if destination_id:
        conditions.append("a.DestinationID = %s")
        params.append(destination_id)

    return render_template(
        "attractions.html",
        attractions=get_attractions(" AND ".join(conditions), params),
        destinations=destination_choices(), categories=CATEGORIES,
        states=state_choices(),
        q=q, category=category, state=state, destination_id=destination_id)


@app.route("/attraction/<int:attraction_id>")
@login_required
def attraction_detail(attraction_id):
    found = get_attractions("a.AttractionID = %s", (attraction_id,))
    if not found:
        abort(404)
    attraction = found[0]
    reviews = fetch_all(
        """SELECT r.ReviewID, r.UserID, r.Rating, r.Comment, r.`Timestamp`, u.Username
           FROM Reviews r JOIN Users u ON u.UserID = r.UserID
           WHERE r.AttractionID = %s ORDER BY r.`Timestamp` DESC, r.ReviewID DESC""",
        (attraction_id,))
    my_review = None
    if "user_id" in session:
        my_review = fetch_one(
            "SELECT Rating, Comment FROM Reviews WHERE UserID = %s AND AttractionID = %s",
            (session["user_id"], attraction_id))
    culture = get_culture("c.DestinationID = %s", (attraction["DestinationID"],), limit=3)
    specialities = get_specialities("s.DestinationID = %s", (attraction["DestinationID"],), limit=4)
    related = get_attractions(
        "a.DestinationID = %s AND a.AttractionID <> %s",
        (attraction["DestinationID"], attraction_id), limit=3)
    return render_template(
        "attraction_detail.html", attraction=attraction, reviews=reviews,
        my_review=my_review, related=related, culture=culture, specialities=specialities)


@app.route("/culture")
@login_required
def culture():
    kind = request.args.get("type", "").strip()
    state = request.args.get("state", "").strip()
    conditions, params = [], []
    if kind:
        conditions.append("c.ItemType = %s")
        params.append(kind)
    if state:
        conditions.append("d.State = %s")
        params.append(state)
    return render_template(
        "culture.html",
        items=get_culture(" AND ".join(conditions), params),
        kind=kind, state=state, types=CULTURE_TYPES, states=state_choices())


@app.route("/culture/<int:culture_id>")
@login_required
def culture_detail(culture_id):
    found = get_culture("c.CultureID = %s", (culture_id,))
    if not found:
        abort(404)
    item = found[0]
    related = get_culture(
        "c.DestinationID = %s AND c.CultureID <> %s",
        (item["DestinationID"], culture_id), limit=3)
    return render_template("culture_detail.html", item=item, related=related)


@app.route("/specialities")
@login_required
def specialities():
    kind = request.args.get("type", "").strip()
    state = request.args.get("state", "").strip()
    conditions, params = [], []
    if kind in SPECIALITY_TYPES:
        conditions.append("s.SpecialityType = %s")
        params.append(kind)
    else:
        kind = ""
    if state:
        conditions.append("d.State = %s")
        params.append(state)
    return render_template(
        "specialities.html", items=get_specialities(" AND ".join(conditions), params),
        kind=kind, state=state, states=state_choices())


@app.route("/speciality/<int:speciality_id>")
@login_required
def speciality_detail(speciality_id):
    found = get_specialities("s.SpecialityID = %s", (speciality_id,))
    if not found:
        abort(404)
    item = found[0]
    related = get_specialities(
        "s.SpecialityType = %s AND s.SpecialityID <> %s",
        (item["SpecialityType"], speciality_id), limit=3)
    return render_template("speciality_detail.html", item=item, related=related)


@app.route("/businesses")
@login_required
def businesses():
    kind = request.args.get("type", "").strip()
    state = request.args.get("state", "").strip()
    conditions, params = [], []
    if kind in BUSINESS_TYPES:
        conditions.append("b.BusinessType = %s")
        params.append(kind)
    else:
        kind = ""
    if state:
        conditions.append("d.State = %s")
        params.append(state)
    return render_template(
        "businesses.html", items=get_businesses(" AND ".join(conditions), params),
        kind=kind, state=state, business_types=BUSINESS_TYPES, states=state_choices())


@app.route("/reviews")
@login_required
def reviews():
    rating = request.args.get("rating", type=int)
    sql = """SELECT r.ReviewID, r.Rating, r.Comment, r.`Timestamp`, u.Username,
                    a.AttractionID, a.Name AS AttractionName, a.ImageURL
             FROM Reviews r
             JOIN Users u ON u.UserID = r.UserID
             JOIN Attractions a ON a.AttractionID = r.AttractionID"""
    params = ()
    if rating in (1, 2, 3, 4, 5):
        sql += " WHERE r.Rating = %s"
        params = (rating,)
    else:
        rating = None
    sql += " ORDER BY r.`Timestamp` DESC, r.ReviewID DESC"
    return render_template("reviews.html", reviews=fetch_all(sql, params), rating=rating)


@app.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    results, total = None, 0
    if q or category:
        like = "%" + (q or category) + "%"
        dest_where, dest_params = [], []
        attr_where, attr_params = [], []
        if q:
            dest_where.append("(d.Name LIKE %s OR d.State LIKE %s OR d.Region LIKE %s OR d.Category LIKE %s)")
            dest_params += [like] * 4
            attr_where.append(
                "(a.Name LIKE %s OR a.Category LIKE %s OR d.Name LIKE %s OR d.State LIKE %s)")
            attr_params += [like] * 4
        if category:
            dest_where.append("d.Category = %s")
            dest_params.append(category)
            attr_where.append("a.Category = %s")
            attr_params.append(category)
        results = {
            "destinations": get_destinations(" AND ".join(dest_where), dest_params),
            "attractions": get_attractions(" AND ".join(attr_where), attr_params),
            "culture": get_culture(
                "(c.Title LIKE %s OR c.ItemType LIKE %s OR d.State LIKE %s)", (like, like, like)),
            "specialities": get_specialities(
                "(s.Name LIKE %s OR s.SpecialityType LIKE %s OR d.State LIKE %s)",
                (like, like, like)),
            "businesses": get_businesses(
                "(b.Name LIKE %s OR b.BusinessType LIKE %s OR d.State LIKE %s OR d.Name LIKE %s)",
                (like, like, like, like)),
        }
        if not q and category:
            results["culture"] = []
            results["specialities"] = []
            results["businesses"] = []
        total = sum(len(rows) for rows in results.values())
    return render_template(
       "search_results.html", q=q, category=category, results=results, total=total,
        categories=CATEGORIES)

@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        language = request.form.get("language", "en")
        taken = fetch_one(
            "SELECT UserID FROM Users WHERE Username = %s AND UserID <> %s",
            (username, session["user_id"]))
        if not 3 <= len(username) <= 50:
            flash("Username must be 3 to 50 characters long.", "error")
        elif language not in LANGUAGES:
            flash("Please choose a valid language.", "error")
        elif taken:
            flash("This username is already taken.", "error")
        else:
            execute("UPDATE Users SET Username = %s, PreferredLanguage = %s WHERE UserID = %s",
                    (username, language, session["user_id"]))
            session["username"], session["lang"] = username, language
            flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    user = fetch_one("SELECT UserID, Username, Email, Role, PreferredLanguage "
                     "FROM Users WHERE UserID = %s", (session["user_id"],))
    my_reviews = fetch_all(
        """SELECT r.ReviewID, r.Rating, r.Comment, r.`Timestamp`,
                  a.AttractionID, a.Name AS AttractionName, a.ImageURL
           FROM Reviews r JOIN Attractions a ON a.AttractionID = r.AttractionID
           WHERE r.UserID = %s ORDER BY r.`Timestamp` DESC""", (session["user_id"],))
    return render_template("profile.html", user=user, my_reviews=my_reviews)


# ---------------------------------------------------------------
# 7. Reviews
# ---------------------------------------------------------------
@app.route("/attraction/<int:attraction_id>/review", methods=["POST"])
@login_required
def add_review(attraction_id):
    if not fetch_one("SELECT AttractionID FROM Attractions WHERE AttractionID = %s",
                     (attraction_id,)):
        abort(404)
    back = url_for("attraction_detail", attraction_id=attraction_id) + "#reviews"
    try:
        rating = int(request.form.get("rating", ""))
    except ValueError:
        rating = 0
    comment = request.form.get("comment", "").strip()

    if rating < 1 or rating > 5:
        flash("Rating must be a whole number from 1 to 5.", "error")
    elif len(comment) > 1000:
        flash("Comment must be 1000 characters or fewer.", "error")
    else:
        existing = fetch_one(
            "SELECT ReviewID FROM Reviews WHERE UserID = %s AND AttractionID = %s",
            (session["user_id"], attraction_id))
        if existing:
            execute("UPDATE Reviews SET Rating = %s, Comment = %s, `Timestamp` = CURRENT_TIMESTAMP "
                    "WHERE ReviewID = %s", (rating, comment, existing["ReviewID"]))
            flash("Your review has been updated.", "success")
        else:
            execute("INSERT INTO Reviews (UserID, AttractionID, Rating, Comment) "
                    "VALUES (%s, %s, %s, %s)",
                    (session["user_id"], attraction_id, rating, comment))
            flash("Thank you! Your review has been added.", "success")
    return redirect(back)


@app.route("/review/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    review = fetch_one("SELECT ReviewID, UserID FROM Reviews WHERE ReviewID = %s", (review_id,))
    if review is None:
        abort(404)
    if review["UserID"] != session["user_id"] and session.get("role") != "Admin":
        abort(403)
    execute("DELETE FROM Reviews WHERE ReviewID = %s", (review_id,))
    flash("Review deleted.", "success")
    return redirect(safe_target(request.form.get("next"), url_for("profile")))


# ---------------------------------------------------------------
# 8. Admin dashboard and CRUD
# ---------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = fetch_one(
        """SELECT (SELECT COUNT(*) FROM Users) AS Users,
                  (SELECT COUNT(*) FROM Destinations) AS Destinations,
                  (SELECT COUNT(*) FROM Attractions) AS Attractions,
                  (SELECT COUNT(*) FROM Reviews) AS Reviews,
                  (SELECT COUNT(*) FROM Businesses) AS Businesses,
                  (SELECT COUNT(*) FROM CultureItems) AS CultureItems,
                  (SELECT COUNT(*) FROM Specialities) AS Specialities""")
    recent_reviews = fetch_all(
        """SELECT r.ReviewID, r.Rating, r.Comment, r.`Timestamp`, u.Username,
                  a.AttractionID, a.Name AS AttractionName
           FROM Reviews r JOIN Users u ON u.UserID = r.UserID
           JOIN Attractions a ON a.AttractionID = r.AttractionID
           ORDER BY r.`Timestamp` DESC, r.ReviewID DESC LIMIT 8""")
    users = fetch_all("SELECT UserID, Username, Email, Role, PreferredLanguage "
                      "FROM Users ORDER BY UserID")
    return render_template("admin_dashboard.html", stats=stats,
                           recent_reviews=recent_reviews, users=users)


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "error")
    else:
        try:
            execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
            flash("User deleted (their reviews were deleted too).", "success")
        except mysql.connector.IntegrityError:
            flash("This user still owns attractions or businesses, so the row cannot be "
                  "deleted (foreign key restriction).", "error")
    return redirect(url_for("admin_dashboard"))


# ----- Destinations -----
@app.route("/admin/destinations")
@admin_required
def admin_destinations():
    return render_template("admin_destinations.html",
                           destinations=get_destinations(order="d.DestinationID"))


def blank_destination_data():
    data = {"name": "", "state": "", "region": "", "category": CATEGORIES[0], "image_url": ""}
    for code in LANGUAGES:
        data["description_" + code] = ""
    return data


def load_destination_data(destination_id):
    row = fetch_one("SELECT * FROM Destinations WHERE DestinationID = %s", (destination_id,))
    if row is None:
        abort(404)
    data = blank_destination_data()
    data.update(name=row["Name"], state=row["State"], region=row["Region"] or "",
                category=row["Category"], image_url=row["ImageURL"] or "")
    for t in fetch_all("SELECT LanguageCode, Description FROM DestinationTranslations "
                       "WHERE DestinationID = %s", (destination_id,)):
        data["description_" + t["LanguageCode"]] = t["Description"]
    return data


def save_destination(destination_id, data):
    db = get_db()
    cursor = db.cursor()
    try:
        image = data["image_url"] or None
        if destination_id is None:
            cursor.execute(
                "INSERT INTO Destinations (Name, State, Region, Category, ImageURL) "
                "VALUES (%s, %s, %s, %s, %s)",
                (data["name"], data["state"], data["region"] or None, data["category"], image))
            destination_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Destinations SET Name = %s, State = %s, Region = %s, "
                "Category = %s, ImageURL = %s WHERE DestinationID = %s",
                (data["name"], data["state"], data["region"] or None,
                 data["category"], image, destination_id))
        for code in LANGUAGES:
            description = data["description_" + code]
            cursor.execute("SELECT TranslationID FROM DestinationTranslations "
                           "WHERE DestinationID = %s AND LanguageCode = %s",
                           (destination_id, code))
            exists = cursor.fetchone()
            if description and exists:
                cursor.execute("UPDATE DestinationTranslations SET Description = %s "
                               "WHERE TranslationID = %s", (description, exists[0]))
            elif description:
                cursor.execute(
                    "INSERT INTO DestinationTranslations (DestinationID, LanguageCode, Description) "
                    "VALUES (%s, %s, %s)", (destination_id, code, description))
            elif exists and code != "en":
                cursor.execute("DELETE FROM DestinationTranslations WHERE TranslationID = %s",
                               (exists[0],))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        raise
    finally:
        cursor.close()


def destination_form(destination_id):
    if request.method == "POST":
        data = blank_destination_data()
        for key in data:
            data[key] = request.form.get(key, "").strip()
        errors = []
        if not data["name"] or len(data["name"]) > 100:
            errors.append("Name is required (maximum 100 characters).")
        if not data["state"] or len(data["state"]) > 50:
            errors.append("State is required.")
        if data["category"] not in CATEGORIES:
            errors.append("Please choose a valid category.")
        if not data["description_en"]:
            errors.append("The English description is required.")
        if not errors:
            save_destination(destination_id, data)
            flash("Destination saved.", "success")
            return redirect(url_for("admin_destinations"))
        for message in errors:
            flash(message, "error")
    elif destination_id is None:
        data = blank_destination_data()
    else:
        data = load_destination_data(destination_id)
    return render_template("admin_destination_form.html", data=data,
                           destination_id=destination_id, categories=CATEGORIES)


@app.route("/admin/destinations/add", methods=["GET", "POST"])
@admin_required
def admin_add_destination():
    return destination_form(None)


@app.route("/admin/destinations/<int:destination_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_destination(destination_id):
    return destination_form(destination_id)


@app.route("/admin/destinations/<int:destination_id>/delete", methods=["POST"])
@admin_required
def admin_delete_destination(destination_id):
    try:
        execute("DELETE FROM Destinations WHERE DestinationID = %s", (destination_id,))
        flash("Destination deleted.", "success")
    except mysql.connector.IntegrityError:
        flash("This destination still has attractions linked to it, so it cannot be deleted.",
              "error")
    return redirect(url_for("admin_destinations"))


# ----- Attractions -----
@app.route("/admin/attractions")
@admin_required
def admin_attractions():
    return render_template("admin_attractions.html",
                           attractions=get_attractions(order="a.AttractionID"))


def blank_attraction_data():
    data = {"name": "", "category": CATEGORIES[0], "latitude": "", "longitude": "",
            "destination_id": "", "image_url": ""}
    for code in LANGUAGES:
        data["description_" + code] = ""
        data["specialities_" + code] = ""
    return data


def load_attraction_data(attraction_id):
    row = fetch_one("SELECT * FROM Attractions WHERE AttractionID = %s", (attraction_id,))
    if row is None:
        abort(404)
    data = blank_attraction_data()
    data.update(name=row["Name"], category=row["Category"], latitude=str(row["Latitude"]),
                longitude=str(row["Longitude"]), destination_id=row["DestinationID"],
                image_url=row["ImageURL"] or "")
    for t in fetch_all("SELECT LanguageCode, Description, LocalSpecialities "
                       "FROM AttractionTranslations WHERE AttractionID = %s", (attraction_id,)):
        data["description_" + t["LanguageCode"]] = t["Description"]
        data["specialities_" + t["LanguageCode"]] = t["LocalSpecialities"] or ""
    return data


def validate_attraction(data):
    errors = []
    if not data["name"] or len(data["name"]) > 150:
        errors.append("Name is required (maximum 150 characters).")
    if data["category"] not in CATEGORIES:
        errors.append("Please choose a valid category.")
    try:
        if not -90 <= float(data["latitude"]) <= 90:
            errors.append("Latitude must be between -90 and 90.")
        if not -180 <= float(data["longitude"]) <= 180:
            errors.append("Longitude must be between -180 and 180.")
    except ValueError:
        errors.append("Latitude and longitude must be numbers.")
    if not fetch_one("SELECT DestinationID FROM Destinations WHERE DestinationID = %s",
                     (data["destination_id"],)):
        errors.append("Please choose a destination.")
    if not data["description_en"]:
        errors.append("The English description is required.")
    return errors


def save_attraction(attraction_id, data):
    db = get_db()
    cursor = db.cursor()
    try:
        image = data["image_url"] or None
        if attraction_id is None:
            cursor.execute(
                "INSERT INTO Attractions (Name, Category, Latitude, Longitude, ImageURL, "
                "DestinationID, CreatorID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (data["name"], data["category"], data["latitude"], data["longitude"],
                 image, data["destination_id"], session["user_id"]))
            attraction_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Attractions SET Name = %s, Category = %s, Latitude = %s, "
                "Longitude = %s, ImageURL = %s, DestinationID = %s WHERE AttractionID = %s",
                (data["name"], data["category"], data["latitude"], data["longitude"],
                 image, data["destination_id"], attraction_id))
        for code in LANGUAGES:
            description = data["description_" + code]
            specialities = data["specialities_" + code] or None
            cursor.execute("SELECT TranslationID FROM AttractionTranslations "
                           "WHERE AttractionID = %s AND LanguageCode = %s", (attraction_id, code))
            exists = cursor.fetchone()
            if description and exists:
                cursor.execute("UPDATE AttractionTranslations SET Description = %s, "
                               "LocalSpecialities = %s WHERE TranslationID = %s",
                               (description, specialities, exists[0]))
            elif description:
                cursor.execute("INSERT INTO AttractionTranslations (AttractionID, LanguageCode, "
                               "Description, LocalSpecialities) VALUES (%s, %s, %s, %s)",
                               (attraction_id, code, description, specialities))
            elif exists and code != "en":
                cursor.execute("DELETE FROM AttractionTranslations WHERE TranslationID = %s",
                               (exists[0],))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        raise
    finally:
        cursor.close()


def attraction_form(attraction_id):
    if request.method == "POST":
        data = blank_attraction_data()
        for key in data:
            data[key] = request.form.get(key, "").strip()
        errors = validate_attraction(data)
        if not errors:
            save_attraction(attraction_id, data)
            flash("Attraction saved.", "success")
            return redirect(url_for("admin_attractions"))
        for message in errors:
            flash(message, "error")
    elif attraction_id is None:
        data = blank_attraction_data()
    else:
        data = load_attraction_data(attraction_id)
    return render_template("admin_attraction_form.html", data=data,
                           attraction_id=attraction_id, categories=CATEGORIES,
                           destinations=destination_choices())


@app.route("/admin/attractions/add", methods=["GET", "POST"])
@admin_required
def admin_add_attraction():
    return attraction_form(None)


@app.route("/admin/attractions/<int:attraction_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_attraction(attraction_id):
    return attraction_form(attraction_id)


@app.route("/admin/attractions/<int:attraction_id>/delete", methods=["POST"])
@admin_required
def admin_delete_attraction(attraction_id):
    execute("DELETE FROM Attractions WHERE AttractionID = %s", (attraction_id,))
    flash("Attraction deleted (its translations and reviews were deleted too).", "success")
    return redirect(url_for("admin_attractions"))


# ----- Culture -----
@app.route("/admin/culture")
@admin_required
def admin_culture():
    return render_template("admin_culture.html", items=get_culture(order="c.CultureID"))


def blank_culture_data():
    data = {"title": "", "item_type": CULTURE_TYPES[0], "destination_id": "", "image_url": ""}
    for code in LANGUAGES:
        data["description_" + code] = ""
    return data


def save_culture(culture_id, data):
    db = get_db()
    cursor = db.cursor()
    try:
        image = data["image_url"] or None
        if culture_id is None:
            cursor.execute(
                "INSERT INTO CultureItems (Title, ItemType, ImageURL, DestinationID) "
                "VALUES (%s, %s, %s, %s)",
                (data["title"], data["item_type"], image, data["destination_id"]))
            culture_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE CultureItems SET Title = %s, ItemType = %s, ImageURL = %s, "
                "DestinationID = %s WHERE CultureID = %s",
                (data["title"], data["item_type"], image, data["destination_id"], culture_id))
        for code in LANGUAGES:
            description = data["description_" + code]
            cursor.execute("SELECT TranslationID FROM CultureTranslations "
                           "WHERE CultureID = %s AND LanguageCode = %s", (culture_id, code))
            exists = cursor.fetchone()
            if description and exists:
                cursor.execute("UPDATE CultureTranslations SET Description = %s "
                               "WHERE TranslationID = %s", (description, exists[0]))
            elif description:
                cursor.execute(
                    "INSERT INTO CultureTranslations (CultureID, LanguageCode, Description) "
                    "VALUES (%s, %s, %s)", (culture_id, code, description))
            elif exists and code != "en":
                cursor.execute("DELETE FROM CultureTranslations WHERE TranslationID = %s",
                               (exists[0],))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        raise
    finally:
        cursor.close()


def culture_form(culture_id):
    if request.method == "POST":
        data = blank_culture_data()
        for key in data:
            data[key] = request.form.get(key, "").strip()
        errors = []
        if not data["title"]:
            errors.append("Title is required.")
        if data["item_type"] not in CULTURE_TYPES:
            errors.append("Please choose a valid type.")
        if not fetch_one("SELECT DestinationID FROM Destinations WHERE DestinationID = %s",
                         (data["destination_id"],)):
            errors.append("Please choose a destination.")
        if not data["description_en"]:
            errors.append("The English description is required.")
        if not errors:
            save_culture(culture_id, data)
            flash("Culture item saved.", "success")
            return redirect(url_for("admin_culture"))
        for message in errors:
            flash(message, "error")
    elif culture_id is None:
        data = blank_culture_data()
    else:
        row = fetch_one("SELECT * FROM CultureItems WHERE CultureID = %s", (culture_id,))
        if row is None:
            abort(404)
        data = blank_culture_data()
        data.update(title=row["Title"], item_type=row["ItemType"],
                    destination_id=row["DestinationID"], image_url=row["ImageURL"] or "")
        for t in fetch_all("SELECT LanguageCode, Description FROM CultureTranslations "
                           "WHERE CultureID = %s", (culture_id,)):
            data["description_" + t["LanguageCode"]] = t["Description"]
    return render_template("admin_culture_form.html", data=data, culture_id=culture_id,
                           types=CULTURE_TYPES, destinations=destination_choices())


@app.route("/admin/culture/add", methods=["GET", "POST"])
@admin_required
def admin_add_culture():
    return culture_form(None)


@app.route("/admin/culture/<int:culture_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_culture(culture_id):
    return culture_form(culture_id)


@app.route("/admin/culture/<int:culture_id>/delete", methods=["POST"])
@admin_required
def admin_delete_culture(culture_id):
    execute("DELETE FROM CultureItems WHERE CultureID = %s", (culture_id,))
    flash("Culture item deleted.", "success")
    return redirect(url_for("admin_culture"))


# ----- Specialities -----
@app.route("/admin/specialities")
@admin_required
def admin_specialities():
    return render_template("admin_specialities.html",
                           items=get_specialities(order="s.SpecialityID"))


def blank_speciality_data():
    data = {"name": "", "speciality_type": "Food", "destination_id": "", "image_url": ""}
    for code in LANGUAGES:
        data["description_" + code] = ""
    return data


def save_speciality(speciality_id, data):
    db = get_db()
    cursor = db.cursor()
    try:
        image = data["image_url"] or None
        if speciality_id is None:
            cursor.execute(
                "INSERT INTO Specialities (Name, SpecialityType, ImageURL, DestinationID) "
                "VALUES (%s, %s, %s, %s)",
                (data["name"], data["speciality_type"], image, data["destination_id"]))
            speciality_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Specialities SET Name = %s, SpecialityType = %s, ImageURL = %s, "
                "DestinationID = %s WHERE SpecialityID = %s",
                (data["name"], data["speciality_type"], image, data["destination_id"],
                 speciality_id))
        for code in LANGUAGES:
            description = data["description_" + code]
            cursor.execute("SELECT TranslationID FROM SpecialityTranslations "
                           "WHERE SpecialityID = %s AND LanguageCode = %s",
                           (speciality_id, code))
            exists = cursor.fetchone()
            if description and exists:
                cursor.execute("UPDATE SpecialityTranslations SET Description = %s "
                               "WHERE TranslationID = %s", (description, exists[0]))
            elif description:
                cursor.execute(
                    "INSERT INTO SpecialityTranslations (SpecialityID, LanguageCode, Description) "
                    "VALUES (%s, %s, %s)", (speciality_id, code, description))
            elif exists and code != "en":
                cursor.execute("DELETE FROM SpecialityTranslations WHERE TranslationID = %s",
                               (exists[0],))
        db.commit()
    except mysql.connector.Error:
        db.rollback()
        raise
    finally:
        cursor.close()


def speciality_form(speciality_id):
    if request.method == "POST":
        data = blank_speciality_data()
        for key in data:
            data[key] = request.form.get(key, "").strip()
        errors = []
        if not data["name"]:
            errors.append("Name is required.")
        if data["speciality_type"] not in SPECIALITY_TYPES:
            errors.append("Please choose Food or Craft.")
        if not fetch_one("SELECT DestinationID FROM Destinations WHERE DestinationID = %s",
                         (data["destination_id"],)):
            errors.append("Please choose a destination.")
        if not data["description_en"]:
            errors.append("The English description is required.")
        if not errors:
            save_speciality(speciality_id, data)
            flash("Speciality saved.", "success")
            return redirect(url_for("admin_specialities"))
        for message in errors:
            flash(message, "error")
    elif speciality_id is None:
        data = blank_speciality_data()
    else:
        row = fetch_one("SELECT * FROM Specialities WHERE SpecialityID = %s", (speciality_id,))
        if row is None:
            abort(404)
        data = blank_speciality_data()
        data.update(name=row["Name"], speciality_type=row["SpecialityType"],
                    destination_id=row["DestinationID"], image_url=row["ImageURL"] or "")
        for t in fetch_all("SELECT LanguageCode, Description FROM SpecialityTranslations "
                           "WHERE SpecialityID = %s", (speciality_id,)):
            data["description_" + t["LanguageCode"]] = t["Description"]
    return render_template("admin_speciality_form.html", data=data,
                           speciality_id=speciality_id, types=SPECIALITY_TYPES,
                           destinations=destination_choices())


@app.route("/admin/specialities/add", methods=["GET", "POST"])
@admin_required
def admin_add_speciality():
    return speciality_form(None)


@app.route("/admin/specialities/<int:speciality_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_speciality(speciality_id):
    return speciality_form(speciality_id)


@app.route("/admin/specialities/<int:speciality_id>/delete", methods=["POST"])
@admin_required
def admin_delete_speciality(speciality_id):
    execute("DELETE FROM Specialities WHERE SpecialityID = %s", (speciality_id,))
    flash("Speciality deleted.", "success")
    return redirect(url_for("admin_specialities"))


# ----- Businesses -----
@app.route("/admin/businesses")
@admin_required
def admin_businesses():
    return render_template("admin_businesses.html",
                           businesses=get_businesses(order="b.BusinessID"))


BUSINESS_FIELDS = ["name", "business_type", "address", "phone", "description",
                   "image_url", "destination_id", "owner_id"]


def business_form(business_id):
    if request.method == "POST":
        data = {key: request.form.get(key, "").strip() for key in BUSINESS_FIELDS}
        errors = []
        if not data["name"] or len(data["name"]) > 150:
            errors.append("Name is required (maximum 150 characters).")
        if data["business_type"] not in BUSINESS_TYPES:
            errors.append("Please choose a valid business type.")
        if not data["address"] or len(data["address"]) > 200:
            errors.append("Address is required (maximum 200 characters).")
        if data["phone"] and not PHONE_PATTERN.match(data["phone"]):
            errors.append("Phone may contain only digits, spaces, + and - (7 to 20 characters).")
        if not fetch_one("SELECT DestinationID FROM Destinations WHERE DestinationID = %s",
                         (data["destination_id"],)):
            errors.append("Please choose a destination.")
        if not fetch_one("SELECT UserID FROM Users WHERE UserID = %s AND Role IN ('Business', 'Admin')",
                         (data["owner_id"],)):
            errors.append("Please choose a valid owner (Business or Admin user).")
        if not errors:
            values = (data["name"], data["business_type"], data["address"], data["phone"] or None,
                      data["description"] or None, data["image_url"] or None,
                      data["destination_id"], data["owner_id"])
            if business_id is None:
                execute("INSERT INTO Businesses (Name, BusinessType, Address, Phone, Description, "
                        "ImageURL, DestinationID, OwnerID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        values)
            else:
                execute("UPDATE Businesses SET Name = %s, BusinessType = %s, Address = %s, "
                        "Phone = %s, Description = %s, ImageURL = %s, DestinationID = %s, "
                        "OwnerID = %s WHERE BusinessID = %s", values + (business_id,))
            flash("Business saved.", "success")
            return redirect(url_for("admin_businesses"))
        for message in errors:
            flash(message, "error")
    elif business_id is None:
        data = {key: "" for key in BUSINESS_FIELDS}
        data["business_type"] = BUSINESS_TYPES[0]
    else:
        row = fetch_one("SELECT * FROM Businesses WHERE BusinessID = %s", (business_id,))
        if row is None:
            abort(404)
        data = {"name": row["Name"], "business_type": row["BusinessType"],
                "address": row["Address"], "phone": row["Phone"] or "",
                "description": row["Description"] or "", "image_url": row["ImageURL"] or "",
                "destination_id": row["DestinationID"], "owner_id": row["OwnerID"]}
    owners = fetch_all("SELECT UserID, Username FROM Users "
                       "WHERE Role IN ('Business', 'Admin') ORDER BY Username")
    return render_template("admin_business_form.html", data=data, business_id=business_id,
                           business_types=BUSINESS_TYPES, owners=owners,
                           destinations=destination_choices())


@app.route("/admin/businesses/add", methods=["GET", "POST"])
@admin_required
def admin_add_business():
    return business_form(None)


@app.route("/admin/businesses/<int:business_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_business(business_id):
    return business_form(business_id)


@app.route("/admin/businesses/<int:business_id>/delete", methods=["POST"])
@admin_required
def admin_delete_business(business_id):
    execute("DELETE FROM Businesses WHERE BusinessID = %s", (business_id,))
    flash("Business deleted.", "success")
    return redirect(url_for("admin_businesses"))


# ---------------------------------------------------------------
# 9. Error pages
# ---------------------------------------------------------------
def show_error(code, title, message):
    return render_template("error.html", code=code, title=title, message=message), code


@app.errorhandler(403)
def forbidden(error):
    return show_error(403, "Access denied", "You do not have permission to open this page.")


@app.errorhandler(404)
def not_found(error):
    return show_error(404, "Page not found", "The page you are looking for does not exist.")


@app.errorhandler(mysql.connector.Error)
def database_error(error):
    app.logger.error("Database error: %s", error)
    return show_error(500, "Database problem",
                      "The database could not complete this request. Check that MySQL is "
                      "running and that database.sql has been imported.")


@app.errorhandler(500)
def server_error(error):
    return show_error(500, "Something went wrong", "An unexpected error occurred. Please try again.")


if __name__ == "__main__":
    app.run(debug=True)
