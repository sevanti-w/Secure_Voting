# Secure_Voting
Secure Voting Using Blockchain in Python

1. Flask has been used to deploy the code to a local server to build the system. Some of its libraries to link HTML templates to the functionalities, server requests, and session has been added.
2. DatetimelibraryhasbeenaddedtoprovidetimestampstothevotingBlocks
3. Librarypasslib.hashhasbeenaddedtocreatemd5hashesoftheuser’sloginpasswordandcomparethe
logged in password with the stored hashed password.
4. HashLiblibraryhasbeenused,anditsSHA-256functionalityhasbeenimported.Thisistohashthe
previous blocks of the blockchains
5. sqlite3libraryhasbeenusedtocreateSQLdatabasesandstoredatainthem.
6. requestshavebeenaddedfortheHTMLpagestocommunicatewiththePythonfunctions
7. pip has been used in the project to install the necessary files
______________________________________________________________________________________________________________________________
1. Make sure Python is updated to latest version by using python3 -V
2. Download pip by “curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py “
or upgrade using “python -m pip install --upgrade pip”
3. Navigate to project folder to install virtual environment to run the project in virtual environment. Steps
found here https://sourabhbajaj.com/mac-setup/Python/virtualenv.html
For Windows, the last step would be” venv\Scripts\activate”
4. Install the requirements using “pip install -r requirements.txt”
5. Connect the Flask app to the main.py pages of both ballot and login: “export FLASK_APP=main.py”
For windows it will be: “set FLASK_APP=main.py”
6. Navigate to Login folder
7. Use “Flask run”
8. Navigate to registration page http://127.0.0.1:5000/login/register
9. Make a note of Generated ID in Profile page.
   
10. ClosetheserverandnavigatetoBallotfolder
11. RuntheFlaskappbyFlaskrun
12. NavigatetoBallotLoginpagehttp://127.0.0.1:5000/ballot_login 13. To Find the tallied votes, http://127.0.0.1:5000/tally

