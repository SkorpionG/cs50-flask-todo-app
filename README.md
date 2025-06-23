# Flask Todo App

## Description

### About

This project is a simple todo app that allow users to create, organize, and track their todo tasks. The user has the option of creating a new account if they don't already have one, or to login with their existing account before they can create or manage their task. After logging in, the user will be redirected to the dashboard page. This page will show tasks that are due within a week. In this app, the user can create new tasks and customize it by:

1. Create a task title
2. Give it a description
3. Set a status (Pending, In Progress, Completed),
4. Set a priority (Low, Medium, High),
5. Set a due date for the task
6. Set one or more tags

Beside the above properties of a task, the app will record the **created time** and **last modified** time of the task. These properties will remain editable throughout the entire lifetime of the task until deleted by the user. In addition, the user will have the ability to sort tasks by priority, status, due date, and created time, as well as filter tasks by priority, status, created time, tags, and by user search. The user also can organize tasks by creating tags. Each task can be associated with multiple tags, and one tag can be associated with multiple tasks. The user can customize a tag by:

1. Give a tag name
2. Set a color coding for easy recognition

Lastly, the app provides a setting page where the user can modify their account settings, including username, email address, password. In the same page, the user can delete their account after entering their current password and confirm the action.

### Frontend Logic

The majority of the code associated with the frontend is located within the "static" and "templates" directories. The "templates" directory is where all the HTML and Jinja templates are located. Within this directory, there are several and html files for different purposes:

- The "auth" folder contain files associated with user authentication pages (such as login and registration).
- The "components" folder contain html components that are reusable throughout the application. These components are simpler in terms of structure, and usually doesn't depend on data coming from the backend.
- The "macros" folder contain jinja macros what works similar to components, except that each html file inside the "macros" folder can contain multiple "macro" that works like a python function. This is because these macros can be imported by other html files using a python-like syntax, and can accept arguments just like a python function. These features sets them apart from what's inside the "components" folder, and makes it easier to manage the complexity of this project and make parts of the code reusable.
- The "user" folder contains pages that are more associated with the majority part of the application, which is not accessible by default unless the user is logged in. These pages include dashboard page, settings page, tasks and tags pages, and forms that will be populated with user information once logged in.
- The reset of the html files inside this folder is some generic html files that display the basic information about the app, rendering the home page (not user dashboard), and defines the base template for all the other pages.

Inside the "static" folder is where all the CSS and JavaScript code is located. Some of the files inside the "css" folder are associated with a particular html template, while others are for application-wide styling. For example, the "flash-messages" css file is required in order to style the "flash-messages" html macro. The same idea applies to the js files inside the "js" folder, where "flash-messages.js" is required add interactivity to flash messages. Some files, like styles.scss and script.js are associated with the entire application, whereas others are for a specific component/template. The assets folder is where all the image assets is stored, such as website logo.

### Backend Logic

Most of the python files outside both the "static" and "templates" folders are associated with with the application's backend logic. What each files does are the follow:

- The app.py is responsible for rendering the index.html, about page, and the user dashboard. It also contains some useful functionality such as context processor and datetime formatting that other part of the backend might need as well.
- The auth.py is responsible for rendering user registration, login, and password reset pages, as well as handle requests for login and account registration.
- The tasks.py is responsible for rendering pages about user tasks, and handle request for creating, editing, updating, and deleting user tasks.
- The tags.py is responsible for rendering pages about user tags, and handle request for creating, editing, updating, and deleting user tags.
- The settings.py is responsible for rendering settings pages, and handle request for updating user profile settings such as username, email, password, and account deletion.
- The validation.py is where functions for email and password validation are defined.
- The navigation.py stores several variables that tells the frontend what pages to display and the corresponding routes, name, and even icons associated with each page.
- The middleware.py contains some flask middleware process the request before it reach the actual routes, such as the login_required middleware that make sure a specific page is only accessible to logged in users. These functions makes the backend code more reusable.
- The init_db.py contain a function that will setup the database file after been executed. It will read the database schema from the **schema.sql**, connect to database.db (where all the user data is stored), drop existing databases if it exists, and recreate the database schema for all tables defined in schema.sql.
- The database.py contains many functions that make interacting with the database easier, and also makes the code to to so much reusable.

### Database

Inside the database.db, there are 3 tables that are responsible for storing user data, which are the **users** table, **tasks** table, **tags** table, and **task_tags** table.

- The **users** table store account related user data, such as email, username, and password hash.
- The **tasks** table store task related to user tasks. Each task is associated with one user and has a user_id field. The tasks table also stores the other various properties associated with a task.
- The **tags** table store tags created by the users. Each tag is associated with one user and has a user_id field. The tags table also stores the name and color coding for each tag.
- The **task_tags** table is a many to many relationship database that join the tasks and tags table. This is because each task can have many tags attached or connected, while each tags can be connected by multiple tasks.

### Notes

Before running the application, be sure to install all the required libraries (listed inside "requirements.txt") and run the init_db.py to initialize the database.
