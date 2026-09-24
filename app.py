from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "servicenow-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///servicenow.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# USER TABLE
# =========================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    employment_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


# =========================
# TICKET TABLE
# =========================

class Ticket(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    ticket_type = db.Column(
        db.String(20),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    short_description = db.Column(
        db.String(500),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    state = db.Column(
        db.String(50),
        nullable=True
    )

    priority = db.Column(
        db.String(50),
        nullable=True
    )

    caller = db.Column(
        db.String(100),
        nullable=True
    )

    requested_for = db.Column(
        db.String(100),
        nullable=True
    )

    location = db.Column(
        db.String(150),
        nullable=True
    )

    contact_type = db.Column(
        db.String(100),
        nullable=True
    )

    subcategory = db.Column(
        db.String(100),
        nullable=True
    )

    assignment_group = db.Column(
        db.String(150),
        nullable=True
    )

    configuration_item = db.Column(
        db.String(150),
        nullable=True
    )

    assigned_to = db.Column(
        db.String(100),
        nullable=True
    )

    impact = db.Column(
        db.String(20),
        nullable=True
    )

    urgency = db.Column(
        db.String(20),
        nullable=True
    )

    service = db.Column(
        db.String(150),
        nullable=True
    )

    additional_comments = db.Column(
        db.Text,
        nullable=True
    )

    work_notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        employment_number = request.form["employment_number"]

        password = request.form["password"]

        user = User.query.filter_by(
            employment_number=employment_number
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id

            session["employment_number"] = (
                user.employment_number
            )

            session["full_name"] = user.full_name

            return redirect(
                url_for("dashboard")
            )

        return "Invalid employment number or password."

    return render_template(
        "login.html"
    )


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        employment_number = request.form[
            "employment_number"
        ]

        full_name = request.form[
            "full_name"
        ]

        email = request.form[
            "email"
        ]

        password = request.form[
            "password"
        ]

        confirm_password = request.form[
            "confirm_password"
        ]

        if password != confirm_password:

            return "Passwords do not match."

        existing_user = User.query.filter_by(
            employment_number=employment_number
        ).first()

        if existing_user:

            return "Employment number already exists."

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            return "Email address already exists."

        hashed_password = generate_password_hash(
            password
        )

        new_user = User(

            employment_number=employment_number,

            full_name=full_name,

            email=email,

            password=hashed_password

        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    total_tickets = Ticket.query.filter_by(
        user_id=user_id
    ).count()

    open_tickets = Ticket.query.filter(
        Ticket.user_id == user_id,
        Ticket.state.in_([
            "New",
            "Open",
            "In Progress",
            "On Hold"
        ])
    ).count()

    resolved_tickets = Ticket.query.filter_by(
        user_id=user_id,
        state="Resolved"
    ).count()

    closed_tickets = Ticket.query.filter_by(
        user_id=user_id,
        state="Closed"
    ).count()

    recent_tickets = Ticket.query.filter_by(
        user_id=user_id
    ).order_by(
        Ticket.id.desc()
    ).limit(5).all()

    return render_template(
        "dashboard.html",
        full_name=session["full_name"],
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        closed_tickets=closed_tickets,
        recent_tickets=recent_tickets
    )


# =========================
# GENERATE TICKET NUMBER
# =========================

def generate_ticket_number(ticket_type):

    if ticket_type == "Incident":

        prefix = "INC"

    else:

        prefix = "REQ"

    last_ticket = Ticket.query.filter_by(
        ticket_type=ticket_type
    ).order_by(
        Ticket.id.desc()
    ).first()

    if last_ticket:

        try:

            last_number = int(
                last_ticket.ticket_number.replace(
                    prefix,
                    ""
                )
            )

        except ValueError:

            last_number = 0

    else:

        if ticket_type == "Incident":

            last_number = 11210

        else:

            last_number = 10000

    new_number = last_number + 1

    return f"{prefix}{new_number:07d}"


# =========================
# CALCULATE PRIORITY
# =========================

def calculate_priority(impact, urgency):

    if not impact or not urgency:

        return "-"

    try:

        i = int(impact)

        u = int(urgency)

        total = i + u

        if total <= 2:

            return "1 - Critical"

        elif total <= 4:

            return "2 - High"

        elif total <= 5:

            return "3 - Moderate"

        else:

            return "4 - Low"

    except ValueError:

        return "-"


# =========================
# INCIDENT
# =========================

@app.route("/incident", methods=["GET", "POST"])
def incident():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        impact = request.form.get(
            "impact",
            ""
        )

        urgency = request.form.get(
            "urgency",
            ""
        )

        priority = calculate_priority(
            impact,
            urgency
        )

        new_ticket = Ticket(

            ticket_number=generate_ticket_number(
                "Incident"
            ),

            ticket_type="Incident",

            user_id=session["user_id"],

            short_description=request.form.get(
                "short_description",
                ""
            ),

            description=request.form.get(
                "description",
                ""
            ),

            category=request.form.get(
                "category",
                ""
            ),

            state=request.form.get(
                "state",
                "New"
            ),

            priority=priority,

            caller=request.form.get(
                "caller",
                session["full_name"]
            ),

            location=request.form.get(
                "location",
                ""
            ),

            contact_type=request.form.get(
                "contact_type",
                ""
            ),

            subcategory=request.form.get(
                "subcategory",
                ""
            ),

            assignment_group=request.form.get(
                "assignment_group",
                ""
            ),

            configuration_item=request.form.get(
                "configuration_item",
                ""
            ),

            assigned_to=request.form.get(
                "assigned_to",
                ""
            ),

            impact=impact,

            urgency=urgency,

            additional_comments=request.form.get(
                "additional_comments",
                ""
            ),

            work_notes=request.form.get(
                "work_notes",
                ""
            )

        )

        db.session.add(new_ticket)

        db.session.commit()

        return redirect(
            url_for("ticket_list")
        )

    return render_template(
        "incident.html",
        full_name=session["full_name"]
    )


# =========================
# REQUEST
# =========================

@app.route("/request", methods=["GET", "POST"])
def service_request():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        new_ticket = Ticket(

            ticket_number=generate_ticket_number(
                "Request"
            ),

            ticket_type="Request",

            user_id=session["user_id"],

            short_description=request.form.get(
                "short_description",
                ""
            ),

            description=request.form.get(
                "description",
                ""
            ),

            category=request.form.get(
                "category",
                ""
            ),

            state=request.form.get(
                "state",
                "Open"
            ),

            priority=request.form.get(
                "priority",
                "-"
            ),

            requested_for=request.form.get(
                "requested_for",
                session["full_name"]
            ),

            location=request.form.get(
                "location",
                ""
            ),

            service=request.form.get(
                "service",
                ""
            ),

            assignment_group=request.form.get(
                "assignment_group",
                ""
            ),

            assigned_to=request.form.get(
                "assigned_to",
                ""
            ),

            additional_comments=request.form.get(
                "additional_comments",
                ""
            )

        )

        db.session.add(new_ticket)

        db.session.commit()

        return redirect(
            url_for("ticket_list")
        )

    return render_template(
        "request.html",
        full_name=session["full_name"]
    )


# =========================
# TICKET LIST
# =========================

@app.route("/tickets")
def ticket_list():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    tickets = Ticket.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Ticket.id.desc()
    ).all()

    return render_template(
        "tickets.html",
        tickets=tickets,
        full_name=session["full_name"]
    )


# =========================
# TICKET DETAIL
# =========================

@app.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ticket = Ticket.query.filter_by(
        id=ticket_id,
        user_id=session["user_id"]
    ).first_or_404()

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        full_name=session["full_name"]
    )


# =========================
# UPDATE TICKET
# =========================

@app.route(
    "/ticket/<int:ticket_id>/update",
    methods=["POST"]
)
def update_ticket(ticket_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ticket = Ticket.query.filter_by(
        id=ticket_id,
        user_id=session["user_id"]
    ).first_or_404()

    ticket.short_description = request.form.get(
        "short_description",
        ticket.short_description
    )

    ticket.description = request.form.get(
        "description",
        ticket.description
    )

    ticket.category = request.form.get(
        "category",
        ticket.category
    )

    ticket.state = request.form.get(
        "state",
        ticket.state
    )

    ticket.priority = request.form.get(
        "priority",
        ticket.priority
    )

    ticket.location = request.form.get(
        "location",
        ticket.location
    )

    ticket.assignment_group = request.form.get(
        "assignment_group",
        ticket.assignment_group
    )

    ticket.assigned_to = request.form.get(
        "assigned_to",
        ticket.assigned_to
    )

    ticket.additional_comments = request.form.get(
        "additional_comments",
        ticket.additional_comments
    )

    ticket.work_notes = request.form.get(
        "work_notes",
        ticket.work_notes
    )

    db.session.commit()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket.id
        )
    )


# =========================
# RESOLVE TICKET
# =========================

@app.route(
    "/ticket/<int:ticket_id>/resolve",
    methods=["POST"]
)
def resolve_ticket(ticket_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ticket = Ticket.query.filter_by(
        id=ticket_id,
        user_id=session["user_id"]
    ).first_or_404()

    if ticket.ticket_type == "Incident":

        ticket.state = "Resolved"

        db.session.commit()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket.id
        )
    )


# =========================
# CLOSE TICKET
# =========================

@app.route(
    "/ticket/<int:ticket_id>/close",
    methods=["POST"]
)
def close_ticket(ticket_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ticket = Ticket.query.filter_by(
        id=ticket_id,
        user_id=session["user_id"]
    ).first_or_404()

    ticket.state = "Closed"

    db.session.commit()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket.id
        )
    )


# =========================
# REOPEN TICKET
# =========================

@app.route(
    "/ticket/<int:ticket_id>/reopen",
    methods=["POST"]
)
def reopen_ticket(ticket_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    ticket = Ticket.query.filter_by(
        id=ticket_id,
        user_id=session["user_id"]
    ).first_or_404()

    ticket.state = "In Progress"

    db.session.commit()

    return redirect(
        url_for(
            "ticket_detail",
            ticket_id=ticket.id
        )
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)