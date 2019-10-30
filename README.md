## Project Title
NeverBoringBerlin

## Description
NeverBoringBerlin is an item catalog application created for Udacity Full Stack Nanodegree course.
It's a dynamic RESTful web application developed using the Python framework Flask
along with third-party OAuth authentication (Google and Facebook). This application uses
SQLite database.

This application provides a list of items grouped by categories
as well as user registration and authentication system.
Registered users can create, edit and delete their own items.

## Skills
*   Python
*   Flask
*   SQLAchemy
*   Oauth2
*   Google Login
*   Facebook Login
*   HTML
*   CSS

## Project software requirements
*   Text editor, like Sublime or Visual Studio Code
*   Vagrant
*   Virtual Box
*   A terminal application like Bash

## Project structure
*   Database setup - `database_setup.py`
*   Database sample data - `demodata.py`
*   Application business logic - `application.py`
*   Static folder with css style and images - `/static`
*   Templates folder with layouts - `/templates`

## Executing Project
1. Install Vagrant and VirtualBox
2. Clone the vagrant from the Udacity Repo (https://github.com/udacity/fullstack-nanodegree-vm)
3. Clone this repo into the /catalog folder in the /vagrant directory
4. Run vagrant up to run the virtual machine, then vagrant ssh to login to the virtual machine
5. Navigate to the /catalog directory inside the vagrant environment
6. Run `python database_setup.py` to create the database
7. Run `python demodata.py` to populate the database
8. Run `python application.py` and navigate to http://localhost:8000 in your browser

## JSON endpoints
1.  All items grouped by categories: http://localhost:8000/locations-grouped/json
2.  All categories: http://localhost:8000/location-types/json
3.  Selected category: /location-types/<int:category_id>/json, f.e. http://localhost:8000/location-types/1/json
4. All items: http://localhost:8000/locations/json
5. Selected item: /locations/<int:item_id>/json, f.e http://localhost:8000/locations/1/json
6. All users: http://localhost:8000/users/json
7. Selected user: /users/<int:user_id>/json, f.e. http://localhost:8000/users/1/json

## Credits
Udacity Full Stack Web Developer Nano Degree: https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004

## Author
Daria Shyman daria.shyman@gmail.com