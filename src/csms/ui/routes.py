
"""Web routes for the CSMS user interface."""

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


main_blueprint = Blueprint("main", __name__)


def get_resident_service():
    """Create the existing Resident service for the application database."""
    repository = ResidentRepository(
        database_file=current_app.config.get("DATABASE")
    )
    validator = ResidentValidator()

    return ResidentService(repository, validator)


@main_blueprint.get("/")
def index() -> str:
    """Display the Sprint 0 welcome page."""
    return render_template(
        "index.html",
        application_name=current_app.config["APP_NAME"],
        application_version=current_app.config["APP_VERSION"],
        current_sprint=current_app.config["CURRENT_SPRINT"],
    )


@main_blueprint.get("/health")
def health():
    """Return a simple application health response."""
    return jsonify(
        {
            "application": current_app.config["APP_NAME"],
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
