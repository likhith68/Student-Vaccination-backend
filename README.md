**Backend Setup (Django)**
cd backend
python -m venv env
source env/bin/activate (On Windows use: env\Scripts\activate)
pip install -r requirements.txt


**Run migrations and create superuser:**
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser 


**Start the development server:**
python manage.py runserver
The API will be accessible at: http://127.0.0.1:8000/
