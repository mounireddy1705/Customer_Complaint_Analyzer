import streamlit as st
from collections import Counter
import pandas as pd

from complaint_manager import (
    load_complaints,
    create_complaint,
    update_complaint,
    add_thread_message,
    get_complaint
)

from ollama_ai import analyze_complaint


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ComplaintIQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #172554 !important;
    }

    p {
        color: #334155;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #172554;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Metric cards */

    [data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    }

    /* General cards */

    .custom-card {
        background-color: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        margin-bottom: 18px;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

complaints = load_complaints()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🤖 ComplaintIQ")
    st.write("AI Customer Complaint Analyzer")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📝 Raise Complaint",
            "📋 All Complaints",
            "💬 Complaint Threads",
            "📊 Analytics",
            "🤖 AI Insights"
        ]
    )

    st.divider()

    st.caption("Powered by Ollama + Llama 3.2")


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("🤖 ComplaintIQ Dashboard")

    st.write(
        "AI-powered overview of your customer complaints."
    )

    st.divider()

    # -----------------------------------------------------
    # KPI CALCULATIONS
    # -----------------------------------------------------

    total = len(complaints)

    open_count = sum(
        1
        for c in complaints
        if c.get("status") not in ["Resolved", "Closed"]
    )

    resolved_count = sum(
        1
        for c in complaints
        if c.get("status") in ["Resolved", "Closed"]
    )

    urgent_count = sum(
        1
        for c in complaints
        if c.get("analysis", {}).get("priority")
        in ["High", "Critical"]
    )

    negative_count = sum(
        1
        for c in complaints
        if c.get("analysis", {}).get("sentiment")
        == "Negative"
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📋 Total", total)

    with col2:
        st.metric("🟠 Open", open_count)

    with col3:
        st.metric("🚨 Urgent", urgent_count)

    with col4:
        st.metric("✅ Resolved", resolved_count)

    with col5:
        st.metric("🔴 Negative", negative_count)

    st.divider()

    # -----------------------------------------------------
    # AI OVERVIEW
    # -----------------------------------------------------

    st.subheader("🤖 AI Complaint Overview")

    if complaints:

        categories = Counter(
            c.get("analysis", {}).get(
                "category",
                "Other"
            )
            for c in complaints
        )

        sentiments = Counter(
            c.get("analysis", {}).get(
                "sentiment",
                "Neutral"
            )
            for c in complaints
        )

        priorities = Counter(
            c.get("analysis", {}).get(
                "priority",
                "Medium"
            )
            for c in complaints
        )

        departments = Counter(
            c.get(
                "department",
                "Other"
            )
            for c in complaints
        )

        top_category = (
            categories.most_common(1)[0][0]
            if categories else "N/A"
        )

        top_department = (
            departments.most_common(1)[0][0]
            if departments else "N/A"
        )

        top_sentiment = (
            sentiments.most_common(1)[0][0]
            if sentiments else "N/A"
        )

        top_priority = (
            priorities.most_common(1)[0][0]
            if priorities else "N/A"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info(
                f"📌 **Top Category**\n\n"
                f"{top_category}"
            )

        with col2:
            st.info(
                f"🏢 **Top Department**\n\n"
                f"{top_department}"
            )

        with col3:
            st.info(
                f"😊 **Common Sentiment**\n\n"
                f"{top_sentiment}"
            )

        with col4:
            st.info(
                f"⚡ **Common Priority**\n\n"
                f"{top_priority}"
            )

    else:

        st.info(
            "No complaints yet. Raise a complaint to generate AI insights."
        )

    st.divider()

    # -----------------------------------------------------
    # COMPLAINT TREND
    # -----------------------------------------------------

    st.subheader("📈 Complaint Trend")

    if complaints:

        trend_records = []

        for complaint in complaints:

            created_at = complaint.get(
                "created_at",
                ""
            )

            if created_at:
                trend_records.append(
                    {
                        "Date": created_at[:10]
                    }
                )

        if trend_records:

            trend_df = pd.DataFrame(
                trend_records
            )

            trend_df["Date"] = pd.to_datetime(
                trend_df["Date"],
                errors="coerce"
            )

            trend_df = trend_df.dropna()

            if not trend_df.empty:

                trend_df = (
                    trend_df
                    .groupby("Date")
                    .size()
                    .reset_index(
                        name="Complaints"
                    )
                    .set_index("Date")
                )

                st.line_chart(
                    trend_df["Complaints"]
                )

            else:

                st.info(
                    "No valid date information available."
                )

        else:

            st.info(
                "No complaint trend data available."
            )

    else:

        st.info(
            "No complaints available."
        )

    st.divider()

    # -----------------------------------------------------
    # CATEGORY + PRIORITY
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Complaints by Category")

        if complaints:

            category_counts = Counter(
                c.get("analysis", {}).get(
                    "category",
                    "Other"
                )
                for c in complaints
            )

            category_df = pd.DataFrame(
                {
                    "Category": list(
                        category_counts.keys()
                    ),
                    "Complaints": list(
                        category_counts.values()
                    )
                }
            )

            st.bar_chart(
                category_df.set_index(
                    "Category"
                )
            )

        else:

            st.info("No category data.")

    with col2:

        st.subheader("🚨 Priority Distribution")

        if complaints:

            priority_counts = Counter(
                c.get("analysis", {}).get(
                    "priority",
                    "Medium"
                )
                for c in complaints
            )

            priority_df = pd.DataFrame(
                {
                    "Priority": list(
                        priority_counts.keys()
                    ),
                    "Complaints": list(
                        priority_counts.values()
                    )
                }
            )

            st.bar_chart(
                priority_df.set_index(
                    "Priority"
                )
            )

        else:

            st.info("No priority data.")

    st.divider()

    # -----------------------------------------------------
    # SENTIMENT + DEPARTMENT
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("😊 Customer Sentiment")

        if complaints:

            sentiment_counts = Counter(
                c.get("analysis", {}).get(
                    "sentiment",
                    "Neutral"
                )
                for c in complaints
            )

            sentiment_df = pd.DataFrame(
                {
                    "Sentiment": list(
                        sentiment_counts.keys()
                    ),
                    "Complaints": list(
                        sentiment_counts.values()
                    )
                }
            )

            st.bar_chart(
                sentiment_df.set_index(
                    "Sentiment"
                )
            )

        else:

            st.info("No sentiment data.")

    with col2:

        st.subheader("🏢 Complaints by Department")

        if complaints:

            department_counts = Counter(
                c.get(
                    "department",
                    "Other"
                )
                for c in complaints
            )

            department_df = pd.DataFrame(
                {
                    "Department": list(
                        department_counts.keys()
                    ),
                    "Complaints": list(
                        department_counts.values()
                    )
                }
            )

            st.bar_chart(
                department_df.set_index(
                    "Department"
                )
            )

        else:

            st.info("No department data.")

    st.divider()

    # -----------------------------------------------------
    # RECENT COMPLAINTS
    # -----------------------------------------------------

    st.subheader("🕒 Recent Complaints")

    if complaints:

        recent = list(
            reversed(
                complaints[-5:]
            )
        )

        for complaint in recent:

            analysis = complaint.get(
                "analysis",
                {}
            )

            with st.container(border=True):

                st.markdown(
                    f"### #{complaint.get('id', 'N/A')} "
                    f"— {complaint.get('subject', 'No Subject')}"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.write(
                        f"**Customer:** "
                        f"{complaint.get('customer_name', 'Unknown')}"
                    )

                with col2:
                    st.write(
                        f"**Category:** "
                        f"{analysis.get('category', 'Other')}"
                    )

                with col3:
                    st.write(
                        f"**Priority:** "
                        f"{analysis.get('priority', 'Medium')}"
                    )

                with col4:
                    st.write(
                        f"**Status:** "
                        f"{complaint.get('status', 'New')}"
                    )

                st.write(
                    f"**Complaint:** "
                    f"{complaint.get('complaint', '')}"
                )

    else:

        st.info(
            "No complaints yet."
        )

    st.divider()

    # -----------------------------------------------------
    # QUICK INSIGHTS
    # -----------------------------------------------------

    st.subheader("💡 Quick Business Insights")

    if complaints:

        if urgent_count > 0:

            st.warning(
                f"🚨 There are **{urgent_count}** "
                f"High/Critical complaints requiring attention."
            )

        else:

            st.success(
                "✅ There are currently no High/Critical complaints."
            )

        if negative_count > 0:

            st.warning(
                f"🔴 **{negative_count}** complaints have negative sentiment."
            )

        if total > 0:

            resolution_rate = (
                resolved_count / total
            ) * 100

            st.info(
                f"📈 Current resolution rate: "
                f"**{resolution_rate:.1f}%**"
            )

    else:

        st.info(
            "Add complaints to generate business insights."
        )


# =========================================================
# RAISE COMPLAINT
# =========================================================

elif page == "📝 Raise Complaint":

    st.title("📝 Raise a Complaint")

    st.write(
        "Submit a complaint and let Ollama analyze it instantly."
    )

    st.divider()

    with st.form("complaint_form"):

        col1, col2 = st.columns(2)

        with col1:

            customer_name = st.text_input(
                "Customer Name",
                placeholder="Enter customer name"
            )

        with col2:

            department = st.selectbox(
                "Department",
                [
                    "Billing",
                    "Product",
                    "Service",
                    "Delivery",
                    "Technical",
                    "Account",
                    "Refund",
                    "Other"
                ]
            )

        subject = st.text_input(
            "Complaint Subject",
            placeholder="Example: Delivery delay"
        )

        complaint_text = st.text_area(
            "Describe Your Complaint",
            placeholder="Explain your problem in detail...",
            height=180
        )

        submitted = st.form_submit_button(
            "🤖 Analyze Complaint",
            use_container_width=True
        )

    if submitted:

        if not customer_name.strip():

            st.error("Please enter the customer name.")

        elif not subject.strip():

            st.error("Please enter the complaint subject.")

        elif not complaint_text.strip():

            st.error("Please describe the complaint.")

        else:

            try:

                with st.spinner(
                    "🤖 Ollama is analyzing your complaint..."
                ):

                    complaint = create_complaint(
                        customer_name=customer_name.strip(),
                        subject=subject.strip(),
                        complaint_text=complaint_text.strip(),
                        department=department
                    )

                    analysis = analyze_complaint(
                        complaint_text.strip()
                    )

                    update_complaint(
                        complaint["id"],
                        {
                            "analysis": analysis,
                            "status": "Analyzed"
                        }
                    )

                st.success(
                    f"Complaint #{complaint['id']} submitted successfully!"
                )

                st.divider()

                st.subheader("🤖 AI Complaint Analysis")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Category",
                        analysis.get(
                            "category",
                            "Other"
                        )
                    )

                with col2:
                    st.metric(
                        "Sentiment",
                        analysis.get(
                            "sentiment",
                            "Neutral"
                        )
                    )

                with col3:
                    st.metric(
                        "Priority",
                        analysis.get(
                            "priority",
                            "Medium"
                        )
                    )

                with st.container(border=True):

                    st.subheader("📋 Complaint Summary")

                    st.write(
                        analysis.get(
                            "summary",
                            "No summary available."
                        )
                    )

                with st.container(border=True):

                    st.subheader("🔎 Key Issues")

                    issues = analysis.get(
                        "key_issues",
                        []
                    )

                    if issues:

                        for issue in issues:
                            st.write(
                                f"• {issue}"
                            )

                    else:

                        st.write(
                            "No specific key issues identified."
                        )

                with st.container(border=True):

                    st.subheader(
                        "🌱 Possible Root Cause"
                    )

                    st.write(
                        analysis.get(
                            "root_cause",
                            "Not available."
                        )
                    )

                with st.container(border=True):

                    st.subheader(
                        "💡 Company Feedback"
                    )

                    st.write(
                        analysis.get(
                            "feedback",
                            "Not available."
                        )
                    )

                with st.container(border=True):

                    st.subheader(
                        "✅ Recommended Action"
                    )

                    st.write(
                        analysis.get(
                            "suggested_action",
                            "Not available."
                        )
                    )

                with st.container(border=True):

                    st.subheader(
                        "💬 Suggested Customer Response"
                    )

                    st.write(
                        analysis.get(
                            "suggested_response",
                            "Not available."
                        )
                    )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )


# =========================================================
# ALL COMPLAINTS
# =========================================================

elif page == "📋 All Complaints":

    st.title("📋 All Complaints")

    st.write(
        "Search, filter, and manage customer complaints."
    )

    st.divider()

    if not complaints:

        st.info(
            "No complaints available yet."
        )

    else:

        st.subheader("🔎 Search & Filters")

        col1, col2 = st.columns(2)

        with col1:

            search_text = st.text_input(
                "Search",
                placeholder=(
                    "Search customer, subject, ID, or complaint..."
                )
            )

        with col2:

            departments = sorted(
                set(
                    c.get(
                        "department",
                        "Other"
                    )
                    for c in complaints
                )
            )

            department_filter = st.selectbox(
                "🏢 Department",
                ["All"] + departments
            )

        col1, col2, col3 = st.columns(3)

        with col1:

            priority_filter = st.selectbox(
                "🚨 Priority",
                [
                    "All",
                    "Low",
                    "Medium",
                    "High",
                    "Critical"
                ]
            )

        with col2:

            sentiment_filter = st.selectbox(
                "😊 Sentiment",
                [
                    "All",
                    "Positive",
                    "Neutral",
                    "Negative"
                ]
            )

        with col3:

            status_filter = st.selectbox(
                "🔄 Status",
                [
                    "All",
                    "New",
                    "Analyzed",
                    "In Progress",
                    "Waiting for Customer",
                    "Resolved",
                    "Closed"
                ]
            )

        # Apply filters

        filtered = []

        for complaint in complaints:

            analysis = complaint.get(
                "analysis",
                {}
            )

            if search_text.strip():

                search = search_text.lower()

                searchable = " ".join(
                    [
                        complaint.get(
                            "id",
                            ""
                        ),
                        complaint.get(
                            "customer_name",
                            ""
                        ),
                        complaint.get(
                            "subject",
                            ""
                        ),
                        complaint.get(
                            "complaint",
                            ""
                        )
                    ]
                ).lower()

                if search not in searchable:
                    continue

            if (
                department_filter != "All"
                and complaint.get(
                    "department"
                ) != department_filter
            ):
                continue

            if (
                priority_filter != "All"
                and analysis.get(
                    "priority",
                    "Medium"
                ) != priority_filter
            ):
                continue

            if (
                sentiment_filter != "All"
                and analysis.get(
                    "sentiment",
                    "Neutral"
                ) != sentiment_filter
            ):
                continue

            if (
                status_filter != "All"
                and complaint.get(
                    "status",
                    "New"
                ) != status_filter
            ):
                continue

            filtered.append(
                complaint
            )

        st.write(
            f"Showing **{len(filtered)}** "
            f"of **{len(complaints)}** complaints"
        )

        st.divider()

        if filtered:

            for complaint in reversed(filtered):

                analysis = complaint.get(
                    "analysis",
                    {}
                )

                with st.container(border=True):

                    st.markdown(
                        f"### #{complaint.get('id', 'N/A')} "
                        f"— {complaint.get('subject', 'No Subject')}"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.write("**Customer**")

                        st.write(
                            complaint.get(
                                "customer_name",
                                "Unknown"
                            )
                        )

                    with col2:

                        st.write("**Department**")

                        st.write(
                            complaint.get(
                                "department",
                                "Other"
                            )
                        )

                    with col3:

                        st.write("**Priority**")

                        st.write(
                            analysis.get(
                                "priority",
                                "Not Analyzed"
                            )
                        )

                    with col4:

                        st.write("**Sentiment**")

                        st.write(
                            analysis.get(
                                "sentiment",
                                "Not Analyzed"
                            )
                        )

                    st.write("**Complaint:**")

                    st.write(
                        complaint.get(
                            "complaint",
                            ""
                        )
                    )

                    st.write(
                        f"**Status:** "
                        f"{complaint.get('status', 'New')}"
                    )

                    statuses = [
                        "New",
                        "Analyzed",
                        "In Progress",
                        "Waiting for Customer",
                        "Resolved",
                        "Closed"
                    ]

                    current_status = complaint.get(
                        "status",
                        "New"
                    )

                    index = (
                        statuses.index(
                            current_status
                        )
                        if current_status in statuses
                        else 0
                    )

                    new_status = st.selectbox(
                        "Change Status",
                        statuses,
                        index=index,
                        key=f"status_{complaint['id']}"
                    )

                    if st.button(
                        "💾 Save Status",
                        key=f"save_status_{complaint['id']}"
                    ):

                        update_complaint(
                            complaint["id"],
                            {
                                "status": new_status
                            }
                        )

                        st.success(
                            "Status updated successfully."
                        )

                        st.rerun()

        else:

            st.warning(
                "No complaints match the selected filters."
            )


# =========================================================
# COMPLAINT THREADS
# =========================================================

elif page == "💬 Complaint Threads":

    st.title("💬 Complaint Threads")

    st.write(
        "View complaint history and continue the conversation."
    )

    st.divider()

    if not complaints:

        st.info(
            "No complaint threads available."
        )

    else:

        complaint_options = {
            f"#{c['id']} — {c['subject']}":
            c["id"]
            for c in complaints
        }

        selected = st.selectbox(
            "🔎 Select Complaint",
            list(complaint_options.keys())
        )

        complaint_id = complaint_options[selected]

        complaint = get_complaint(
            complaint_id
        )

        if complaint:

            analysis = complaint.get(
                "analysis",
                {}
            )

            st.subheader(
                f"Complaint #{complaint['id']}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Status",
                    complaint.get(
                        "status",
                        "New"
                    )
                )

            with col2:
                st.metric(
                    "Priority",
                    analysis.get(
                        "priority",
                        "Medium"
                    )
                )

            with col3:
                st.metric(
                    "Sentiment",
                    analysis.get(
                        "sentiment",
                        "Neutral"
                    )
                )

            with col4:
                st.metric(
                    "Category",
                    analysis.get(
                        "category",
                        "Other"
                    )
                )

            st.write(
                f"**Customer:** "
                f"{complaint.get('customer_name', 'Unknown')}"
            )

            st.write(
                f"**Department:** "
                f"{complaint.get('department', 'Other')}"
            )

            st.write(
                f"**Subject:** "
                f"{complaint.get('subject', '')}"
            )

            st.divider()

            # -------------------------------------------------
            # AI ANALYSIS
            # -------------------------------------------------

            st.subheader("🤖 AI Analysis")

            if analysis:

                with st.expander(
                    "📋 View Complete AI Analysis",
                    expanded=True
                ):

                    st.write(
                        "**Summary:**"
                    )

                    st.write(
                        analysis.get(
                            "summary",
                            ""
                        )
                    )

                    st.write(
                        "**Key Issues:**"
                    )

                    issues = analysis.get(
                        "key_issues",
                        []
                    )

                    for issue in issues:

                        st.write(
                            f"• {issue}"
                        )

                    st.write(
                        "**Possible Root Cause:**"
                    )

                    st.write(
                        analysis.get(
                            "root_cause",
                            ""
                        )
                    )

                    st.write(
                        "**Company Feedback:**"
                    )

                    st.write(
                        analysis.get(
                            "feedback",
                            ""
                        )
                    )

                    st.write(
                        "**Recommended Action:**"
                    )

                    st.write(
                        analysis.get(
                            "suggested_action",
                            ""
                        )
                    )

                    st.write(
                        "**Suggested Response:**"
                    )

                    st.write(
                        analysis.get(
                            "suggested_response",
                            ""
                        )
                    )

            else:

                st.warning(
                    "This complaint has not been analyzed yet."
                )

            st.divider()

            # -------------------------------------------------
            # THREAD
            # -------------------------------------------------

            st.subheader("💬 Conversation Thread")

            thread = complaint.get(
                "thread",
                []
            )

            for message in thread:

                sender = message.get(
                    "sender",
                    "Unknown"
                )

                content = message.get(
                    "message",
                    ""
                )

                timestamp = message.get(
                    "timestamp",
                    ""
                )

                if sender == "Customer":

                    with st.chat_message("user"):

                        st.write(
                            f"**Customer** • {timestamp}"
                        )

                        st.write(
                            content
                        )

                else:

                    with st.chat_message("assistant"):

                        st.write(
                            f"**{sender}** • {timestamp}"
                        )

                        st.write(
                            content
                        )

            st.divider()

            # -------------------------------------------------
            # ADD MESSAGE
            # -------------------------------------------------

            st.subheader("➕ Add Message")

            sender = st.selectbox(
                "Sender",
                [
                    "Customer",
                    "Support"
                ]
            )

            new_message = st.text_area(
                "Message",
                placeholder=(
                    "Enter a customer follow-up "
                    "or support response..."
                ),
                height=120
            )

            if st.button(
                "💬 Add Message",
                use_container_width=True
            ):

                if new_message.strip():

                    add_thread_message(
                        complaint_id,
                        sender,
                        new_message.strip()
                    )

                    st.success(
                        "Message added successfully!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Please enter a message."
                    )

            st.divider()

            # -------------------------------------------------
            # UPDATE STATUS
            # -------------------------------------------------

            st.subheader("🔄 Update Status")

            statuses = [
                "New",
                "Analyzed",
                "In Progress",
                "Waiting for Customer",
                "Resolved",
                "Closed"
            ]

            current_status = complaint.get(
                "status",
                "New"
            )

            current_index = (
                statuses.index(current_status)
                if current_status in statuses
                else 0
            )

            new_status = st.selectbox(
                "Status",
                statuses,
                index=current_index,
                key=f"thread_status_{complaint_id}"
            )

            if st.button(
                "✅ Save Status",
                use_container_width=True
            ):

                update_complaint(
                    complaint_id,
                    {
                        "status": new_status
                    }
                )

                st.success(
                    f"Status changed to {new_status}."
                )

                st.rerun()

            st.divider()

            # -------------------------------------------------
            # RE-ANALYZE
            # -------------------------------------------------

            st.subheader(
                "🔄 AI Re-analysis"
            )

            st.write(
                "Use this after a follow-up message "
                "to update the AI analysis."
            )

            if st.button(
                "🤖 Re-analyze with Ollama",
                use_container_width=True
            ):

                conversation = ""

                for message in complaint.get(
                    "thread",
                    []
                ):

                    conversation += (
                        f"\n{message.get('sender', '')}: "
                        f"{message.get('message', '')}"
                    )

                with st.spinner(
                    "🤖 Ollama is re-analyzing the thread..."
                ):

                    try:

                        new_analysis = analyze_complaint(
                            conversation
                        )

                        update_complaint(
                            complaint_id,
                            {
                                "analysis": new_analysis,
                                "status": "Analyzed"
                            }
                        )

                        st.success(
                            "AI analysis updated successfully!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Re-analysis failed: {e}"
                        )


# =========================================================
# ANALYTICS
# =========================================================

elif page == "📊 Analytics":

    st.title("📊 Complaint Analytics")

    st.write(
        "Analyze complaint patterns and customer behavior."
    )

    st.divider()

    if not complaints:

        st.info(
            "Add complaints to see analytics."
        )

    else:

        categories = Counter(
            c.get("analysis", {}).get(
                "category",
                "Other"
            )
            for c in complaints
        )

        priorities = Counter(
            c.get("analysis", {}).get(
                "priority",
                "Medium"
            )
            for c in complaints
        )

        sentiments = Counter(
            c.get("analysis", {}).get(
                "sentiment",
                "Neutral"
            )
            for c in complaints
        )

        departments = Counter(
            c.get(
                "department",
                "Other"
            )
            for c in complaints
        )

        statuses = Counter(
            c.get(
                "status",
                "New"
            )
            for c in complaints
        )

        # KPI

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total",
                len(complaints)
            )

        with col2:

            st.metric(
                "High/Critical",
                priorities.get("High", 0)
                + priorities.get("Critical", 0)
            )

        with col3:

            st.metric(
                "Negative",
                sentiments.get(
                    "Negative",
                    0
                )
            )

        with col4:

            st.metric(
                "Resolved",
                statuses.get(
                    "Resolved",
                    0
                )
                + statuses.get(
                    "Closed",
                    0
                )
            )

        st.divider()

        # Category chart

        st.subheader("📊 Complaints by Category")

        category_df = pd.DataFrame(
            {
                "Category": list(
                    categories.keys()
                ),
                "Complaints": list(
                    categories.values()
                )
            }
        )

        st.bar_chart(
            category_df.set_index(
                "Category"
            )
        )

        # Priority and sentiment

        col1, col2 = st.columns(2)

        with col1:

            st.subheader(
                "🚨 Priority Distribution"
            )

            priority_df = pd.DataFrame(
                {
                    "Priority": list(
                        priorities.keys()
                    ),
                    "Complaints": list(
                        priorities.values()
                    )
                }
            )

            st.bar_chart(
                priority_df.set_index(
                    "Priority"
                )
            )

        with col2:

            st.subheader(
                "😊 Sentiment Distribution"
            )

            sentiment_df = pd.DataFrame(
                {
                    "Sentiment": list(
                        sentiments.keys()
                    ),
                    "Complaints": list(
                        sentiments.values()
                    )
                }
            )

            st.bar_chart(
                sentiment_df.set_index(
                    "Sentiment"
                )
            )

        st.divider()

        # Department

        st.subheader(
            "🏢 Complaints by Department"
        )

        department_df = pd.DataFrame(
            {
                "Department": list(
                    departments.keys()
                ),
                "Complaints": list(
                    departments.values()
                )
            }
        )

        st.bar_chart(
            department_df.set_index(
                "Department"
            )
        )


# =========================================================
# AI INSIGHTS
# =========================================================

elif page == "🤖 AI Insights":

    st.title("🤖 AI Business Insights")

    st.write(
        "Important patterns and recommendations based on complaints."
    )

    st.divider()

    if not complaints:

        st.info(
            "Add complaints to generate AI insights."
        )

    else:

        categories = Counter(
            c.get("analysis", {}).get(
                "category",
                "Other"
            )
            for c in complaints
        )

        sentiments = Counter(
            c.get("analysis", {}).get(
                "sentiment",
                "Neutral"
            )
            for c in complaints
        )

        priorities = Counter(
            c.get("analysis", {}).get(
                "priority",
                "Medium"
            )
            for c in complaints
        )

        departments = Counter(
            c.get(
                "department",
                "Other"
            )
            for c in complaints
        )

        resolved = sum(
            1
            for c in complaints
            if c.get("status")
            in ["Resolved", "Closed"]
        )

        high_priority = (
            priorities.get("High", 0)
            + priorities.get("Critical", 0)
        )

        negative = sentiments.get(
            "Negative",
            0
        )

        top_category = (
            categories.most_common(1)[0][0]
            if categories
            else "N/A"
        )

        top_department = (
            departments.most_common(1)[0][0]
            if departments
            else "N/A"
        )

        # -------------------------------------------------
        # OVERVIEW
        # -------------------------------------------------

        st.subheader("📌 Overall Situation")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.info(
                f"📌 Most common issue category:\n\n"
                f"**{top_category}**"
            )

        with col2:

            st.warning(
                f"🚨 High/Critical complaints:\n\n"
                f"**{high_priority}**"
            )

        with col3:

            st.error(
                f"🔴 Negative sentiment:\n\n"
                f"**{negative}**"
            )

        st.divider()

        # -------------------------------------------------
        # BUSINESS INSIGHTS
        # -------------------------------------------------

        st.subheader(
            "💡 Business Recommendations"
        )

        if high_priority > 0:

            st.warning(
                "Prioritize High and Critical complaints "
                "and assign them to support staff immediately."
            )

        if negative > 0:

            st.warning(
                "A significant number of customers show "
                "negative sentiment. Review recurring complaints "
                "and improve customer support."
            )

        if resolved > 0:

            resolution_rate = (
                resolved / len(complaints)
            ) * 100

            st.info(
                f"Current complaint resolution rate: "
                f"**{resolution_rate:.1f}%**"
            )

        st.success(
            f"The department receiving the most complaints is "
            f"**{top_department}**."
        )

        # -------------------------------------------------
        # TOP CATEGORIES
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "📊 Top Complaint Categories"
        )

        category_table = pd.DataFrame(
            {
                "Category": list(
                    categories.keys()
                ),
                "Complaints": list(
                    categories.values()
                )
            }
        ).sort_values(
            "Complaints",
            ascending=False
        )

        st.dataframe(
            category_table,
            use_container_width=True,
            hide_index=True
        )