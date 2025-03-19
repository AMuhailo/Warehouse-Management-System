## 📦🔧Warehouse Management System
![Django](https://img.shields.io/badge/Django-4.2-darkgreen?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12.9-blue?style=for-the-badge) ![Celery](https://img.shields.io/badge/Celery-5.4.0-lightgreen?style=for-the-badge) ![Redis](https://img.shields.io/badge/Redis-5.2.1-red?style=for-the-badge)


## Description project
Warehouse Management System (WMS) is a warehouse management system that allows you to add, edit and control products, categories, customers, managers and employees. The project implements CRUD operations, process automation via Celery & Redis, interactive updating of a number of products via QR codes, as well as an API based on the Django REST Framework. Creating a Docker Container for optimization and deployment on RailWay.

🚀Deploy on Railway The project is deployed on Railway. To check the operation of the site, go to the link: 🔗[Warehouse management](https://warehouse-management.up.railway.app/)

## 🚀 Functional
✔️ Goods / Provider / Category(Goods/Workers) / Manager & Worker CRUD CRUD ✔️ Automatically changes the quantity of goods when placing an order ✔️ Automatically renew via Celery & Redis if the product is low  ✔️ Automatic notification about stock of goods ✔️ Adding and checking the quantity of goods using an additional QR code ✔️ Django REST Framework wiki for query processing ✔️ Updating a number of products by scanning a QR code ✔️ Export and import of data in CSV format ✔️ Possibility of attracting new products or lists of customers ✔️ Retrieving a list of products via API ✔️ CRUD operations for categories, post-owners and clients ✔️ Docker Images 

## 🛠️ Technologies
- **Django**
- **PostgreSQL**
- **Celery + Redis**
- **Celery**
- **Django REST Framework (DRF)**
- **CSV**
- **Docker + Docker Container**
- **Railway Deploy**

## 📦 Installation and local launch
1️⃣ Cloning the repository
```bash
git clone https://github.com/AMuhailo/Warehouse-Management-System.git
cd Warehouse-Management-System.git
```

2️⃣ Virtual environment
```bash
python -m venv venv
source venv/bin/activate    # for macOS and Linux
venv\Scripts\activate       # for Windows
```

3️⃣ Installing dependencies
```bash
pip install -r requirements.txt
```

4️⃣ Setting Environment Variables
To run locally, you need to create an .env file in the root folder:
```bash
ENVIRONMENT=local
SECRET_KEY=your_secret_key
DATABASE_URL=your-url
REDIS_URL=your-url
```

⚠️ Don`t upload .env to GitHub!
It needs to be added to .gitignore.

5️⃣ Starting the server
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
The site is now available at http://127.0.0.1:8000.

## ⚡Launching Celery
To allow Celery to run tasks in the background, start it like this:
```bash
docker pull redis
docker run -it --rm --name redis -p 6973:6973 redis
celery -A warehouse worker --loglevel=info
```

## 🔗 API endpoints 
http://127.0.0.1:8000/api/
http://127.0.0.1:8000/api/management/
http://127.0.0.1:8000/api/not-stock/
http://127.0.0.1:8000/api/not-stock/{pk}/
http://127.0.0.1:8000/api/scan-good/{goods_slug}/{goods_pk}/

## [Docker](https://img.shields.io/badge/Docker-27.4.0-turquoise?style=for-the-badge) 📋 Prerequisites 
Ensure you have the following installed:
- **Docker**
- **Docker Compose**
- **Railway deployment**

6️⃣ Build and run the project with Docker Compose:
```bash
docker-compose up --build
```

## 🐋 Docker Containers
The project uses the following containers:
- **web-container**: Django application
- **postgres-container**: PostgreSQL database
- **redis-container**: Redis server for Celery tasks
- **celery-container**: Celery worker for background tasks

## 🔗 Useful commands
💾 Creating a database backup
```bash
python manage.py dumpdata --indent=2 --output=management/fixtures/db_backup.json
```

♻️ Database recovery
```bash
python manage.py loaddata db_backup.json
```

## 📩 Contacts
If you have any questions, suggestions, problems with the project, ideas or proposals - please contact
📧 Email: amuhailo25@gmail.com
👨‍💻 GitHub: AMuhailo