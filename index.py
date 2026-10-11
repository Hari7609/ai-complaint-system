import streamlit as st
import requests
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Complaint Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    padding-top: 1rem;
}

.hero {
    padding: 30px;
    border-radius: 22px;
    margin-bottom: 25px;
    background:
        linear-gradient(
            135deg,
            rgba(38, 50, 80, 0.95),
            rgba(20, 80, 100, 0.90)
        );
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow:
        0 15px 40px rgba(0,0,0,0.25);
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 5px;
}

.hero-subtitle {
    font-size: 16px;
    opacity: 0.80;
}

.card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.20);
    background: rgba(128,128,128,0.06);
    margin-bottom: 18px;
}

.metric-card {
    padding: 20px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid rgba(128,128,128,0.20);
    background: rgba(128,128,128,0.06);
}

.metric-number {
    font-size: 32px;
    font-weight: 800;
}

.metric-label {
    font-size: 13px;
    opacity: 0.70;
}

.ticket {
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.20);
    margin-bottom: 15px;
}

.ticket-id {
    font-size: 20px;
    font-weight: 800;
}

.ai-box {
    padding: 18px;
    border-radius: 16px;
    background: rgba(0, 180, 150, 0.08);
    border: 1px solid rgba(0, 180, 150, 0.25);
}

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 5px;
}

.footer {
    text-align: center;
    opacity: 0.55;
    margin-top: 40px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "language" not in st.session_state:
    st.session_state.language = "English"

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False


# ============================================================
# LANGUAGE
# ============================================================

language = st.sidebar.selectbox(
    "🌐 Language",
    ["English", "தமிழ்"]
)

st.session_state.language = language


def t(english, tamil):

    if st.session_state.language == "தமிழ்":
        return tamil

    return english


# ============================================================
# API FUNCTIONS
# ============================================================

def get_complaints():

    try:

        response = requests.get(
            f"{BACKEND_URL}/complaints/",
            timeout=5
        )

        if response.status_code == 200:

            return response.json()

    except Exception:

        return []

    return []


def submit_complaint(
    name,
    email,
    category,
    text
):

    try:

        response = requests.post(

            f"{BACKEND_URL}/complaints/",

            json={
                "name": name,
                "email": email,
                "category": category,
                "text": text
            },

            timeout=60
        )

        if response.status_code == 200:

            return True, response.json()

        try:
            message = response.json().get(
                "detail",
                "Unable to submit complaint."
            )
        except:
            message = "Unable to submit complaint."

        return False, message

    except Exception as e:

        return False, str(e)


def update_status(
    complaint_id,
    status
):

    try:

        response = requests.patch(

            f"{BACKEND_URL}/complaints/{complaint_id}/status",

            json={
                "status": status
            },

            timeout=10
        )

        return response.status_code == 200

    except:

        return False


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🤖 AI Complaint")

st.sidebar.caption(
    t(
        "Intelligent Complaint Management",
        "நுண்ணறிவு புகார் மேலாண்மை"
    )
)

st.sidebar.divider()


page = st.sidebar.radio(

    t("Navigation", "வழிசெலுத்தல்"),

    [
        t("Dashboard", "டாஷ்போர்டு"),
        t("New Complaint", "புதிய புகார்"),
        t("Track Ticket", "டிக்கெட் கண்காணிப்பு"),
        t("Admin Portal", "நிர்வாக போர்டல்")
    ]
)


# ============================================================
# THEME
# ============================================================

theme = st.sidebar.selectbox(
    "🎨 Theme",
    ["System", "Light", "Dark"]
)

if theme == "Dark":

    st.markdown("""
    <style>
    .stApp {
        background: #07111f;
        color: #f1f5f9;
    }
    </style>
    """, unsafe_allow_html=True)

elif theme == "Light":

    st.markdown("""
    <style>
    .stApp {
        background: #f5f7fb;
        color: #111827;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.markdown(f"""
<div class="hero">

<div class="hero-title">
🤖 AI Complaint Intelligence
</div>

<div class="hero-subtitle">
{t(
"Automated complaint analysis, prioritization and solution guidance.",
"தானியங்கி புகார் பகுப்பாய்வு, முன்னுரிமை மற்றும் தீர்வு வழிகாட்டுதல்."
)}
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if page in [
    "Dashboard",
    "டாஷ்போர்டு"
]:

    complaints = get_complaints()

    total = len(complaints)

    critical = len([
        c for c in complaints
        if c.get("priority") == "Critical"
    ])

    open_count = len([
        c for c in complaints
        if c.get("status") != "Resolved"
    ])

    resolved = len([
        c for c in complaints
        if c.get("status") == "Resolved"
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">{total}</div>
            <div class="metric-label">TOTAL COMPLAINTS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">{critical}</div>
            <div class="metric-label">CRITICAL</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">{open_count}</div>
            <div class="metric-label">OPEN</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-card">
            <div class="metric-number">{resolved}</div>
            <div class="metric-label">RESOLVED</div>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")

    st.subheader(
        t(
            "Recent Complaints",
            "சமீபத்திய புகார்கள்"
        )
    )

    if not complaints:

        st.info(
            t(
                "No complaints submitted yet.",
                "இதுவரை புகார்கள் எதுவும் சமர்ப்பிக்கப்படவில்லை."
            )
        )

    else:

        for complaint in complaints[:10]:

            priority = complaint.get(
                "priority",
                "Medium"
            )

            status = complaint.get(
                "status",
                "Unsolved"
            )

            st.markdown(
                f"""
                <div class="ticket">

                <div class="ticket-id">
                🎫 {complaint.get("ticket_id")}
                </div>

                <p>
                <b>{complaint.get("name")}</b>
                </p>

                <p>
                {complaint.get("text")}
                </p>

                <p>
                Category:
                <b>{complaint.get("category")}</b>
                &nbsp;&nbsp;

                Priority:
                <b>{priority}</b>
                &nbsp;&nbsp;

                Status:
                <b>{status}</b>
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# NEW COMPLAINT
# ============================================================

elif page in [
    "New Complaint",
    "புதிய புகார்"
]:

    st.subheader(
        t(
            "Submit a New Complaint",
            "புதிய புகாரை சமர்ப்பிக்கவும்"
        )
    )

    st.write(
        t(
            "Our AI will automatically analyze your complaint.",
            "உங்கள் புகாரை AI தானாக பகுப்பாய்வு செய்யும்."
        )
    )

    with st.form("complaint_form"):

        name = st.text_input(
            t("Full Name", "முழு பெயர்")
        )

        email = st.text_input(
            t("Email Address", "மின்னஞ்சல்")
        )

        category = st.selectbox(

            t("Category", "வகை"),

            [
                "General",
                "Billing",
                "Technical",
                "Security"
            ]
        )

        complaint_text = st.text_area(

            t(
                "Describe your complaint",
                "உங்கள் புகாரை விவரிக்கவும்"
            ),

            height=180,

            placeholder=t(
                "Explain your problem clearly...",
                "உங்கள் பிரச்சனையை தெளிவாக விளக்கவும்..."
            )
        )

        submitted = st.form_submit_button(
            t(
                "🚀 Analyze & Submit Complaint",
                "🚀 பகுப்பாய்வு செய்து சமர்ப்பிக்கவும்"
            ),
            use_container_width=True
        )


    if submitted:

        if not name.strip():

            st.error(
                t(
                    "Please enter your name.",
                    "உங்கள் பெயரை உள்ளிடவும்."
                )
            )

        elif not email.strip():

            st.error(
                t(
                    "Please enter your email.",
                    "உங்கள் மின்னஞ்சலை உள்ளிடவும்."
                )
            )

        elif not complaint_text.strip():

            st.error(
                t(
                    "Please describe your complaint.",
                    "உங்கள் புகாரை விவரிக்கவும்."
                )
            )

        else:

            with st.spinner(
                t(
                    "AI is analyzing your complaint...",
                    "AI உங்கள் புகாரை பகுப்பாய்வு செய்கிறது..."
                )
            ):

                success, result = submit_complaint(

                    name,
                    email,
                    category,
                    complaint_text
                )

            if success:

                st.success(
                    t(
                        "Complaint submitted successfully!",
                        "புகார் வெற்றிகரமாக சமர்ப்பிக்கப்பட்டது!"
                    )
                )

                st.markdown(
                    f"""
                    <div class="ai-box">

                    <h3>🎫 {result["ticket_id"]}</h3>

                    <p>
                    <b>Category:</b>
                    {result["category"]}
                    </p>

                    <p>
                    <b>Priority:</b>
                    {result["priority"]}
                    </p>

                    <p>
                    <b>Sentiment:</b>
                    {result["sentiment"]}
                    </p>

                    <hr>

                    <h4>🤖 AI Solution</h4>

                    <p>
                    {result["summary"]}
                    </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.error(
                    f"Error: {result}"
                )


# ============================================================
# TRACK TICKET
# ============================================================

elif page in [
    "Track Ticket",
    "டிக்கெட் கண்காணிப்பு"
]:

    st.subheader(
        t(
            "Track Your Complaint",
            "உங்கள் புகாரை கண்காணிக்கவும்"
        )
    )

    ticket = st.text_input(
        t(
            "Enter Ticket ID",
            "டிக்கெட் ID-ஐ உள்ளிடவும்"
        ),
        placeholder="CMP-000001"
    )

    if st.button(
        t(
            "🔍 Track Complaint",
            "🔍 புகாரை கண்காணிக்கவும்"
        ),
        use_container_width=True
    ):

        if not ticket.strip():

            st.warning(
                t(
                    "Enter a ticket ID.",
                    "டிக்கெட் ID-ஐ உள்ளிடவும்."
                )
            )

        else:

            try:

                numeric_id = int(
                    ticket.upper()
                    .replace("CMP-", "")
                )

                response = requests.get(

                    f"{BACKEND_URL}/complaints/{numeric_id}",

                    timeout=10
                )

                if response.status_code == 200:

                    complaint = response.json()

                    st.markdown(
                        f"""
                        <div class="card">

                        <h2>
                        🎫 {complaint["ticket_id"]}
                        </h2>

                        <p>
                        <b>Name:</b>
                        {complaint["name"]}
                        </p>

                        <p>
                        <b>Category:</b>
                        {complaint["category"]}
                        </p>

                        <p>
                        <b>Priority:</b>
                        {complaint["priority"]}
                        </p>

                        <p>
                        <b>Status:</b>
                        {complaint["status"]}
                        </p>

                        <p>
                        <b>Complaint:</b>
                        {complaint["text"]}
                        </p>

                        <hr>

                        <div class="ai-box">

                        <h3>🤖 AI Solution</h3>

                        <p>
                        {complaint["summary"]}
                        </p>

                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.error(
                        t(
                            "Ticket not found.",
                            "டிக்கெட் கிடைக்கவில்லை."
                        )
                    )

            except ValueError:

                st.error(
                    t(
                        "Invalid ticket format. Example: CMP-000001",
                        "தவறான டிக்கெட் வடிவம். உதாரணம்: CMP-000001"
                    )
                )


# ============================================================
# ADMIN PORTAL
# ============================================================

elif page in [
    "Admin Portal",
    "நிர்வாக போர்டல்"
]:

    if not st.session_state.admin_logged:

        st.subheader(
            "🔐 Admin Login"
        )

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if (
                username == "ADMIN"
                and
                password == "admin1234"
            ):

                st.session_state.admin_logged = True

                st.success(
                    "Login successful."
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    else:

        col1, col2 = st.columns(
            [5, 1]
        )

        with col1:

            st.subheader(
                "🛡️ Admin Dashboard"
            )

        with col2:

            if st.button(
                "Logout"
            ):

                st.session_state.admin_logged = False

                st.rerun()


        complaints = get_complaints()

        # Metrics

        total = len(complaints)

        light = len([
            c for c in complaints
            if c.get("priority") == "Light"
        ])

        medium = len([
            c for c in complaints
            if c.get("priority") == "Medium"
        ])

        critical = len([
            c for c in complaints
            if c.get("priority") == "Critical"
        ])

        resolved = len([
            c for c in complaints
            if c.get("status") == "Resolved"
        ])

        ongoing = len([
            c for c in complaints
            if c.get("status") == "Ongoing"
        ])

        unsolved = len([
            c for c in complaints
            if c.get("status") == "Unsolved"
        ])


        cols = st.columns(7)

        metrics = [

            ("Total", total),
            ("Light", light),
            ("Medium", medium),
            ("Critical", critical),
            ("Resolved", resolved),
            ("Ongoing", ongoing),
            ("Unsolved", unsolved)

        ]

        for col, (label, value) in zip(
            cols,
            metrics
        ):

            with col:

                st.metric(
                    label,
                    value
                )


        st.divider()


        if not complaints:

            st.info(
                "No complaints available."
            )

        else:

            for complaint in complaints:

                st.markdown(
                    f"""
                    <div class="card">

                    <h3>
                    🎫 {complaint["ticket_id"]}
                    </h3>

                    <p>
                    <b>{complaint["name"]}</b>
                    |
                    {complaint["email"]}
                    </p>

                    <p>
                    <b>Category:</b>
                    {complaint["category"]}
                    </p>

                    <p>
                    <b>Priority:</b>
                    {complaint["priority"]}
                    </p>

                    <p>
                    <b>Complaint:</b>
                    {complaint["text"]}
                    </p>

                    <div class="ai-box">

                    <b>🤖 AI Solution:</b>

                    <br>

                    {complaint["summary"]}

                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                current_status = complaint.get(
                    "status",
                    "Unsolved"
                )

                new_status = st.selectbox(

                    f"Status — {complaint['ticket_id']}",

                    [
                        "Unsolved",
                        "Ongoing",
                        "Resolved"
                    ],

                    index=[
                        "Unsolved",
                        "Ongoing",
                        "Resolved"
                    ].index(current_status),

                    key=f"status_{complaint['id']}"
                )


                if new_status != current_status:

                    if st.button(
                        f"Update {complaint['ticket_id']}",
                        key=f"update_{complaint['id']}"
                    ):

                        if update_status(
                            complaint["id"],
                            new_status
                        ):

                            st.success(
                                "Status updated successfully."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to update status."
                            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
    🤖 AI Complaint Intelligence System
    <br>
    Automated Analysis • Prioritization • Solution Guidance
    </div>
    """,
    unsafe_allow_html=True
) 




#cd "D:\AI Complaint 2"; .\.venv\Scripts\python.exe -m uvicorn backend:app --reload



#cd "D:\AI Complaint 2"; .\.venv\Scripts\python.exe -m streamlit run index.py