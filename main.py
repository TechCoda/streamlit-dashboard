import streamlit as st
import json
import datetime
import random

# Load or initialize user data
def load_user_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "streak": 0,
            "last_checkin": None,
            "weekly_goals": [],
            "projects": [],
            "completed_challenges": []
        }
# ---------------------- Global Styling ----------------------

def save_user_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f, indent=2)

user_data = load_user_data()

# 🔁 Optional: Restore progress from uploaded JSON
uploaded_file = st.sidebar.file_uploader("🔁 Restore Progress", type="json")

if uploaded_file is not None:
    try:
        user_data = json.load(uploaded_file)
        st.sidebar.success("✅ Progress restored!")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to load file: {e}")


st.markdown(
    """
    <style>
    .main {
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #f26c8d;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1em;
        font-weight: 600;
    }
    .stDownloadButton>button {
        background-color: #f2a7b3;
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    .stTextInput, .stTextArea {
        border-radius: 10px;
    }
    .stRadio > div {
        gap: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True  # ✅ This was missing the closing parenthesis below
)

st.markdown("""
<div style='background-color:#fff3cd;padding:10px;border-radius:10px;border:1px solid #ffeeba; margin-bottom:1rem;'>
  <strong>⚠️ Beta:</strong> This app is still in testing! Your progress is saved locally and can be restored via file upload. Feedback is welcome 💌
</div>
""", unsafe_allow_html=True)


# ---------------------- Motivation Tab ----------------------
def motivation_tab():
    st.title("🌞 Motivation & Streak Tracker")

    quotes = [
        "Small progress is still progress.",
        "Keep going, you're getting closer.",
        "Code every day, even just a little.",
        "Done is better than perfect."
    ]
    today = str(datetime.date.today())

    st.info(random.choice(quotes))

    last_checkin = user_data.get("last_checkin")
    if last_checkin != today:
        if last_checkin == str(datetime.date.today() - datetime.timedelta(days=1)):
            user_data["streak"] += 1
        else:
            user_data["streak"] = 1
        user_data["last_checkin"] = today
        save_user_data(user_data)

    st.success(f"🔥 Current Streak: {user_data['streak']} day(s)")

# ---------------------- Weekly Goals Tab ----------------------
def weekly_goals_tab():
    st.title("🎯 Weekly Goals")

    goal = st.text_input("Set a goal for this week:")
    if st.button("Add Goal"):
        if goal:
            user_data["weekly_goals"].append({"goal": goal, "done": False})
            save_user_data(user_data)

    for i, item in enumerate(user_data["weekly_goals"]):
        col1, col2 = st.columns([0.8, 0.2])
        if not item["done"]:
            col1.write(f"- {item['goal']}")
            if col2.button("✅ Done", key=f"goal_{i}"):
                user_data["weekly_goals"][i]["done"] = True
                save_user_data(user_data)
        else:
            col1.write(f"✅ ~~{item['goal']}~~")

# ---------------------- Weekly Challenge Tab ----------------------
def challenges_tab():
    st.title("🚀 Weekly Challenge")

    try:
        with open("challenges.json") as f:
            challenges = json.load(f)
    except:
        st.error("Could not load challenges.")
        return

    week_num = datetime.date.today().isocalendar()[1] % len(challenges)
    challenge = challenges[week_num]

    st.subheader(challenge["title"])
    st.write(challenge["description"])
    st.markdown(f"**Track:** {challenge['track']}")
    if challenge["resource_link"]:
        st.markdown(f"[📘 Resource]({challenge['resource_link']})")

    if st.button("✅ Mark Challenge Complete"):
        if challenge["title"] not in user_data["completed_challenges"]:
            user_data["completed_challenges"].append(challenge["title"])
            save_user_data(user_data)
            st.success("Challenge marked as complete!")

            # ---- Download Current Challenge ----
    challenge_text = f"Title: {challenge['title']}\nDescription: {challenge['description']}\nTrack: {challenge['track']}\nLink: {challenge['resource_link']}"
    st.download_button(
        label="📥 Download This Challenge",
        data=challenge_text,
        file_name="weekly_challenge.txt",
        mime="text/plain"
    )


# ---------------------- Portfolio Tab ----------------------
def portfolio_tab():
    st.title("📁 Portfolio Builder")

    # Load portfolio data
    try:
        with open("portfolio.json", "r") as f:
            portfolio = json.load(f)
    except FileNotFoundError:
        portfolio = []

    # --- Add new project form ---
    with st.form("Add Portfolio Project"):
        title = st.text_input("Project Title")
        description = st.text_area("Project Description")
        tech = st.text_input("Technologies Used (comma-separated)")
        link = st.text_input("Link to GitHub or live demo")
        submitted = st.form_submit_button("Add Project")

        if submitted and title:
            portfolio.append({
                "title": title,
                "description": description,
                "tech": tech,
                "link": link,
                "status": "In Progress"  # Default status
            })
            with open("portfolio.json", "w") as f:
                json.dump(portfolio, f, indent=2)
            st.success("Project added to portfolio!")
            st.rerun()

    # --- Layout switcher ---
    st.subheader("🖼️ Portfolio Preview")
    layout = st.radio("Choose a layout", ["🧾 Resume", "📋 List", "💳 Card"])

    if not portfolio:
        st.info("No projects added yet.")
        return

    # --- Display based on layout choice ---
    for i, proj in enumerate(portfolio):
        if layout == "🧾 Resume":
            st.markdown(f"""
- **{proj['title']}**  ({proj.get('status', 'In Progress')})  
  {proj['description']}  
  _Tech:_ `{proj['tech']}`  
  {'🔗 [' + proj['link'] + '](' + proj['link'] + ')' if proj['link'] else ''}
""")
        elif layout == "📋 List":
            with st.expander(f"📌 {proj['title']}"):
                st.write(proj['description'])
                st.markdown(f"**Tech Used:** `{proj['tech']}`")
                st.markdown(f"**Status:** {proj.get('status', 'In Progress')}")
                if proj['link']:
                    st.markdown(f"[🔗 View Project]({proj['link']})")

                col1, col2 = st.columns([0.2, 0.2])
                if col1.button("✏️ Edit", key=f"list_edit_{i}"):
                    with st.form(f"list_edit_form_{i}"):
                        new_title = st.text_input("Project Title", value=proj['title'], key=f"list_title_{i}")
                        new_desc = st.text_area("Description", value=proj['description'], key=f"list_desc_{i}")
                        new_tech = st.text_input("Technologies Used", value=proj['tech'], key=f"list_tech_{i}")
                        new_link = st.text_input("Link", value=proj['link'], key=f"list_link_{i}")

                        # Status dropdown
                        status_options = ["In Progress", "Done", "On Hold"]
                        new_status = st.selectbox("Status", options=status_options, index=status_options.index(proj.get("status", "In Progress")))

                        if st.form_submit_button("Save Changes"):
                            portfolio[i] = {
                                "title": new_title,
                                "description": new_desc,
                                "tech": new_tech,
                                "link": new_link,
                                "status": new_status
                            }
                            with open("portfolio.json", "w") as f:
                                json.dump(portfolio, f, indent=2)
                            st.success("Changes saved!")
                            st.rerun()
                if col2.button("🗑️ Delete", key=f"list_delete_{i}"):
                    portfolio.pop(i)
                    with open("portfolio.json", "w") as f:
                        json.dump(portfolio, f, indent=2)
                    st.warning("Project deleted.")
                    st.rerun()

        elif layout == "💳 Card":
            st.markdown(f"""
<div style='padding: 10px; background-color: #f9f9f9; border-radius: 10px; margin-bottom: 10px;'>
  <h4>{proj['title']} ({proj.get('status', 'In Progress')})</h4>
  <p>{proj['description']}</p>
  <p><b>Tech:</b> <code>{proj['tech']}</code></p>
  {f"<a href='{proj['link']}' target='_blank'>🔗 View Project</a>" if proj['link'] else ''}
</div>
""", unsafe_allow_html=True)

    # --- Display existing projects with Edit/Delete (outside preview) ---
    st.subheader("🗂️ Your Projects")
    if not portfolio:
        st.info("No projects added yet.")
    else:
        for i, proj in enumerate(portfolio):
            with st.expander(f"📌 {proj['title']}"):
                st.markdown(f"**Description:** {proj['description']}")
                st.markdown(f"**Tech Used:** `{proj['tech']}`")
                st.markdown(f"**Status:** {proj.get('status', 'In Progress')}")
                if proj['link']:
                    st.markdown(f"[🔗 View Project]({proj['link']})")

                col1, col2 = st.columns([0.2, 0.2])
                if col1.button("✏️ Edit", key=f"outside_edit_{i}"):
                    with st.form(f"outside_edit_form_{i}"):
                        new_title = st.text_input("Project Title", value=proj['title'], key=f"outside_title_{i}")
                        new_desc = st.text_area("Description", value=proj['description'], key=f"outside_desc_{i}")
                        new_tech = st.text_input("Technologies Used", value=proj['tech'], key=f"outside_tech_{i}")
                        new_link = st.text_input("Link", value=proj['link'], key=f"outside_link_{i}")

                        # Status dropdown here too
                        status_options = ["In Progress", "Done", "On Hold"]
                        new_status = st.selectbox("Status", options=status_options, index=status_options.index(proj.get("status", "In Progress")))

                        if st.form_submit_button("Save Changes"):
                            portfolio[i] = {
                                "title": new_title,
                                "description": new_desc,
                                "tech": new_tech,
                                "link": new_link,
                                "status": new_status
                            }
                            with open("portfolio.json", "w") as f:
                                json.dump(portfolio, f, indent=2)
                            st.success("Changes saved!")
                            st.rerun()

                if col2.button("🗑️ Delete", key=f"outside_delete_{i}"):
                    portfolio.pop(i)
                    with open("portfolio.json", "w") as f:
                        json.dump(portfolio, f, indent=2)
                    st.warning("Project deleted.")
                    st.rerun()

    # ---- Download Portfolio Buttons ----
    st.subheader("📥 Download Your Portfolio")

    portfolio_json = json.dumps(portfolio, indent=2)
    st.download_button(
        label="⬇️ Download as JSON",
        data=portfolio_json,
        file_name="my_portfolio.json",
        mime="application/json"
    )

    # Create a simple text version
    resume_text = ""
    for proj in portfolio:
        resume_text += f"{proj['title']} ({proj.get('status', 'In Progress')})\n"
        resume_text += f"{proj['description']}\n"
        resume_text += f"Tech: {proj['tech']}\n"
        resume_text += f"Link: {proj['link']}\n\n"

    st.download_button(
        label="⬇️ Download as Text",
        data=resume_text,
        file_name="my_portfolio.txt",
        mime="text/plain"
    )


# ---------------------- Main App ----------------------
st.sidebar.title("💡 Navigation")
page = st.sidebar.radio("Go to", ["Motivation", "Weekly Goals", "Weekly Challenges", "Portfolio"])

if page == "Motivation":
    motivation_tab()
elif page == "Weekly Goals":
    weekly_goals_tab()
elif page == "Weekly Challenges":
    challenges_tab()
elif page == "Portfolio":
    portfolio_tab()
