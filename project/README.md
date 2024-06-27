# Blogg-50
#### Video Demo:  <https://youtu.be/weLTMD60lxw>
#### Description:
Blogg-50 is a comprehensive blogging platform developed as the final project for Harvard's CS50x course. The platform allows users to create, manage, and interact with blog posts, providing a full suite of features typically found in modern blogging applications. This README aims to provide a thorough overview of the project, including its functionality, the technologies used, and the design choices made during development.

## 1. Project Overview:
Blogg-50 is designed to be a user-friendly platform where users can register, log in, log out, change their password and manage their blog posts such as sharing, updating, deleting etc. It supports user profiles, post categorization, a comments and sub comments system, a like and dislike system, a follow and unfollow system, a search system and so much more. The project emphasizes a clean user interface and robust back-end functionality to ensure a seamless user experience.

## 2. Features
  - **Register and Log In:** Secure user registration and login with username uniqueness and password validation. Passwords are hashed for security.
  
  - **Password Management:** Users can securely change passwords, ensuring the new password matches the old one and inputs are validated.
  
  - **Profile Management:** Users have a profile page with an image, bio, join date, followers, followings, and post count. Users can update their profiles with images and bios.
  
  - **Blog Posts Management:** Create, update, and delete posts. Supports rich text formatting, image uploads, and ensures users can only edit their own posts.
  
  - **Comments and Sub Comments Management:** Users can comment and reply on posts. They can update or delete only their comments and sub-comments, with all inputs validated.
  
  - **Likes and Dislikes Management:** Users can like or dislike posts, with the option to remove or switch likes/dislikes. Counts of likes and dislikes are displayed.
  
  - **Follow and Unfollow Management:** Users can follow or unfollow others, with follow information displayed on profile pages. Users cannot follow themselves.
  
  - **Search Functionality Management:** A search bar on the navigation bar filters posts and users using SQL's "LIKE" clause.
  
  - **Filtering Management:** Posts can be filtered by categories like Video Games, Life, Traveling, Fashion, and Science.
  
  - **Feedbacks of Tranactions:** Uses Flask's "flash" function to feedback users of actions such as "Post liked."
  
  - **Require Login For Some Pages:** Blogg-50 uses a decorator called "login_required" similar as finance problem in week 9.

  ## 3. Technologies Used
- **Flask:** A lightweight WSGI web application framework in Python used for the backend.

- **SQLite:** A C-language library that provides a lightweight, disk-based database. It is used as the database for the project.

- **Jinja:** A template engine for Python used for rendering HTML.

- **Bootstrap:** A front-end framework for developing responsive and mobile-first websites.

- **JavaScript:** Used for enhancing the interactivity and functionality of the web application, such as smooth scrolling and dynamic content updates.

- **HTML & CSS:** Markup and styling languages used for the structure and design of the web application.

## 4. File Structure
- **static:** Directory containing static files like CSS and images.
  - **styles.css:** Contains base styling for layout.html, uses Google's "roboto" font for texts.
  - **images:** By default contains "default.png" for default post cover image and "default_profile.jpg" for user profile image.

- **templates:** Directory containing HTML templates rendered by Flask.
  - **layout.html:** Contains the layout of Blogg-50. This html file links some css and js files such as custom "styles.css" file, Bootstrap's css and Javascript files, custom Jinja2 stylings and finally FontAwesome's css file. This file also contains a Javascript code for sliding smoothly to the footer part.
  - **login.html:** Contains a login form for logging the user into Blogg-50.
  - **register.html:** Contains a register form for registering user an account.
  - **change_password.html:** Contains a change passsword for changing password on account.
  - **about.html:** Contains information part for about link on navigation bar.
  - **blog.html:** Contains information part for blog link on navigation bar.
  - **index.html:** Home page that contains the welcome message such as "Hello, user" and contains the sorted posts by "all posts, latest posts and popular posts".
  - **new_post.html:** Contains a new post form for sharing post.
  - **update_post.html:** Contains a update post form for updating post.
  - **posts_by_category.html:** Contains posts for corresponding filtered category.
  - **detailed_post.html:** Contains details of a particular post such as cover image, author, publish date etc.
  - **show_comments.html:** Contains information of comments and sub comments for a particular post.
  - **publish_comment.html:** Contains a publish comment form for particular post.
  - **publish_sub_comment.html:** Contains a publish sub comment form for particular comment.
  - **update_comment.html:** Contains a update comment form for particular comment.
  - **update_sub_comment.html:** Contains a update sub comment form for particular comment.
  - **search.html:** Contains search results for entered input. These results are for posts and users.
  - **profile.html:** Contains profile page for users
  - **update_profile.html:** Contains a update profile form for updating profile by profile image and bio.
  - **followers.html:** Contains the list for follower users of logged in user.
  - **following.html:** Contains the list for following users of logged in user.

- **tables:** Directory containing SQL tables for showcase
  - **users.sql:** Contains a table for users and index for username.
  - **posts.sql:** Contains a table for posts and index for user id.
  - **comments.sql:** Contains a table for comments and index for comment.
  - **sub_comments.sql:** Contains a table for sub comments.
  - **likes.sql:** Contains a table for likes and index for post id.
  - **follows.sql:** Contains a table for follow transactions and index for follower id and following id.
 
- **flask_session:** Session data.

- **__pycache__:** Python bytecode files.

- **app.py:** Contains the main logics and routes to run Blogg-50 properly such as "register, login, new_post" routes and so much more.

- **helpers.py:** Contains "login_required" decorator.

-  **project.db:** Database file for running SQL queries that in app.py file.

-  **requirements.txt:** Text file that showing must download libraries in order to run Blogg-50 without an issue.

-  **README.md:** Text file for informing users about Blogg-50.

## 5. Design Choices
I chose Flask for its simplicity and flexibility, SQLite for its lightweight nature, and Bootstrap for responsive design. Key decisions include using cs50's SQL class for database interactions and Jinja for templating. The login_required decorator ensures security for sensitive routes. Feedbacks are managed using Flask's flash function, enhancing user experience with real-time feedback.

## 6. Conclusion
Blogg-50 provides a robust and user-friendly platform for blogging, incorporating a wide range of features to enhance the user experience. Through careful design choices and the use of modern technologies like Flask, SQLite, and Bootstrap, the project successfully delivers a comprehensive solution for creating and managing blog content. Future enhancements could include more advanced search functionalities, additional customization options for user profiles, and the integration of more social features to further engage users. Overall, Blogg-50 demonstrates a solid understanding of web development principles and offers a strong foundation for further development and improvements.
