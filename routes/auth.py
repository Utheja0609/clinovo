from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from app import mysql
from models.user import User
from models.role import Role

auth_bp = Blueprint('auth', __name__)

# Route map points to the 'client' blueprint now
ROLE_ROUTE_MAP = {
    "principal investigator": "client.principal_investigator",
    "primary contact for site communication": "client.primary_contact",
    "study coordinator": "client.study_coordinator",
    "pharmacist": "client.pharmacist",
    "test article shipment": "client.test_article_shipment",
    "regulatory manager": "client.regulatory_manager",
    "central unit manager": "client.central_unit_manager",
    "data manager": "client.data_manager",
    "all other regulatory supplies": "client.all_other_regulatory_supplies",
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.home"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/")
def home():
    if "user_id" in session:
        user_type = str(session.get("user_type", "")).strip().lower()
        if user_type in ["admin", "administrator"]:
            return redirect(url_for("admin.admin_dashboard"))
        elif user_type in ROLE_ROUTE_MAP:
            return redirect(url_for(ROLE_ROUTE_MAP[user_type]))
        return redirect(url_for("auth.role_selection"))
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.get_by_username_or_email(mysql, username)

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
                return redirect(url_for("admin.admin_dashboard"))
            if user_type_clean in ROLE_ROUTE_MAP:
                return redirect(url_for(ROLE_ROUTE_MAP[user_type_clean]))

            return redirect(url_for("auth.role_selection"))

    flash("Invalid Username or Password", "danger")
    return redirect(url_for("auth.home"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.home"))

@auth_bp.route("/role-selection")
@login_required
def role_selection():
    roles = Role.get_all(mysql)
    return render_template("role_selection.html", roles=roles, username=session.get("username"))

@auth_bp.route("/select-role", methods=["POST"])
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
        return redirect(url_for("auth.role_selection"))

    role_id = Role.get_id_by_name(mysql, role)
    return render_template(role_pages[role], role=role, role_id=role_id)