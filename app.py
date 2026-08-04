import json
import urllib.parse
import urllib.request
from functools import wraps
import pandas as pd
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)
from werkzeug.security import check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors

from field_mapping import get_field_mapping


# ==========================================================
# FLASK APP & SECRET KEY
# ==========================================================

app = Flask(__name__)
app.secret_key = "clinovo_secret_key"


# ==========================================================
# MYSQL CONFIGURATION
# ==========================================================

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "uthej@123"
app.config["MYSQL_DB"] = "clinovo_assessment"

mysql = MySQL(app)


# ==========================================================
# ROLE ROUTE MAPPING
# ==========================================================

ROLE_ROUTE_MAP = {
    "principal investigator": "principal_investigator",
    "primary contact for site communication": "primary_contact",
    "study coordinator": "study_coordinator",
    "pharmacist": "pharmacist",
    "test article shipment": "test_article_shipment",
    "regulatory manager": "regulatory_manager",
    "central unit manager": "central_unit_manager",
    "data manager": "data_manager",
    "all other regulatory supplies": "all_other_regulatory_supplies",
}


# ==========================================================
# AUTHENTICATION DECORATOR
# ==========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================================
# PANDAS SCORING ALGORITHM (PRESERVED FOR PIE CHARTS)
# ==========================================================

def calculate_site_scores_from_db():
    """
    Fetches user answers from MySQL, executes survey scoring via pandas, 
    and structures flat role percentages for pie chart rendering.
    """
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("""
            SELECT 
                si.site_name,
                r.role_name,
                a.answer,
                q.question_text
            FROM answers a
            JOIN questionnaire_submission qs ON a.submission_id = qs.submission_id
            JOIN site_information si ON qs.site_id = si.site_id
            JOIN roles r ON qs.role_id = r.role_id
            JOIN questions q ON a.question_id = q.question_id
        """)
        rows = cur.fetchall()

        if not rows:
            return {}

        df = pd.DataFrame(rows)

        INVERTED_YES_FIELDS = [
            'additional_training', 'regulatory_inspection', 
            'obstacles', 'training', 'shipment', 'irb_obstacles', 
            'add_committees', 'offsite_longterm_storage', 'q_additional_training',
            'q13_4', 'paper_crf'
        ]

        dashboard_data = {}
        grouped = df.groupby(['site_name', 'role_name'])

        for (site_name, role_name), group in grouped:
            obtained_score = 0
            maximum_score = 0

            for _, row in group.iterrows():
                value = row['answer']
                question_text = str(row['question_text']).lower()

                if pd.isna(value) or str(value).strip() == "":
                    continue

                val_str = str(value).strip().lower()

                # 1. Inverted 'No' Fields
                if any(inv in question_text for inv in INVERTED_YES_FIELDS):
                    maximum_score += 1
                    if val_str in ['no', '0', 'false']:
                        obtained_score += 1

                # 2. Standard Positive Responses
                elif val_str in ['yes', '1', 'true', 'n/a', 'na']:
                    obtained_score += 1
                    maximum_score += 1

                # 3. Standard 'No' Responses
                elif val_str in ['no', '0', 'false']:
                    maximum_score += 1

                # 4. Text/Date Responses
                elif isinstance(value, str) and value.strip() != "":
                    obtained_score += 1
                    maximum_score += 1

                # 5. Non-zero Numbers
                elif isinstance(value, (int, float)) and value > 0:
                    obtained_score += 1
                    maximum_score += 1

            percentage = round((obtained_score / maximum_score) * 100, 1) if maximum_score > 0 else 0.0

            if site_name not in dashboard_data:
                dashboard_data[site_name] = {}
                
            dashboard_data[site_name][role_name] = percentage

        return dashboard_data

    except Exception as e:
        print(f"\n[ERROR] Failed to fetch or process DB scores: {e}\n")
        return {}
    finally:
        cur.close()


# ==========================================================
# REST API ENDPOINTS FOR FRONTEND
# ==========================================================

@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    """API endpoint returning site role scores for pie chart JS script."""
    user_type = str(session.get("user_type", "")).strip().lower()
    if user_type not in ["admin", "administrator"]:
        return jsonify({"error": "Unauthorized access"}), 403

    calculated_scores = calculate_site_scores_from_db()
    return jsonify(calculated_scores)


@app.route("/api/site-locations")
@login_required
def api_site_locations():
    """Separate API endpoint returning site coordinates for Leaflet GIS Map."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("""
            SELECT DISTINCT 
                site_name, official_address, latitude, longitude, city, country 
            FROM site_information
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        locations = cur.fetchall()
        return jsonify(locations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


# ==========================================================
# HOME PAGE & AUTHENTICATION
# ==========================================================

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cur.execute(
            "SELECT * FROM users WHERE username=%s OR email=%s",
            (username, username)
        )
        user = cur.fetchone()

        if user:
            is_password_valid = False
            user_pw = user.get("password", "")
            
            if user_pw.startswith("scrypt:") or user_pw.startswith("pbkdf2:"):
                is_password_valid = check_password_hash(user_pw, password)
            else:
                is_password_valid = (user_pw == password)

            if is_password_valid:
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["user_type"] = user["user_type"]

                user_type_clean = str(user["user_type"]).strip().lower()

                if user_type_clean in ["admin", "administrator"]:
                    return redirect(url_for("admin_dashboard"))

                if user_type_clean in ROLE_ROUTE_MAP:
                    return redirect(url_for(ROLE_ROUTE_MAP[user_type_clean]))

                return redirect(url_for("role_selection"))

        flash("Invalid Username or Password", "danger")
        return redirect(url_for("home"))

    finally:
        cur.close()


@app.route("/admin-dashboard")
@login_required
def admin_dashboard():
    user_type = str(session.get("user_type", "")).strip().lower()
    if user_type not in ["admin", "administrator"]:
        flash("Access restricted to administrators only.", "warning")
        return redirect(url_for("home"))

    calculated_scores = calculate_site_scores_from_db()
    return render_template("dashboard.html", db_sites_data=json.dumps(calculated_scores))


# ==========================================================
# INDIVIDUAL ROLE QUESTIONNAIRE DISPLAY ROUTES
# ==========================================================

@app.route("/principal-investigator")
@login_required
def principal_investigator():
    return render_template("principalInvestigator.html")

@app.route("/primary-contact")
@login_required
def primary_contact():
    return render_template("primaryContact.html")

@app.route("/study-coordinator")
@login_required
def study_coordinator():
    return render_template("studyCoordinator.html")

@app.route("/pharmacist")
@login_required
def pharmacist():
    return render_template("pharmacist.html")

@app.route("/test-article-shipment")
@login_required
def test_article_shipment():
    return render_template("testArticleShipment.html")

@app.route("/regulatory-manager")
@login_required
def regulatory_manager():
    return render_template("regulatoryManager.html")

@app.route("/central-unit-manager")
@login_required
def central_unit_manager():
    return render_template("centralUnitManager.html")

@app.route("/data-manager")
@login_required
def data_manager():
    return render_template("dataManager.html")

@app.route("/all-other-regulatory-supplies")
@login_required
def all_other_regulatory_supplies():
    return render_template("regulatorySupplies.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("home"))


@app.route("/role-selection")
@login_required
def role_selection():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute("SELECT role_id, role_name FROM roles ORDER BY role_id")
        roles = cur.fetchall()
        return render_template("role_selection.html", roles=roles, username=session.get("username"))
    finally:
        cur.close()


@app.route("/select-role", methods=["POST"])
@login_required
def select_role():
    role = request.form.get("role")
    session["selected_role"] = role

    role_pages = {
        "Principal Investigator": "principalInvestigator.html",
        "Primary Contact For Site Communication": "primaryContact.html",
        "Study Coordinator": "studyCoordinator.html",
        "Pharmacist": "pharmacist.html",
        "Test Article Shipment": "testArticleShipment.html",
        "All Other Regulatory Supplies": "regulatorySupplies.html",
        "Regulatory Manager": "regulatoryManager.html",
        "Central Unit Manager": "centralUnitManager.html",
        "Data Manager": "dataManager.html"
    }

    if role not in role_pages:
        flash("Invalid role selected.", "danger")
        return redirect(url_for("role_selection"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        role_id = get_role_id(cur, role)
        return render_template(role_pages[role], role=role, role_id=role_id)
    finally:
        cur.close()


# ==========================================================
# DATABASE HELPER & GEOCODING FUNCTIONS
# ==========================================================

def get_role_id(cur, role_name):
    cur.execute("SELECT role_id FROM roles WHERE role_name=%s", (role_name,))
    result = cur.fetchone()
    return result["role_id"] if result else None


def get_question_mapping(cur, role_id):
    cur.execute(
        "SELECT question_id, question_order FROM questions WHERE role_id=%s ORDER BY question_order",
        (role_id,)
    )
    rows = cur.fetchall()
    return {row["question_order"]: row["question_id"] for row in rows}


def geocode_address_server_side(address_text):
    """
    Enhanced geocoder using OpenStreetMap Nominatim API.
    Attempts strict geocoding first, then cleans company/site codes if failed.
    """
    if not address_text or not str(address_text).strip():
        return None, None, None, None

    raw_str = str(address_text).strip()
    
    cleaned_str = ", ".join([
        part.strip() for part in raw_str.split(',') 
        if not part.strip().isupper() and len(part.strip()) > 2
    ])

    queries_to_try = [raw_str]
    if cleaned_str and cleaned_str != raw_str:
        queries_to_try.append(cleaned_str)

    for q in queries_to_try:
        try:
            url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
                'q': q,
                'format': 'json',
                'limit': 1
            })
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'ClinovoAssessmentApp/1.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    display_parts = data[0].get('display_name', '').split(',')
                    city = display_parts[0].strip() if display_parts else "Clinical Center"
                    country = display_parts[-1].strip() if display_parts else "India"
                    return lat, lon, city, country
        except Exception as e:
            print(f"[GEOCODE WARNING] Failed query '{q}': {e}")

    return None, None, None, None


def save_site_information(cur, form):
    """
    Saves site information along with geocoded coordinates into MySQL.
    Uses strict float parsing to avoid sending empty string values to MySQL DECIMAL columns.
    """
    official_address = form.get("official_address") or ""

    def parse_float(val):
        try:
            return float(val) if val and str(val).strip() != "" else None
        except (ValueError, TypeError):
            return None

    site_lat = parse_float(form.get("site_latitude"))
    site_lng = parse_float(form.get("site_longitude"))
    site_city = form.get("site_city")
    site_country = form.get("site_country")

    # If coordinates are missing from form submission, resolve via server-side geocoder
    if site_lat is None or site_lng is None:
        auto_lat, auto_lng, auto_city, auto_country = geocode_address_server_side(official_address)
        site_lat = site_lat if site_lat is not None else auto_lat
        site_lng = site_lng if site_lng is not None else auto_lng
        site_city = site_city or auto_city or "Hyderabad"
        site_country = site_country or auto_country or "India"

    cur.execute(
        """
        INSERT INTO site_information
        (site_name, official_address, daily_address, overnight_address, phone, fax, email, latitude, longitude, city, country)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            form.get("site_name"),
            official_address,
            form.get("daily_address"),
            form.get("overnight_address"),
            form.get("phone_number"),
            form.get("fax_number"),
            form.get("email_address"),
            site_lat if site_lat is not None else 17.3850,
            site_lng if site_lng is not None else 78.4867,
            site_city or "Hyderabad",
            site_country or "India"
        )
    )
    return cur.lastrowid


def create_submission(cur, user_id, role_id, site_id):
    cur.execute(
        "INSERT INTO questionnaire_submission (user_id, role_id, site_id) VALUES (%s, %s, %s)",
        (user_id, role_id, site_id)
    )
    return cur.lastrowid


def save_answers(cur, submission_id, form, db_questions, field_mapping):
    for field_name, question_order in field_mapping.items():
        question_id = db_questions.get(question_order)
        if not question_id:
            continue

        values = form.getlist(field_name)
        if not values:
            value = form.get(field_name)
            if value:
                values = [value]

        if not values:
            continue

        answer = ", ".join(values)
        cur.execute(
            "INSERT INTO answers (submission_id, question_id, answer) VALUES (%s, %s, %s)",
            (submission_id, question_id, answer)
        )


# ==========================================================
# GENERIC QUESTIONNAIRE SUBMIT ROUTE
# ==========================================================

@app.route("/submit-questionnaire/<role_name>", methods=["POST"])
@login_required
def submit_questionnaire(role_name):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        role_id = get_role_id(cur, role_name)

        if role_id is None:
            flash(f"Role '{role_name}' not found in database.", "danger")
            return redirect(url_for("role_selection"))

        site_id = save_site_information(cur, request.form)

        submission_id = create_submission(
            cur,
            session["user_id"],
            role_id,
            site_id
        )

        db_questions = get_question_mapping(cur, role_id)
        field_mapping = get_field_mapping(role_name)

        if not field_mapping:
            raise ValueError(f"No field mapping defined in field_mapping.py for role: '{role_name}'")

        save_answers(
            cur,
            submission_id,
            request.form,
            db_questions,
            field_mapping
        )

        mysql.connection.commit()

        return render_template(
            "summary.html",
            submission_id=submission_id,
            role=role_name,
            site=request.form.get("site_name")
        )

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Database Error during submission: {e}", "danger")
        return redirect(url_for("role_selection"))

    finally:
        cur.close()


@app.route("/summary")
@login_required
def summary():
    return render_template("summary.html", role=session.get("selected_role"))


if __name__ == "__main__":
    app.run(debug=True)