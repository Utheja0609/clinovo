from flask import Blueprint, render_template, redirect, url_for, session, flash
from routes.auth import login_required
import json
# Import the calculation function so we can provide fallback Jinja data
from routes.dashboard import calculate_site_scores_from_db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin-dashboard")
@login_required
def admin_dashboard():
    user_type = str(session.get("user_type", "")).strip().lower()
    if user_type not in ["admin", "administrator"]:
        flash("Access restricted to administrators only.", "warning")
        return redirect(url_for("auth.home"))

    scores = calculate_site_scores_from_db()
    return render_template("dashboard.html", db_sites_data=json.dumps(scores))