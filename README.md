# Quick start
1. Create .env file in repository root folder and add the following: 
```.env
API_ID = your_id
API_HASH = your_hash
```
2. Run main.py file and provide the channel username when prompted!

**Don't forget to install requirements!**

# Complete guide
1. Make sure you have python3 and pip3 installed.
```
python3 --version
```
```
pip3 --version
```
2. Download or clone repository to your local machine.
```bash
git clone https://github.com/wzxcff/APIScraperTG.git
cd APIScraperTG
```
3. Retrieve your API_ID and API_HASH from my.telegram.org (or use the one provided (if any)).
4. Create .env file in repository root folder, and put inside your ID and HASH. Should look like this:
```.env
API_ID = your_id
API_HASH = your_hash
```
5. Create and activate virtual environment (if not activated already), open terminal and run:
```bash
python3 -m venv venv
```
Activate venv (run in the terminal):
  - MacOS/Linux: ```source venv/bin/activate```
  - Windows: ```venv\Scripts\activate```

6. Now using the same terminal, install project requirements:
```bash
pip install -r requirements.txt
```
7. Run main.py file and provide the channel username when prompted.
8. That's it, you're ready to go!
