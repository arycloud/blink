#Introduction

BLINK is a Learning Management System built on top of Django (3.1).
It allows the Instructors to create courses, add modules and content of various types like 
Audio, Video , Images and Text. As an Instructor you must have the 
privileges to create, edit and delete courses.
Also, it allows Students to take course , thay can register and search for courses then add to their accounts.


## Setup

1. You must have Python3 installed on your system
2. Django (3.1) is the second requirement you need to fullfill.
3. Clone the repository by running the command as:

    `git clone https://github.com/arycloud/blink.git`
    
## Installation
1. Create the virtual environment with the command:
    
    `virtualenv venv -p python3`
2. Log into the environment directory and activate the environment:
    
    `source venv/bin/activate`
3. Install required packages:

    `pip install -r requirements`
    
4. The repository includes all the requirements, so you don't need to run
database migrations, but if you make changes in models, you should run:

    `python manage.py makemigrations`
    
    `python manage.py migrate`
5. Now you can run the project as:

    `python manage.py runserver`

6. Access the site at: 
    http://127.0.0.1:8000/
     