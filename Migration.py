import streamlit as st
import os
# import openai
from openai import OpenAI
import json
import boto3
from streamlit_option_menu import option_menu
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()






# def fetch_data(link):
#     with open(link, 'r',encoding='utf-8') as file:
#         content = json.load(file)
#     return content

def fetch_data(file_path):
    # Replace these with your AWS credentials
    access_key = os.getenv("ACCESS_KEY")
    secret_access_key = os.getenv("SECRET_ACCESS_KEY")
    region_name = 'ap-south-1'

    # Replace with your bucket and file details
    bucket_name = 'saas-reviews'
    object_key = file_path

    # Create an S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name,
    )

    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"].read()
    return json.loads(content.decode("utf-8"))

### DEFINING ARBITARY##
software=''
migrated_from_product,migrated_towards_product=[],[]


###FUNCTIONS######################################################################################
def render_review(summary, content, sentiment):
    """
    Render the HTML for a review based on sentiment.
    Parameters:
    - summary: Summary of the review.
    - content: Full content of the review.
    - sentiment: Sentiment score (1 for positive, -1 for negative, 0 for neutral).

    Returns:
    - A tuple of strings (summary_html, content_html).
    """
    styles = {
        1: {"bg_color": "#d4edda", "text_color": "#155724"},
        -1: {"bg_color": "#f8d7da", "text_color": "#721c24"},
        0: {"bg_color": "#fff3cd", "text_color": "#856404"},
    }
    style = styles.get(sentiment, styles[0])

    summary_html = f"""
    <div style="background-color: {style['bg_color']}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
        <p style="color: {style['text_color']}; font-size: 16px; margin: 0;">{summary}</p>
    </div>
    """

    content_html = f"""
    <div style="background-color: {style['bg_color']}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
        <p style="color: {style['text_color']}; font-size: 16px; margin: 0;">{content}</p>
    </div>
    """
    return summary_html, content_html

def formatting(software,query_engine_response_to_from,mtp,mfp):
    col1, col2 = st.columns(2)
    # Add content to the first column
    with col2:
        st.markdown(f"<span style='color: green; font-weight: bold;'>**Reason for Switching to {software}**</span>", unsafe_allow_html=True)
        for point in query_engine_response_to_from['migrated_towards_product']:
            with st.expander(f"**{point['title']}**"):
                st.markdown(f"{point['body']}")
                str1=[]
                for ref in point['ref']:
                    str1.append(f"[{linkify_numbers([ref-1])}]")
                result = ','.join(str1)
                st.markdown(result)

    # Add content to the second column
    with col1:
        st.markdown(f"<span style='color: red; font-weight: bold;'>**Reason for Switching from {software}**</span>", unsafe_allow_html=True)
        for point in query_engine_response_to_from['migrated_from_product']:
            with st.expander(f"**{point['title']}**"):
                st.markdown(f"{point['body']}")
                str1=[]
                for ref in point['ref']:
                    str1.append(f"[{linkify_numbers([ref-1])}]")
                result = ','.join(str1)
                st.markdown(result)

    st.markdown("______________________")
    st.markdown(f"<span style='color: red; font-weight: bold;'>**Reviews highlighting Switching from {software}**</span>", unsafe_allow_html=True)
    for review in mfp:
        # st.markdown(f'<a name="{review["id"]}"></a>', unsafe_allow_html=True)
        st.markdown(f"<a name=\"{review['id']-1}\"></a>", unsafe_allow_html=True)

        st.markdown(review['summary'])
        if 'body' in review.keys():
            st.markdown(f"[{review['id']}] |Platform : Reddit/{review['subreddit']} | {review['created_utc'].split()[0]} | [Open Review]({review['url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['body'])
        elif 'content' in review.keys():
            st.markdown(f"[{review['id']}] |Platform : Quora | {review['ts_created'].split('T')[0]} | [Open Review]({review['url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['content'])
        else:
            st.markdown(f"[{review['id']}] |Platform : G2 | {review['date'].split('T')[0]} | [Open Review]({review['review_url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['review_content'])
        st.markdown("-----")


    st.markdown(f"<span style='color: green; font-weight: bold;'>**Reviews highlighting Switching to {software}**</span>", unsafe_allow_html=True)
    for review in mtp:
        # st.markdown(f"<a name="{review['id']}"></a>", unsafe_allow_html=True)
        st.markdown(f"<a name=\"{review['id']-1}\"></a>", unsafe_allow_html=True)

        st.markdown(review['summary'])
        if 'body' in review.keys():
            st.markdown(f"[{review['id']}] | Platform : Reddit/{review['subreddit']} | {review['created_utc'].split()[0]} | [Open Review]({review['url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['body'])
        elif 'content' in review.keys():
            st.markdown(f"[{review['id']}] |Platform : Quora | {review['ts_created'].split('T')[0]} | [Open Review]({review['url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['content'])
        else:
            st.markdown(f"[{review['id']}] |Platform : G2 | {review['date'].split('T')[0]} | [Open Review]({review['review_url']}) | [Go Back](#{10000})")
            with st.expander("View Full Review"):
                st.markdown(review['review_content'])
        st.markdown("-----")


def search_product(product):
    product_lower = product.strip().lower()
    vector = [
        int(product_lower in all_databases["g2"]),
        int(product_lower in all_databases["reddit"]),
        int(product_lower in all_databases["quora"]),
    ]
    return vector




def json_percent(file,percentage,source):
    with open(file, 'r',encoding='utf-8') as f:
        data = json.load(f)
    if source=='G2':
        data = data[0]['reviews'][:int(percentage*len(g2_data[0]['reviews']))]
    elif source=='Reddit':
        data = data['reviews'][:int(percentage*len(data['reviews']))]
    elif source=='Quora':
        data = data[:int(percentage*len(data))]
    return data



def fitment_widget(name,circle_value):
    with st.container():
        # Outer border with CSS styling
        st.markdown(
            f"""
            <style>
            .outer-border {{
                border: 3px solid #888888;
                border-radius: 10px;
                padding: 9px;
                width: 220px;
                margin: auto;
                background-color: #333333;
                color: #FFFFFF;
            }}
            .circle-border {{
                border: 6px solid #FFA500;
                border-radius: 40%;
                width: 80px;
                height: 80px;
                display: flex;
                justify-content: center;
                align-items: center;
                font-weight: bold;
                font-size: 1.3em;
                color: #FFA500;
                background-color: #444444;
            }}
            .inline-icon {{
                border: 1px solid #FFFFFF;
                border-radius: 50%;
                padding: 200px 50px;
                font-size: 12px;
                color: #FFA500;
            }}
            .review-button {{
                background-color: #FFA500;
                color: #333333;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                cursor: pointer;
                text-align: center;
            }}
            .review-button:hover {{
                background-color: #FF8C00;
            }}
            a {{
                color: #FFA500;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .wiz-heading {{
                
                font-size: 1em;
                color: #FFFFFF;
            }}
            </style>
            <div class="outer-border">
                <div style="display: flex; justify-content: space-between; align-items: top;">
                    <h2 class="wiz-heading" style="margin: 0;">{name}</h2>
                    <div class="circle-border">{circle_value}/10</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def migration_analysis(software_name):
    software=software_name
    ### Data Loading
    g2_data,quora_data,reddit_data=[], [], []
    vect1=search_product(software)
    # st.markdown(vect1)
    if vect1[0]==1:
        g2_data=fetch_data('Dataset/'+software+'/g2.json')
        company_name=software
    if vect1[1]==1:
        reddit_data=fetch_data('Dataset/'+software+'/reddit.json')
        company_name=software
    if vect1[2]==1:
        quora_data=fetch_data('Dataset/'+software+'/quora.json')
        company_name=software
    ### Data Loading

    migrated_towards_product,mtp,migrated_from_product,mfp=[],[],[],[]
    i=1

    if vect1[1]==1:
        for review in reddit_data['reviews']:
            temp={}
            if review['migration']==-1 and review['score']>=threshold_reddit:
                temp['id']=i
                temp['body']=review['body']
                migrated_from_product.append(temp)
                review['id']=i
                mfp.append(review)
                i+=1
    if vect1[2]==1:
        for review in quora_data:
            temp={}
            if review['migration']==-1 and review['score']>=threshold_quora:
                temp['id']=i
                temp['body']=review['content']
                migrated_from_product.append(temp)
                review['id']=i
                mfp.append(review)
                i+=1
    if vect1[0]==1:
        for review in g2_data[0]['reviews']:
            temp={}
            if review['migration']==-1 and review['score']>=threshold_g2:
                temp['id']=i
                temp['body']=review['review_content']
                migrated_from_product.append(temp)
                review['id']=i
                mfp.append(review)
                i+=1

    if vect1[1]==1:
        for review in reddit_data['reviews']:
            temp={}
            if review['migration']==1 and review['score']>=threshold_reddit:  
                temp['id']=i
                temp['body']=review['body']
                migrated_towards_product.append(temp)
                review['id']=i
                mtp.append(review)
                i+=1
    if vect1[2]==1:
        for review in quora_data:
            temp={}
            if review['migration']==1 and review['score']>=threshold_quora:  
                temp['id']=i
                temp['body']=review['content']
                migrated_towards_product.append(temp)
                review['id']=i
                mtp.append(review)
                i+=1
    if vect1[0]==1:
        for review in g2_data[0]['reviews']:
            temp={}
            if review['migration']==1 and review['score']>=threshold_g2: 
                temp['id']=i
                temp['body']=review['review_content']
                migrated_towards_product.append(temp)
                review['id']=i
                mtp.append(review) 
                i+=1

    ### MIGRATION PROMPT TEMPLATE####################################################################
    migration_format='{"migrated_from_product":[{"title":"3-4 word summary of reason1","body":"Reason1 for migration from {software}","ref":[id]},{"title":"3-4 word summary of reason2","body":"Reason2 for migration from {software}","ref":[id]},{"title":"3-4 word summary of reason3","body":"Reason3 for migration from {software}","ref":[id]},{"title":"3-4 word summary of reason4","body":"Reason4 for migration from {software}","ref":[id]},{"title":"3-4 word summary of reason5","body":"Reason5 for migration from {software}","ref":[id]}],"migrated_towards_product":[{"title":"3-4 word summary of reason1","body":"Reason1 for migration to {software}","ref":[id]},{"title":"3-4 word summary of reason2","body":"Reason2 for migration to {software}","ref":[id]},{"title":"3-4 word summary of reason3","body":"Reason3 for migration to {software}","ref":[id]},{"title":"3-4 word summary of reason4","body":"Reason4 for migration to {software}","ref":[id]},{"title":"3-4 word summary of reason5","body":"Reason5 for migration to {software}","ref":[id]}]}'

    system_prompt_migration = f"""
    You are given a list of reviews where users have mentioned that they have migrated to another software from {software} as well as reviews mentioning migration from another software to {software}.
    You need to extract excatly 5 reasons for migration to {software} and excatly 5 reasons for migration from {software} as mentioned in the reviews and include the ID associated with each reason.

    The output should strictly be a JSON in the following format:
    {migration_format}
    Ensure that each reason includes atmost 3 and atleast 2 of its associated ID from the reviews, and the output should be a single string in valid JSON format without using /n or 'json'.

    list of reviews that mentions migration from {software} to other software: {migrated_from_product}
    list of reviews that mentions migration to {software} from other software: {migrated_towards_product}
    
    Ensure the output strictly adheres to this structure and contains no extraneous characters, line breaks, or formatting,/n or '''json.The ouput should be a single string with the json format.

    """
    ### MIGRATION PROMPT TEMPLATE####################################################################
    response = client.chat.completions.create(
                    model="gpt-4o",  # Use "gpt-3.5-turbo" or "gpt-4" based on your need
                    messages=[
                        {"role": "system", "content": system_prompt_migration},
                    ],
                    temperature=1
                )
    query_engine_response_to_from=response.choices[0].message.content
    # st.markdown(query_engine_response_to_from)
    mod_query_engine_response_to_from=json.loads(query_engine_response_to_from)
    
    return mod_query_engine_response_to_from,mtp,mfp
    





###FUNCTIONS######################################################################################


# tools = ["Adobe", "Airtable", "Amplitude", "Ansible", "AppDynamics", "Asana", "Atlassian", "AWS", "Azure", "BambooHR", "Basecamp", "BigCommerce", "Bitbucket", "Box", "Braze", "Buddy", "Calendly", "Chef", "CircleCI", "ClickUp", "Confluence", "Crowdstrike", "DataDog", "DigitalOcean", "Docker", "DocuSign", "Dropbox", "Druva", "Dynatrace", "ElasticSearch", "Figma", "Firebase", "Freshdesk", "Freshworks", "GCP", "Github", "Gitlab", "Gong", "Grafana", "Gusty", "Heroku", "Hubspot", "Intercom", "Jamf", "Jenkins", "JFrog", "Jira", "Kubernetes", "Linode", "Looker", "Lucidchart", "Miro", "Mixpanel", "Monday", "MongoDB", "Netlify", "Nginx", "Notion", "Nutanix", "Octopus Deploy", "Okta", "PagerDuty", "Palo Alto", "Panther", "Pluralsight", "Postman", "Prometheus", "Puppet", "Qualtrics", "QuickBooks", "Rippling", "Salesforce", "Sentry", "ServiceNow", "Shopify", "Slack", "Smartsheet", "Snowflake", "SonarQube", "Splunk", "Square", "Stripe", "Tableau", "TeamCity", "Terraform", "TravisCI", "Trello", "Twilio", "UpCloud", "Vanta", "Vercel", "VMware", "Wiz", "Workday", "Zendesk", "Zoho", "Zoom"]
tools = ["Confluence", "Notion", "Box", "Dropbox"]
sizes=["Small","Medium","Enterprise",'All']

###CRIDENTIALS###################################################################################

###CRIDENTIALS###################################################################################

###PAGE LAYOUT ###################################################################################

st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .jazzee-title {
        display: inline;
        background: linear-gradient(93.59deg, orange 3.13%, #f6be58 85.77%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5em;
        font-weight: bold;
    }
    .email-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create the header with the title and button
st.markdown(
    """
    <div class="header-container">
        <h1><span class="jazzee-title">Jazzee</span> Assist</h1>
        <a href="mailto:jazzee@example.com?subject=Query" target="_blank">
            <button class="email-button">Email Jazzee</button>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 200px;  /* Adjust the width here */
    }
    </style>
    """,
    unsafe_allow_html=True
)

software = st.selectbox("Choose the software:", tools)


# Horizontal radio buttons
size = option_menu(
    menu_title=None,  # No title for the menu
    options=["SMB", "Mid Market", "Enterprise", "General"],  # Menu options
    icons=["shop", "building", "globe", "cogs"],  # Icons for each option
    menu_icon="briefcase",  # Icon for the menu (can be any relevant icon)
    default_index=3,  # Default selected option
    orientation="horizontal",  # Horizontal layout
    styles={
        "container": {"padding": "0", "background-color": "#f0f0f5"},
        "icon": {"color": "#000000", "font-size": "20px"},  # Blue icons for visibility
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#d1e7ff",  # Light blue hover effect
            "color": "#333333",  # Dark text color for better contrast
        },
        "nav-link-selected": {
            "background-color": "#007bff",  # Blue background for selected option
            "color": "white",  # White text when selected
        },
    },
)
if size=='SMB':
    size='Small'
if size=='Mid Market':
    size='Medium'
if size=='Enterprise':
    size='Enterprise'

###PAGE LAYOUT ####################################################################################


# size = st.selectbox("Choose size of organization", sizes)
# threshold_g2 = st.slider('Select threshold for G2', 0.0, 10.0, 9.5)
# threshold_quora=st.slider('Select threshold for Quora', 0.0, 10.0, 7.0)
# threshold_reddit=st.slider('Select threshold for Reddit', 0.0, 10.0, 6.0)





###PARAMETERS######################################################################################
threshold_g2=9.5
threshold_quora=7.0
threshold_reddit=5.5
###PARAMETERS######################################################################################
    





### CREATION OF UNIFORM DB####################################################################    
with open("g2.txt", "r") as file:
    g2_db = set(file.read().strip().lower().splitlines())  # Convert to lowercase for uniformity
with open("quora.txt", "r") as file:
    quora_db = set(file.read().strip().lower().splitlines())
with open("reddit.txt", "r") as file:
    reddit_db = set(file.read().strip().lower().splitlines())
# Combine data for unified searching
all_databases = {"g2": g2_db, "reddit": reddit_db, "quora": quora_db}
### CREATION OF UNIFORM DB####################################################################   





# flag=0
# cont=fetch_data('Saas Price from vendr.json')
# for elem in cont:
#     if elem['Name']==software:
#         price=elem['Price']
#         flag=1
g2_data,quora_data,reddit_data=[], [], []
vect1=search_product(software)
if vect1[0]==1:
    g2_data=fetch_data('Dataset/'+software+'/g2.json')
    company_name=software
if vect1[1]==1:
    reddit_data=fetch_data('Dataset/'+software+'/reddit.json')
    company_name=software
if vect1[2]==1:
    quora_data=fetch_data('Dataset/'+software+'/quora.json')
    company_name=software

def linkify_numbers(numbers):
    return ", ".join([f"[{num+1}](#{num})" for num in numbers])


total_db_g2,total_db_reddit,total_db_quora=[],[],[]
total_db=[]
flag1=1
if size=='All':
    flag1=0
if vect1[0]==1:
    for review in g2_data[0]['reviews']:
        if review['score']>=threshold_g2 and (review['business_use_case']==size.lower() or flag1==0):
            total_db_g2.append(review)
            temp_json= {
                "review":review['review_content'],
            }
            total_db.append(temp_json)
if vect1[1]==1:
    for review in reddit_data['reviews']:
        if review['score']>=threshold_reddit and (review['business_use_case']==size.lower() or flag1==0):
            total_db_reddit.append(review)
            temp_json= {
                "review":review['body'],
            }
            total_db.append(temp_json)
if vect1[2]==1:
    for review in quora_data:
        if review['score']>=threshold_quora and (review['business_use_case']==size.lower() or flag1==0):
            total_db_quora.append(review)
            temp_json= {
                "review":review['content'],
            }
            total_db.append(temp_json)
i=1
for elem in total_db:
    elem['id']=i
    i+=1

# st.markdown(f"Total reviews with score greater than {threshold_quora} are {len(total_db_quora)}")
format='{"Pros":[{"title":3-4 word summary of pro1,"body":pro1,"ref":[id]},{"title":3 word summary of pro2,"body":pros2,"ref":[id]},{"title":3-4 word summary of pro3,"body":pro3,"ref":[id]},{"title":3-4 word summary of pro4,"body":pro4,"ref":[id]},{"title":3-4 word summary of pro5,"body":pro5,"ref":[id]}],"Cons":[{"title":3-4 word summary of con1,"body":con1,"ref":[id]},{"title":3 word summary of con2,"body":con2,"ref":[id]},{"title":3-4 word summary of con3,"body":con3,"ref":[id]},{"title":3-4 word summary of con4,"body":con4,"ref":[id]},{"title":3-4 word summary of con5,"body":con5,"ref":[id]}],"Fitment Score":fitment_score}'



system_prompt = f"""
You are provided with a list of user reviews for {software} software collected from G2, Reddit, and Quora.  
Analyze the reviews to identify **5 key unique pros** and **5 key unique cons** of {software} software. The pros and cons should be insightful and practical, enabling potential buyers to make well-informed decisions about the software.  

Ensure that each pro and con includes atmost 3 most relevant ID . Ensure that the id is from the entire db and not just the top reviews and also the id should refrence the most relevant review which matches with that pro or con.

Also provide a **fitment score** for the software based on the reviews. The fitment score should be a number between 0 and 10, where 0 indicates that the software is not suitable for the user's needs and 10 indicates that the software is a perfect fit.
The output must be a **single JSON string** formatted as follows:  

{format}

Ensure the output strictly adheres to this structure and contains no extraneous characters, line breaks, or formatting,/n or '''json.The ouput should be a single string with the json format.
  
Database size reference: {total_db}
"""

st.markdown("Fitment Rating")
comp=fetch_data('competitor.json')
rating_content=fetch_data('rating1.json')
def generate_score(prod_name,size):
    for elem in rating_content:
        if elem["Name"].lower()==prod_name.lower() and elem["size"]==size:
            return elem['Score']


if software in comp.keys():
    competitors=comp[software]
    # st.markdown(competitors)
    xcv=competitors
if len(competitors)>0:
    xcv = st.columns(min(len(competitors),3))
    for i in range(len(xcv)):
        if i==0:
            with xcv[0]:
                fitment_widget(software,generate_score(software,size.lower()))
        else:
            with xcv[i]:
                fitment_widget(competitors[i-1],generate_score(competitors[i-1],size.lower()))
# st.markdown(generate_score("Adobe","general"))

st.markdown(f'<a name="{10000}"></a>', unsafe_allow_html=True)
tabs = st.tabs([software]+competitors[:(min(2,len(competitors)))])

  # Default active tab

flag=0
if st.button("Show me Migration analysis",key=0):
    flag=1
    with tabs[0]:
                with st.spinner('⏳ Fetching reviews matching the profile'):
                    mod_query_engine_response_to_from,mtp,mfp=migration_analysis(software)
                    # st.markdown(query_engine_response_to_from)
                    formatting(software,mod_query_engine_response_to_from,mtp,mfp)

    for i in range(1,1+min(len(competitors),2)):
        with tabs[i]:
            # if st.button("Show me Migration analysis",key=i):
            if flag==1:
                with st.spinner('⏳ Fetching reviews matching the profile'):
                    software=competitors[i-2]
                    # st.markdown(software)
                    query_engine_response_to_from,mtp,mfp=migration_analysis(software)
                    formatting(software,query_engine_response_to_from,mtp,mfp)
                
