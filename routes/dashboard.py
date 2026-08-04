from flask import Blueprint, jsonify, session
import pandas as pd
import MySQLdb.cursors
from app import mysql
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)

def calculate_site_scores_from_db():
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

        # YOUR TEAM'S EXACT LOGIC
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

                if any(inv in question_text for inv in INVERTED_YES_FIELDS):
                    maximum_score += 1
                    if val_str in ['no', '0', 'false']:
                        obtained_score += 1
                elif val_str in ['yes', '1', 'true', 'n/a', 'na']:
                    obtained_score += 1
                    maximum_score += 1
                elif val_str in ['no', '0', 'false']:
                    maximum_score += 1
                elif isinstance(value, str) and value.strip() != "":
                    obtained_score += 1
                    maximum_score += 1
                elif isinstance(value, (int, float)) and value > 0:
                    obtained_score += 1
                    maximum_score += 1

            percentage = round((obtained_score / maximum_score) * 100, 1) if maximum_score > 0 else 0.0

            if site_name not in dashboard_data:
                dashboard_data[site_name] = {}
                
            dashboard_data[site_name][role_name] = percentage

        return dashboard_data
    except Exception as e:
        print(f"[ERROR] Calculation Failed: {e}")
        return {}
    finally:
        cur.close()

@dashboard_bp.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    user_type = str(session.get("user_type", "")).strip().lower()
    if user_type not in ["admin", "administrator"]:
        return jsonify({"error": "Unauthorized access"}), 403

    calculated_scores = calculate_site_scores_from_db()
    return jsonify(calculated_scores)