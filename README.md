# SUMMARY
This library app originated as a unit project for the Udacity Full Stack Web 
Developer Nanodegree.  The purpose of the project was to develop a catalogue 
application that stored items with properties on a user basis.  Users can 
login using OAuth2.0 with Google or Facebook login.  Users can track the 
status of the books in their library, add notes, and view the books contained
 in other users' collections.


# REQUIREMENTS
- [Python v2.7.12](https://www.python.org/downloads/release/python-2712/)
- [Flask v0.12.2](https://pypi.python.org/pypi/Flask/0.12.2)
- [SQLAlchemy v1.1.13](https://www.sqlalchemy.org/download.html)
- [OAuth2Client](https://github.com/google/oauth2client)

# INSTRUCTIONS

- Acquire and implement google and facebook API keys
    - Google
        - Go to https://console.developers.google.com/apis in your web browser
        - Log-in, and click on "credentials in the sidebar"
        - Click "Create Credentials" and select "OAuth Client ID"
        - Click "Web Application" and name your credentials for this project
        - Set Javascript origins to "http://localhost:5000" and redirects to 
        "http://localhost:5000/login" and "http://localhost:5000/gconnect"
        - Click "Create", and click the down arrow icon next to the 
        credential to download the credentials as JSON
        - Place this JSON file in the main project directory, and name it 
        "client_secrets.json"
        - after the import section in main.py, set the APPLICATION_NAME 
        variable to the same name as you used in your credentials
        - Paste your google client id in the quotes on line 24 in login.html
    - Facebook
        - Go to https://developers.facebook.com/ in your web browser and 
        login to your Facebook account.  Once logged in, click "my apps" in 
        the upper right corner.
        - Click "Add a new app" and follow the prompts.  Once created hover 
        over "Facebook Login" and click "set up".
        - Click "WWW".  Set the url to "http://localhost:5000" and save.
        - Click "settings" in the left nav bar
        - Add "http://localhost:5000/login" and 
        "http://localhost:5000/fbconnect" to the authorized redirects and 
        click save
        - Click "dashboard" in the upper left, and copy to ID and secret to 
        their respective places in "fb_client_secrets.json"
        - Paste your appid in the quotes on line 73 of login.html

- Set up the database by running the following two commands from the 
directory containing the main.py file.
    - "python database_setup.py"
    - "python lotsofbooks.py"
    
- Start the webserver
    - Confirm the main.py script is in the same directory as the 
    littleelibrary.db database.
    - From console, use command "python main.py" to start server on port 5000
    
- Login and create your collection
    - In a web browser, go to http://localhost:5000 and provide your Google 
    or Facebook credentials.
