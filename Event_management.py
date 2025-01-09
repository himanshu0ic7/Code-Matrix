import sqlite3
import streamlit as st
import pandas as pd

conn = sqlite3.connect("event_management.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS venues (
        venue_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        venue_id INTEGER NOT NULL,
        ticket_price REAL NOT NULL,
        FOREIGN KEY (venue_id) REFERENCES venues (venue_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendees (
        attendee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        event_id INTEGER NOT NULL,
        ticket_count INTEGER NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events (event_id)
    )
''')
conn.commit()


st.title("🎤 Event Management System")
menu = st.sidebar.selectbox("Menu", ["Add Venue", "Add Event", "View Events", "Register Attendee", "View Attendees", "Event Analytics"])

if menu == "Add Venue":
    st.header("Add a New Venue")
    with st.form("add_venue_form"):
        name = st.text_input("Venue Name")
        location = st.text_input("Location")
        capacity = st.number_input("Capacity", min_value=1, step=1)
        submitted = st.form_submit_button("Add Venue")

        if submitted:
            cursor.execute("INSERT INTO venues (name, location, capacity) VALUES (?, ?, ?)", (name, location, capacity))
            conn.commit()
            st.success(f"Venue '{name}' added successfully!")

elif menu == "Add Event":
    st.header("Add a New Event")
    cursor.execute("SELECT * FROM venues")
    venues = cursor.fetchall()

    if venues:
        with st.form("add_event_form"):
            name = st.text_input("Event Name")
            date = st.date_input("Event Date")
            venue_id = st.selectbox("Select Venue", [f"{v[0]} - {v[1]}" for v in venues])
            ticket_price = st.number_input("Ticket Price", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Event")

            if submitted:
                venue_id = int(venue_id.split(" - ")[0])
                cursor.execute("INSERT INTO events (name, date, venue_id, ticket_price) VALUES (?, ?, ?, ?)", (name, date, venue_id, ticket_price))
                conn.commit()
                st.success(f"Event '{name}' added successfully!")
    else:
        st.info("No venues available. Please add a venue first.")

elif menu == "View Events":
    st.header("Available Events")
    cursor.execute("SELECT events.event_id, events.name, events.date, venues.name AS venue, events.ticket_price "
                   "FROM events INNER JOIN venues ON events.venue_id = venues.venue_id")
    events = cursor.fetchall()

    if events:
        df = pd.DataFrame(events, columns=["Event ID", "Event Name", "Date", "Venue", "Ticket Price"])
        st.table(df)
    else:
        st.info("No events available.")

elif menu == "Register Attendee":
    st.header("Register an Attendee")
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    if events:
        with st.form("register_attendee_form"):
            name = st.text_input("Attendee Name")
            event_id = st.selectbox("Select Event", [f"{e[0]} - {e[1]}" for e in events])
            ticket_count = st.number_input("Number of Tickets", min_value=1, step=1)
            submitted = st.form_submit_button("Register Attendee")

            if submitted:
                event_id = int(event_id.split(" - ")[0])
                cursor.execute("INSERT INTO attendees (name, event_id, ticket_count) VALUES (?, ?, ?)", (name, event_id, ticket_count))
                conn.commit()
                st.success(f"{name} successfully registered for the event.")
    else:
        st.info("No events available. Please add an event first.")

elif menu == "View Attendees":
    st.header("Attendee List")
    cursor.execute("SELECT attendees.name, events.name AS event, attendees.ticket_count "
                   "FROM attendees INNER JOIN events ON attendees.event_id = events.event_id")
    attendees = cursor.fetchall()

    if attendees:
        df = pd.DataFrame(attendees, columns=["Attendee Name", "Event", "Tickets Purchased"])
        st.table(df)
    else:
        st.info("No attendees registered.")

elif menu == "Event Analytics":
    st.header("Event Analytics")
    cursor.execute("SELECT events.name, SUM(attendees.ticket_count) AS total_attendees, "
                   "SUM(attendees.ticket_count * events.ticket_price) AS total_revenue "
                   "FROM attendees INNER JOIN events ON attendees.event_id = events.event_id "
                   "GROUP BY events.event_id")
    analytics = cursor.fetchall()

    if analytics:
        df = pd.DataFrame(analytics, columns=["Event Name", "Total Attendees", "Total Revenue"])
        st.table(df)
    else:
        st.info("No data available for analytics.")

st.markdown("<p style='text-align: center;'>Developed with ❤️ using Python and Streamlit</p>", unsafe_allow_html=True)