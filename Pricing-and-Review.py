import streamlit as st
# from chatbot_using_openai_assistant_v2 import process_query, assistant
from ref import process_query, assistant
from arrange import fetch_reviews

# App configuration
st.set_page_config(
    page_title="Jazzee Agent", 
    layout="wide"
)

# CSS for sticky header and footer
st.markdown(
    """
    <style>
        .sticky-header {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 1000;
            padding: 5px;
            border-bottom: 1px solid #ddd;
            text-align: center;
        }

        .dropdown-container {
            max-width: 150px;
            margin-left: auto;
        }

        div[data-baseweb="select"] {
            max-height:300px;
            max-width: 350px;
            margin-left: auto;
            overflow-y: auto;
        }

        .sticky-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: white;
            padding: 10px;
            border-top: 1px solid #ddd;
            z-index: 1000;
        }

        .main-content {
            margin-top: 20px;
            margin-bottom: 60px; /* Space for the sticky footer */
            max-height: calc(100vh - 140px); /* Adjust height based on header and footer */
            overflow-y: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.markdown('<div class="sticky-header"><h1>Jazzee Assist Agent</h1></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; font-size: 18px; line-height: 1.6;">
        <strong>Welcome to our SaaS Pricing Tool!</strong><br>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    """
    <div style="text-align: center; font-size: 16px; line-height: 1.2;">
        Discover customized pricing options tailored to your needs.
        This tool provides detailed insights into our product tiers,
        helping you make informed decisions. Explore genuine product reviews
        and find the perfect plan for your business today!
    </div>
    """,
    unsafe_allow_html=True
)
# Sidebar
st.sidebar.header("Select a Product")

# Dropdown for product selection
# product = st.sidebar.selectbox(
#     "Select a Product:",
#     ["Product 1", "Product 2", "Product 3"]
# )

default_option = "Select an option"
# options = [default_option, 'Airtable', 'Confluence', 'Jira', 'BambooHR', 'Box', 'Calendly', 'ClickUp', 'DocuSign eSignature', 'Druva SAAS Applications', 'Freshdesk', 'GitHub', 'Gitlab', 'Gong', 'HubSpot Marketing Hub', 'Jamf', 'JFrog Self-Hosted', 'Miro', 'Monday.com', 'MongoDB', 'Okta Workforce Identity Cloud', 'Palo Alto Networks Prisma Access', 'Pluralsight Flow', 'Rippling Platform', 'ServiceNow IT Service Management', 'Tableau Cloud', 'Terraform', 'Zoom Workplace', 'ZoomInfo', 'Asana', 'HubSpot Sales Hub', 'Notion', 'PagerDuty', 'Trello', 'Zendesk Suite', 'wiz', 'orca_security', 'Sentinelone', 'Drata', 'Vanta', 'Sprinto', 'Dropbox', 'Elastic', 'Lucidchart', 'Adobe esign', 'Adobe Creative Cloud All apps', 'Adobe Creative Cloud Single App', 'Crowdstrike', 'Datadog Infrastructure', 'Datadog Security', 'Datadog Applications', 'Figma', 'Freshworks Freshservice', 'Guesty', 'HubSpot Service Hub', 'Panther Web', 'Panther Web+Apps', 'Pluralsight Skills', 'Postman', 'Shopify', 'Slack', 'Snowflake', 'Square', 'TravisCI', 'Twilio', 'Vercel']  # Generate 100 options
options = [default_option, "Confluence", "Notion", "Box", "Dropbox"]
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None

selected_option = st.sidebar.selectbox("Select an option:", options, label_visibility="collapsed")


# Chat messages
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if "chat_mode" not in st.session_state:
    st.session_state["chat_mode"] = None

if "thread" not in st.session_state:
    st.session_state.thread = None

st.sidebar.header("Select a Service")
# Toggle buttons side by side
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("Pricing"):
        st.session_state["chat_mode"] = "Pricing"
    
with col2:
    if st.button("Review"):
        st.session_state["chat_mode"] = "Review"

# with col3:
#     if st.button("Migration"):
#         st.switch_page("pages/Migration.py")
# st.sidebar.page_link("pages/Migration.py", label="Migration Analysis")

chat_mode = st.session_state["chat_mode"]

if chat_mode:
    st.sidebar.markdown(f"You have selected {chat_mode}.")
else:
    st.sidebar.markdown("You have not selected any services.")
# Main screen for chat
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state['messages']:
    if message['sender'] == 'user':
        # st.write(f"**You:** {message['content']}")
        # st.chat_message(name="human")
        with st.chat_message("human"):
            st.markdown(message['content'])
    else:
        # st.write(f"**Bot:** {message['content']}")
        with st.chat_message("ai"):
            st.markdown(message['content'])

# Scroll to bottom
scroll_script = """
    <script>
        const chatDiv = window.parent.document.querySelector('section.main');
        if (chatDiv) {
            setTimeout(() => { chatDiv.scrollTop = chatDiv.scrollHeight; }, 100);
        }
    </script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sticky text input for chatting
st.markdown('<div class="sticky-footer">', unsafe_allow_html=True)
# def handle_input():
#     # chat_input = st.session_state['chat_input']
#     selected_product = selected_option
#     if chat_input:
#         # Add user message
#         print("I am here")
#         st.session_state['messages'].append({"sender": "user", "content": chat_input})

#         # Add bot reply
#         if st.session_state["chat_mode"] == "Pricing":
#             # bot_reply = f"I see you said pricing: {chat_input}, {selected_product}"
#             query_header = f"The product in context is {selected_product}."
#             query_input = query_header + chat_input
#             bot_reply, st.session_state.thread = process_query(query=query_input, thread=st.session_state.thread, assistant=assistant)

#         else:
#             # bot_reply = f"I see you said review: {chat_input}, {selected_product}"
#             bot_reply = fetch_reviews(query=chat_input, product=selected_product)
#         st.session_state['messages'].append({"sender": "bot", "content": bot_reply})

        # Clear input field
        # st.session_state['chat_input'] = ""

if "processing" not in st.session_state:
    st.session_state["processing"] = False

if "chat_input" not in st.session_state:
    st.session_state["chat_input"] = None

if (selected_option != default_option) and (chat_mode != None):
    # chat_input = st.text_input("Type your message:", "", key="chat_input", on_change=handle_input)
    chat_input = st.chat_input(placeholder="Type your message:", disabled=st.session_state["processing"])
    
    if chat_input:
        st.session_state["processing"] = True
        st.session_state["chat_input"] = chat_input
        st.rerun()
        # Add user message
    
    # print(st.session_state["processing"])
    if st.session_state["processing"]:
        chat_input = st.session_state["chat_input"]
        selected_product = selected_option
        print("I am here")
        print(selected_option)
        st.session_state['messages'].append({"sender": "user", "content": chat_input})

        # Add bot reply
        if st.session_state["chat_mode"] == "Pricing":
            query_header = f"The product in context is {selected_product}."
            print(query_header)
            print(chat_input)
            query_input = query_header + chat_input
            bot_reply, st.session_state.thread = process_query(query=query_input, thread=st.session_state.thread, assistant=assistant)

        else:
            bot_reply = fetch_reviews(query=chat_input, product=selected_product)
        st.session_state['messages'].append({"sender": "bot", "content": bot_reply})

        with st.chat_message("human"):
            st.markdown(chat_input)
        
        with st.chat_message("ai"):
            st.markdown(bot_reply)

        st.session_state["processing"] = False
        st.rerun()

        
else:
    st.markdown(
    """
    <div style="text-align: center; font-size: 18px; line-height: 1.6;">
        <strong>Please select a product and a service to activate chat mode!</strong><br>
    </div>
    """,
    unsafe_allow_html=True
)
    

st.markdown('</div>', unsafe_allow_html=True)
