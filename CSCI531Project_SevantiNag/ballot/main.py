#importing libraries to support voting by a user
from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import passlib.hash
import hashlib
from hashlib import sha256
import sqlite3

#Block Class being the block item of the blockchain
class Block:
    #Instantiating block properties
    blockNo = 0
    voter = None
    candidate = None
    next = None
    hash = None
    nonce = 0
    #Hexa decimal hash instantiated
    previous_hash = 0x0
    timestamp = datetime.datetime.now()
    
    def __init__(self, voter, candidate):
        self.voter = voter
        self.candidate = candidate
    
    def hash(self):
        #SHA256 hasing
        h = hashlib.sha256()
        #Encoding values in UTF-8 for hashing
        h.update(
        str(self.nonce).encode('utf-8') +
        str(self.voter).encode('utf-8') +
        str(self.candidate).encode('utf-8') +
       
        #Using hash of previous block in the current block to form blockchain
        str(self.previous_hash).encode('utf-8') +
        str(self.timestamp).encode('utf-8') +
        str(self.blockNo).encode('utf-8')
        )
        return h.hexdigest()
    
    def __str__(self):
        return "Block Hash: " + str(self.hash()) + "\nBlockNo: " + str(self.blockNo) + "\nBlock Voter: " + str(self.voter)+ "\nBlock Candidate: " + str(self.candidate) + "\nHashes: " + str(self.nonce) + "\n--------------"

class Blockchain:
    diff = 20
    
    maxNonce = 2**32
    target = 2 ** (256-diff)

    #Creating first block
    block = Block("Genesis","Independent")
    head = block

    #Adding a New Block to Block Chain Network
    def add(self, block):
        #Updating Variables for the Next Iteration
        block.previous_hash = self.block.hash()
        block.timestamp = self.block.timestamp
        block.blockNo = self.block.blockNo + 1
        self.block.next = block
        self.block = self.block.next
        
    #Mining blocks 
    def mine(self, block):
        for n in range(self.maxNonce):
            if int(block.hash(), 16) <= self.target:
                self.add(block)
                break
            else:
                #Updating the Nounce if none exist
                block.nonce += 1


#Starting the Flask app
app = Flask(__name__)

#Salt for password encrypyion
salt="8sFt66rZ"
app.secret_key = 'your secret key'

# Database to store voter information
conn = sqlite3.connect('../voting.db', check_same_thread=False)
cur = conn.cursor()


# Blockchain variable for Blockchain class
blockchain = Blockchain()

#Creating Database to store voting block information: Voter's ID, Candidate's name, timestamp, previous hash and nonce
cur.execute('CREATE TABLE IF NOT EXISTS ballot(reg_index INTEGER PRIMARY KEY AUTOINCREMENT, voter text, candidate text, timestamp text, prev_hash text, nonce text)')  

#Add First block to DB if it doesn't exist
cur.execute("SELECT voter FROM ballot WHERE voter=?",("Genesis",))
result = cur.fetchall()
if not result:
    cur.execute('INSERT INTO ballot (voter, candidate, timestamp, prev_hash, nonce) VALUES (?,?,?,?,?)', (blockchain.head.voter, blockchain.head.candidate, blockchain.head.timestamp, blockchain.head.previous_hash,blockchain.head.nonce,))
    conn.commit()

#Login page for Ballot
@app.route('/ballot_login/', methods=['GET', 'POST'])
def ballot_login():
    # Output message
    msg = ''
    # Check if "Voter ID" and "password" POST requests exist
    if request.method == 'POST' and 'generate_id' in request.form and 'password' in request.form:
        
        # Create variables for easy access
        username = request.form['generate_id']
        password = request.form['password']
        crypted_pw = passlib.hash.apr_md5_crypt.hash(password, salt=salt)
         
        # Check if account exists using SQL
        cur.execute('SELECT * FROM account WHERE (generate_id=?)', (username,))
        
        # Fetch one record and return result
        account = cur.fetchone()
       
        # Check if already access and voted using SQL
        cur.execute('SELECT voter FROM ballot WHERE (voter=?)', (username,))
        voted = cur.fetchall()
        # If account exists in accounts table in database
        if account:
            #If encrypted password matches entered password
            if(crypted_pw == account[4]):
                if voted:
                    msg = 'Already voted'
                
                else:
                # Create session data to pass to other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[5]
                # Redirect to home page
                    return redirect(url_for('ballot_home'))
            else:
                msg = 'Incorrect username/password!'
        else:
            # Account doesnt exist or password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message 
    return render_template('ballot_login.html', msg=msg)



# Voting page
@app.route('/ballot_home', methods=['GET', 'POST'])
def ballot_home():
    
    #If user is casting the vote
    if request.method == 'POST':
        # Create variables for easy access
        voter = session["username"]
        candidate = request.form["candidate"]

        #Mining the block to add to blockchaining
        blockchain.mine(Block(voter,candidate))
        blockchain.head = blockchain.head.next

        #Adding the mined block to the Database
        cur.execute('INSERT INTO ballot (voter, candidate, timestamp, prev_hash, nonce) VALUES (?,?,?,?,?)', (blockchain.head.voter, blockchain.head.candidate, blockchain.head.timestamp, blockchain.head.previous_hash,blockchain.head.nonce,))
        conn.commit()

        msg = 'Your Vote has been registered.'
        return redirect(url_for('ballot_submit'))
    #Render Home Page
    return render_template('ballot_home.html')

#Confirmation page to show users that their vote has been casted and end their session
@app.route('/ballot_submit', methods=['GET', 'POST'])
def ballot_submit():
    cur.execute('SELECT candidate FROM ballot WHERE (candidate=?)', (session['username'],))
    candidate_name = cur.fetchall()
    if request.method == 'POST':
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('ballot_login'))
    return render_template('ballot_submit.html',candidate_name=candidate_name)


#Page where all the vites have been tallied
@app.route('/tally')
def tally():
    cur.execute('SELECT candidate, COUNT(*) FROM ballot GROUP BY candidate ORDER BY 2 DESC')
    ballot_value = cur.fetchall()
    return render_template('tally.html',ballot_value=ballot_value)



