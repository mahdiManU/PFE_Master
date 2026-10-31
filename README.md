# Legal BPMN Process, Verification

Tool that verifies BPMN models of public administrative processes: it detects
missing information (MI), structural errors (S) and contradictions (C), maps
them to the legal texts and generates a verification report (.docx).

## Requirements
Python 3.11, Node.js LTS, Git.

## Backend
```bash
cd pfe
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
copy .env.example .env         # Linux/Mac: cp .env.example .env  (then fill SECRET_KEY, SIGNING_KEY)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Frontend
```bash
cd pfe/frontend
npm install
npm start
```
Open http://localhost:3000. Log in with the user created above.

## Notes
- The contradiction check C4 uses `googletrans`, which needs an internet connection.
- Verification code is in `pfe/myapp/` (see the code map in docs/).