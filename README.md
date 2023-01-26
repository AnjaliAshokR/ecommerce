# Ecommerce Website Repository
This repository contains the code for an ecommerce website built using Python Django and PostgreSQL and deployed on Amazon Web Services (AWS). The website allows users to browse and purchase products, view their order history, manage their account information, and includes an admin panel for managing products, orders, and customers.
## Table of Contents
1. Django project code (located in /ecommerce_mini)
    - Django apps for handling user and product data
    - Database models for PostgreSQL
2. Scripts (located in /scripts)
    - Scripts for setting up and populating the database with sample data
## Getting Started
To get started with the repository, clone it to your local machine: git clone https://github.com/AnjaliAshokR/ecommerce.git

## Dependencies
The following software is required to run the code in this repository:

  - Python (3.x)
  - Django
  - PostgreSQL
  - virtualenv (optional but recommended)
## Usage
To run the website locally, first create a virtual environment and activate it, then run the following command: pip install -r requirements.txt

Next, you will need to set up a PostgreSQL database and update the settings in the settings.py file to match your database configuration. After that, you can create the necessary tables in the database by running the following command:
- python manage.py makemigrations
- python manage.py migrate
To populate the database with sample data, you can run the script located in /scripts
- python populate_db.py
Finally, you can start the development server by running:
- python manage.py runserver
The website should now be running at http://localhost:8000/. The admin panel can be accessed at http://localhost:8000/admin/

## Contribution
If you want to contribute to this repository, please follow the following steps:

1. Fork the repository
2. Create a new branch for your changes (e.g. git checkout -b new-feature)
3. Make your changes and commit them (e.g. git commit -am 'Added product reviews feature')
4. Push the branch to your fork (e.g. git push origin new-feature)
5. Create a new Pull Request

## Acknowledgements
This project was inspired by the following tutorials and resources:
- https://www.javatpoint.com/django-tutorial
- https://medium.com/tinkerhub-mes-marampally/python-django-complete-roadmap-968dbbe4bfac
- https://medium.com/@humble_bee/django-basics-for-a-beginner-5d864e6aa084
