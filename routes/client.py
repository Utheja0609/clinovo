from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import mysql
from routes.auth import login_required
from models.contact import Contact
from models.response import Response
from models.role import Role
from models.question import Question
from field_mapping import get_field_mapping

client_bp = Blueprint('client', __name__)

# Specific Form Routes
@client_bp.route("/principal-investigator")
@login_required
def principal_investigator(): return render_template("principalInvestigator.html")

@client_bp.route("/primary-contact")
@login_required
def primary_contact(): return render_template("primaryContact.html")

@client_bp.route("/study-coordinator")
@login_required
def study_coordinator(): return render_template("studyCoordinator.html")

@client_bp.route("/pharmacist")
@login_required
def pharmacist(): return render_template("pharmacist.html")

@client_bp.route("/test-article-shipment")
@login_required
def test_article_shipment(): return render_template("testArticleShipment.html")

@client_bp.route("/regulatory-manager")
@login_required
def regulatory_manager(): return render_template("regulatoryManager.html")

@client_bp.route("/central-unit-manager")
@login_required
def central_unit_manager(): return render_template("centralUnitManager.html")

@client_bp.route("/data-manager")
@login_required
def data_manager(): return render_template("dataManager.html")

@client_bp.route("/all-other-regulatory-supplies")
@login_required
def all_other_regulatory_supplies(): return render_template("regulatorySupplies.html")

@client_bp.route("/submit-questionnaire/<role_name>", methods=["POST"])
@login_required
def submit_questionnaire(role_name):
    try:
        role_id = Role.get_id_by_name(mysql, role_name)
        if role_id is None:
            flash(f"Role '{role_name}' not found.", "danger")
            return redirect(url_for("auth.role_selection"))

        site_id = Contact.save_site_info(mysql, request.form)
        submission_id = Response.create_submission(mysql, session["user_id"], role_id, site_id)
        
        db_questions = Question.get_mapping_by_role(mysql, role_id)
        field_mapping = get_field_mapping(role_name)

        Response.save_answers(mysql, submission_id, request.form, db_questions, field_mapping)

        return render_template("summary.html", submission_id=submission_id, role=role_name, site=request.form.get("site_name"))

    except Exception as e:
        flash(f"Database Error: {e}", "danger")
        return redirect(url_for("auth.role_selection"))

@client_bp.route("/summary")
@login_required
def summary():
    return render_template("summary.html", role=session.get("selected_role"))