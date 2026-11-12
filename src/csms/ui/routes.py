
"""Web routes for the CSMS user interface."""

from datetime import date

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_service import ResidentService
from csms.services.resident_validator import ResidentValidator
from csms.models.service_request import ServiceRequest
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.request_service import (
    ServiceRequestSubmissionService,
    ServiceRequestStatusService,
)
from csms.services.service_request_query_service import (
    ServiceRequestQueryService,
)
from csms.services.dashboard_service import DashboardService

main_blueprint = Blueprint("main", __name__)


def format_display_date(value):
    """Return an ISO date in a compact human-readable format."""
    try:
        parsed_date = date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return value

    return f"{parsed_date.strftime('%b')} {parsed_date.day}, {parsed_date.year}"


def get_resident_service():
    """Create the existing Resident service for the application database."""
    repository = ResidentRepository(
        database_file=current_app.config.get("DATABASE")
    )
    validator = ResidentValidator()

    return ResidentService(repository, validator)

def get_service_request_repository():
    return ServiceRequestRepository(
        database_file=current_app.config.get("DATABASE")
    )


def get_service_request_query_service():
    return ServiceRequestQueryService(
        get_service_request_repository()
    )


def get_service_request_submission_service():
    return ServiceRequestSubmissionService(
        service_request_repository=get_service_request_repository(),
        resident_repository=ResidentRepository(
            database_file=current_app.config.get("DATABASE")
        ),
    )


def get_service_request_status_service():
    return ServiceRequestStatusService(
        get_service_request_repository()
    )

@main_blueprint.get("/")
def index() -> str:
    """Display the Sprint 0 welcome page."""
    return render_template(
        "index.html",
        application_name=current_app.config["APP_NAME"],
        application_version=current_app.config["APP_VERSION"],
        current_sprint=current_app.config["CURRENT_SPRINT"],
    )

@main_blueprint.get("/dashboard")
def dashboard():
    """Display dashboard summaries and recent Service Requests."""
    dashboard_data = get_dashboard_service().get_dashboard_data()

    return render_template(
        "dashboard.html",
        **dashboard_data,
    )

@main_blueprint.get("/health")
def health():
    """Return a simple application health response."""
    return jsonify(
        {
            "application": "CSMS",
            "name": current_app.config["APP_NAME"],
            "status": "ok",
            "version": current_app.config["APP_VERSION"],
        }
    )


@main_blueprint.get("/residents")
def resident_list():
    """Display and search all residents."""
    service = get_resident_service()
    query = request.args.get("q", "")

    residents = service.search(query)

    return render_template(
        "residents/list.html",
        residents=residents,
        query=query,
    )


@main_blueprint.route(
    "/residents/register",
    methods=["GET", "POST"],
)
def register_resident():
    """Display and process the Resident registration form."""
    if request.method == "POST":
        resident = Resident(
            first_name=request.form.get("first_name", "").strip(),
            last_name=request.form.get("last_name", "").strip(),
            address=request.form.get("address", "").strip(),
            contact_number=request.form.get(
                "contact_number", ""
            ).strip(),
            email=request.form.get("email", "").strip(),
        )

        service = get_resident_service()
        registered, errors = service.register(resident)

        if errors:
            return render_template(
                "residents/form.html",
                title="Register Resident",
                resident=resident,
                errors=errors,
                form_action=url_for("main.register_resident"),
                is_edit=False,
            ), 400

        flash("Resident successfully registered.", "success")
        return redirect(url_for("main.resident_list"))

    resident = Resident("", "", "", "", "")

    return render_template(
        "residents/form.html",
        title="Register Resident",
        resident=resident,
        errors=[],
        form_action=url_for("main.register_resident"),
        is_edit=False,
    )


@main_blueprint.route(
    "/residents/<int:resident_id>/edit",
    methods=["GET", "POST"],
)
def edit_resident(resident_id):
    """Display and process the Resident edit form."""
    service = get_resident_service()
    resident = service.repository.find_by_id(resident_id)

    if resident is None:
        abort(404)

    if request.method == "POST":
        updated, errors = service.update(
            resident_id,
            request.form.get("first_name", "").strip(),
            request.form.get("last_name", "").strip(),
            request.form.get("address", "").strip(),
            request.form.get("contact_number", "").strip(),
            request.form.get("email", "").strip(),
        )

        if errors:
            resident.first_name = request.form.get(
                "first_name", ""
            ).strip()
            resident.last_name = request.form.get(
                "last_name", ""
            ).strip()
            resident.address = request.form.get(
                "address", ""
            ).strip()
            resident.contact_number = request.form.get(
                "contact_number", ""
            ).strip()
            resident.email = request.form.get(
                "email", ""
            ).strip()

            return render_template(
                "residents/form.html",
                title="Edit Resident",
                resident=resident,
                errors=errors,
                form_action=url_for(
                    "main.edit_resident",
                    resident_id=resident_id,
                ),
                is_edit=True,
            ), 400

        flash("Resident information successfully updated.", "success")
        return redirect(url_for("main.resident_list"))

    return render_template(
        "residents/form.html",
        title="Edit Resident",
        resident=resident,
        errors=[],
        form_action=url_for(
            "main.edit_resident",
            resident_id=resident_id,
        ),
        is_edit=True,
    )


@main_blueprint.post("/residents/<int:resident_id>/deactivate")
def deactivate_resident(resident_id):
    """Deactivate an active Resident."""
    service = get_resident_service()
    deactivated, errors = service.deactivate(resident_id)

    if "not_found" in errors:
        abort(404)

    if deactivated.status == "Inactive":
        flash("Resident is now inactive.", "success")

    return redirect(url_for("main.resident_list"))


@main_blueprint.post("/residents/<int:resident_id>/reactivate")
def reactivate_resident(resident_id):
    """Reactivate an inactive Resident."""
    repository = get_resident_service().repository
    connection = repository.get_connection()

    try:
        cursor = connection.execute(
            "UPDATE residents SET status = ? WHERE id = ?",
            ("Active", resident_id),
        )
        connection.commit()
    finally:
        connection.close()

    if cursor.rowcount == 0:
        abort(404)

    flash("Resident is active again.", "success")
    return redirect(url_for("main.resident_list"))

@main_blueprint.get("/service-requests")
def service_requests():
    query = request.args.get("q", "")
    status = request.args.get("status", "")

    try:
        service_requests = get_service_request_query_service().search(
            query=query,
            status=status or None,
        )
    except ValueError:
        abort(400)

    residents = ResidentRepository(
        database_file=current_app.config.get("DATABASE")
    ).find_all()
    resident_names = {
        resident.id: f"{resident.first_name} {resident.last_name}"
        for resident in residents
    }
    display_dates = {
        service_request.id: format_display_date(
            service_request.date_requested
        )
        for service_request in service_requests
    }

    return render_template(
        "service_requests/list.html",
        service_requests=service_requests,
        query=query,
        selected_status=status,
        resident_names=resident_names,
        display_dates=display_dates,
    )

@main_blueprint.route("/service-requests/new", methods=["GET", "POST"])
def new_service_request():
    residents = ResidentRepository(
        database_file=current_app.config.get("DATABASE")
    ).find_all()
    active_residents = [
        resident for resident in residents if resident.status == "Active"
    ]
    values = {
        "resident_id": "",
        "service_type": "",
        "description": "",
        "date_requested": "",
    }
    errors = {}

    if request.method == "POST":
        values = {
            "resident_id": request.form.get("resident_id", "").strip(),
            "service_type": request.form.get("service_type", "").strip(),
            "description": request.form.get("description", "").strip(),
            "date_requested": request.form.get("date_requested", "").strip(),
        }

        try:
            resident_id = int(values["resident_id"])
        except (ValueError, TypeError):
            resident_id = None

        service_request = ServiceRequest(
            resident_id=resident_id,
            service_type=values["service_type"],
            description=values["description"],
            date_requested=values["date_requested"],
        )

        result = get_service_request_submission_service().submit(
            service_request
        )

        if result["success"]:
            saved_request = result["service_request"]
            flash("Service Request submitted successfully.", "success")
            return redirect(
                url_for(
                    "main.service_request_detail",
                    service_request_id=saved_request.id,
                )
            )

        for field in result.get("errors", []):
            if field == "resident_id":
                errors[field] = "Enter a valid positive Resident ID."
            elif field == "service_type":
                errors[field] = "Service Type is required."
            elif field == "description":
                errors[field] = "Description is required."
            elif field == "date_requested":
                errors[field] = "Enter a valid date."
            else:
                errors[field] = "Please check this field."

        reason = result.get("reason")

        if reason == "resident_not_found":
            errors["resident_id"] = "The specified Resident does not exist."
        elif reason == "resident_inactive":
            errors["resident_id"] = (
                "Service Requests can only be submitted for active Residents."
            )

        return render_template(
            "service_requests/form.html",
            values=values,
            errors=errors,
            active_residents=active_residents,
        ), 400

    return render_template(
        "service_requests/form.html",
        values=values,
        errors=errors,
        active_residents=active_residents,
    )

@main_blueprint.get("/service-requests/<int:service_request_id>")
def service_request_detail(service_request_id):
    service_request = get_service_request_query_service().find_by_id(
        service_request_id
    )

    if service_request is None:
        abort(404)

    related_resident = ResidentRepository(
        database_file=current_app.config.get("DATABASE")
    ).find_by_id(service_request.resident_id)

    return render_template(
        "service_requests/detail.html",
        service_request=service_request,
        related_resident=related_resident,
        display_date=format_display_date(service_request.date_requested),
    )

@main_blueprint.post("/service-requests/<int:service_request_id>/status")
def update_service_request_status(service_request_id):
    target_status = request.form.get("status", "").strip()

    result = get_service_request_status_service().update_status(
        service_request_id,
        target_status,
    )

    if not result["success"]:
        if result.get("reason") == "service_request_not_found":
            abort(404)

        flash("That status change is not allowed.", "error")
    else:
        flash("Service Request status updated successfully.", "success")

    return redirect(
        url_for(
            "main.service_request_detail",
            service_request_id=service_request_id,
        )
    )

def get_dashboard_service():
    """Create the Dashboard service for the application database."""
    database_file = current_app.config.get("DATABASE")

    return DashboardService(
        resident_repository=ResidentRepository(
            database_file=database_file
        ),
        service_request_repository=ServiceRequestRepository(
            database_file=database_file
        ),
    )