from flask import Flask, request, redirect, session, render_template, flash, url_for
from flask_session import Session
from helpers import login_required
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# We are going to need a directory for storing profile photos so we need to create one if we don't have
if not os.path.exists("static/images"):
    os.mkdir("static/images")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """ Home page for Blogg-50"""

    # Welcome message for user like "Hello, user"
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

    # Latest posts
    latest_posts = db.execute("""SELECT posts.*, users.username, 
                                 (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                                 (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count
                                 FROM posts 
                                 JOIN users ON posts.user_id = users.id
                                 ORDER BY publish_date DESC
                             """)

    # Most popular posts
    popular_posts = db.execute("""SELECT posts.*, users.username, 
                                  (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                                  (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count
                                  FROM posts 
                                  JOIN users ON posts.user_id = users.id
                                  GROUP BY posts.id
                                  ORDER BY likes_count - dislikes_count DESC
                              """)

    # All posts
    all_posts = db.execute("""SELECT posts.*, users.username, 
                              (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                              (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count
                              FROM posts 
                              JOIN users ON posts.user_id = users.id
                           """)

    return render_template("index.html", username=username, latest_posts=latest_posts, popular_posts=popular_posts, all_posts=all_posts)


@app.route("/login", methods=["POST", "GET"])
def login():   
    """ Logs the user in """

    if request.method == "POST":
        # Ensuring user entered username and password
        username = request.form.get("username")
        if not username:
            flash("Please provide your username.", "error")
            return render_template("login.html")
        
        password = request.form.get("password")
        if not password:
            flash("Please provide your password.", "error")
            return render_template("login.html")
        
        # Querying database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensuring user entered its username and password correctly
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Oops, your username and/or password is incorrect. Please try again.", "error")
            return render_template("login.html")
        
        # Remembering which user is logged in
        session["user_id"] = rows[0]["id"]

        # Redirecting user to home page
        return redirect("/")
    
    elif request.method == "GET":
        return render_template("login.html")

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/login")
    

@app.route("/logout")
@login_required
def logout():
    """ Logs the user out """

    # Forget the user id
    session.clear()

    # Redirect the user to login page
    return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    """ Registers user into Blogg-50 """

    if request.method == "POST":
        # Ensuring user provided username and password besides confirmed the password
        username = request.form.get("username")
        if not username:
            flash("Please provide a username.", "error")
            return render_template("register.html")
        
        # Ensure username is not a duplicate username
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            flash("That username is already taken. Please enter a different username.", "error")
            return render_template("register.html")
        
        password = request.form.get("password")
        if not password:
            flash("Please provide a password.", "error")
            return render_template("register.html")
        
        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("Please confirm your password.", "error")
            return render_template("register.html")
        
        # Ensuring user confirmed the password correctly
        if password != confirmation:
            flash("Sorry, passwords are not matching. Please try again.", "error")
            return render_template("register.html")
        
        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Store the user in the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password)
        flash("Registered successfully. Please log in.", "success")
        return redirect("/login")
    
    elif request.method == "GET":
        return render_template("register.html")

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/register")
    

@app.route("/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    """ Changes user's password """

    if request.method == "POST":
        # Querying the database for old password
        old_password = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"]

        # Ensuring user entered the new chosen password
        new_password = request.form.get("new_password")
        if not new_password:
            flash("Please provide your new password.", "error")
            return render_template("change_password.html")
        
        # Ensuring user entered the confirmation of new chosen password
        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("Please confirm your new password.", "error")
            return render_template("change_password.html")
        
        # Checking the old and new passwords do not match
        if check_password_hash(old_password, new_password):
            flash("Sorry, the entered passwords are the same. Please enter a different password from before.", "error")
            return render_template("change_password.html")
        
        # Hashing the new password for security
        hashed_new_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)

        # Updating the database with the new password
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_new_password, session["user_id"])

        flash("Password changed successfully. Please log in.", "success")

        # Forget the user id
        session.clear()
        
        # Redirecting user to login
        return redirect("/login")

    elif request.method == "GET":
        return render_template("change_password.html")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/new_post", methods=["POST", "GET"])
@login_required
def new_post():
    """ Provides sharing post """

    if request.method == "POST":
        # Ensuring user provided title, content, category (Required)
        title = request.form.get("title")
        if not title:
            flash("Please provide a title for your post", "error")
            return render_template("new_post.html")
        if len(title) > 50:
            flash("Please provide a title that is less than 100 characters.", "error")
            return render_template("new_post.html")
        
        content = request.form.get("content")
        if not content:
            flash("Please provide content for your post.", "error")
            return render_template("new_post.html")
        
        category = request.form.get("category")
        if not category:
            flash("Please provide a category for your post.", "error")
            return render_template("new_post.html")
        
        # Optional additions
        summary = request.form.get("summary")
        if summary and len(summary) > 100:
            flash("Please provide a summary that is less than 250 characters.", "error")
            return render_template("new_post.html")
        
        tags = request.form.get("tags")
        
        cover_image = request.files.get("cover_image")
        if cover_image:
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join("static/images", filename))
        else:
            filename = None

        # Getting additional information
        publish_date = datetime.now()

        # Inserting corresponding values into the blogs database
        db.execute("INSERT INTO posts (title, content, category, summary, tags, cover_image, publish_date, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                   title, content, category, summary, tags, filename, publish_date, session["user_id"])

        # Redirecting user to home page
        flash("New post created successfully!", "success")
        return redirect("/")
    
    elif request.method == "GET":
        return render_template("new_post.html")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    
@app.route("/show_comments/<int:post_id>")
@login_required
def show_comments(post_id):
    """Shows the entire comments about a particular post"""

    # Query for comments
    comments = db.execute("""SELECT comments.*, users.username, users.profile_image 
                             FROM comments
                             JOIN users ON comments.user_id = users.id
                             WHERE comments.post_id = ?
                             ORDER BY comments.publish_date ASC""", post_id)
    
    # Id's of comments
    comment_ids = [comment["id"] for comment in comments]
    
    # Query for sub-comments
    sub_comments = []
    if comment_ids:
        placeholders = ','.join(['?'] * len(comment_ids))
        sub_comments = db.execute(f"""SELECT sub_comments.*, users.username, users.profile_image 
                                      FROM sub_comments
                                      JOIN users ON sub_comments.user_id = users.id
                                      WHERE sub_comments.comment_id IN ({placeholders})
                                      ORDER BY sub_comments.publish_date ASC""", *comment_ids)
    
    # Rendering template
    return render_template("show_comments.html", comments=comments, sub_comments=sub_comments, post_id=post_id)


@app.route("/publish_comment/<int:post_id>", methods=["GET", "POST"])
@login_required
def publish_comment(post_id):
    """Provides to make a comment on a particular post"""

    if request.method == "POST":
        # Ensure user sent the comment
        comment = request.form.get("comment")
        if not comment:
            flash("Please enter a comment", "error")
            return redirect(url_for('publish_comment', post_id=post_id))
        
        # Additional information
        publish_date = datetime.now()
        
        # Store this comment on database
        db.execute("INSERT INTO comments (post_id, user_id, comment, publish_date) VALUES (?, ?, ?, ?)", 
                   post_id, session["user_id"], comment, publish_date)
        
        # Redirecting user to show_comments page
        flash("New comment created successfully!", "success")
        return redirect(url_for('show_comments', post_id=post_id))

    elif request.method == "GET":
        return render_template("publish_comment.html", post_id=post_id)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect(url_for('show_comments', post_id=post_id))


@app.route("/publish_sub_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def publish_sub_comment(comment_id):
    """ Provides to make a subcomment to a comment """

    if request.method == "POST":
        # Ensure user sent the comment
        sub_comment = request.form.get("sub_comment")
        if not sub_comment:
            flash("Please enter a sub comment", "error")
            return redirect(url_for('publish_sub_comment', comment_id=comment_id))
        
        # Querying to get username and date
        publish_date = datetime.now()
        
        # Store this subcomment on database
        db.execute("INSERT INTO sub_comments (comment_id, user_id, sub_comment, publish_date) VALUES (?, ?, ?, ?)", 
                   comment_id, session["user_id"], sub_comment, publish_date)
        
        # Fetch post_id of the parent comment to redirect correctly
        post_id = db.execute("SELECT post_id FROM comments WHERE id = ?", comment_id)[0]["post_id"]
        
        # Redirecting user to show_comments page
        flash("New sub comment created successfully!", "success")
        return redirect(url_for('show_comments', post_id=post_id))

    elif request.method == "GET":
        return render_template("publish_sub_comment.html", comment_id=comment_id)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    """ Deletes chosen comment """
    
    if request.method == "POST":

        # Fetch the post_id and user_id of the comment to redirect properly
        comment = db.execute("SELECT post_id, user_id FROM comments WHERE id = ?", comment_id)
        if not comment:
            flash("Comment not found", "error")
            return redirect("/")
        
        post_id = comment[0]["post_id"]
        comment_user_id = comment[0]["user_id"]

        # Ensure user can only delete their own comments
        if comment_user_id != session["user_id"]:
            flash("You do not have permission to delete this comment.", "error")
            return redirect(url_for('show_comments', post_id=post_id))
        
        # Delete sub-comments first due to foreign key constraints
        db.execute("DELETE FROM sub_comments WHERE comment_id = ?", comment_id)

        # Delete the comment
        db.execute("DELETE FROM comments WHERE id = ?", comment_id)
        
        # Redirect the user to show comments page
        flash("Comment deleted successfully", "success")
        return redirect(url_for('show_comments', post_id=post_id))

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/update_comment/<int:comment_id>", methods=["POST", "GET"])
@login_required
def update_comment(comment_id):
    """ Updates chosen comment """

    if request.method == "POST":
        # Fetch the post_id and user_id of the comment to redirect properly
        comment = db.execute("SELECT post_id, user_id FROM comments WHERE id = ?", comment_id)
        if not comment:
            flash("Comment not found", "error")
            return redirect("/")
        
        # Taking values of post_id and user_id
        post_id = comment[0]["post_id"]
        user_id = comment[0]["user_id"]

        # Ensure user can only update their own comments
        if user_id != session["user_id"]:
            flash("You do not have permission to update this comment.", "error")
            return redirect(url_for('show_comments', post_id=post_id))

        # Ensure user entered new comment
        new_comment = request.form.get("new_comment")
        if not new_comment:
            flash("Please enter new comment.", "error")
            return redirect(url_for('update_comment', comment_id=comment_id))
        
        # Update the old comment
        db.execute("UPDATE comments SET comment = ? WHERE id = ?", new_comment, comment_id)

        # Redirecting user to show_comments page
        flash("Comment updated successfully.", "success")
        return redirect(url_for('show_comments', post_id=post_id))
    
    elif request.method == "GET":
        # Fetch the existing comment to display in the form
        comment = db.execute("SELECT comment FROM comments WHERE id = ?", comment_id)
        if not comment:
            flash("Comment not found", "error")
            return redirect("/")
        
        # Rendering update comment form
        return render_template("update_comment.html", comment=comment[0]["comment"], comment_id=comment_id)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/delete_sub_comment/<int:sub_comment_id>", methods=["POST"])
@login_required
def delete_sub_comment(sub_comment_id):
    """Deletes chosen sub comment"""

    if request.method == "POST":
        # Fetch the post_id and user_id of the sub comment to redirect properly
        sub_comment = db.execute("""SELECT sub_comments.comment_id, comments.post_id, sub_comments.user_id FROM sub_comments
                                    JOIN comments ON sub_comments.comment_id = comments.id 
                                    WHERE sub_comments.id = ?""", sub_comment_id)
        if not sub_comment:
            flash("Sub comment not found", "error")
            return redirect("/")

        post_id = sub_comment[0]["post_id"]
        user_id = sub_comment[0]["user_id"]

        # Ensure user can only delete their own comments
        if user_id != session["user_id"]:
            flash("You do not have permission to delete this sub comment.", "error")
            return redirect(url_for('show_comments', post_id=post_id))

        # Delete the sub comment
        db.execute("DELETE FROM sub_comments WHERE id = ?", sub_comment_id)

        # Redirect the user to show comments page
        flash("Sub comment deleted successfully", "success")
        return redirect(url_for('show_comments', post_id=post_id))

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/update_sub_comment/<int:sub_comment_id>", methods=["POST", "GET"])
@login_required
def update_sub_comment(sub_comment_id):
    """Updates chosen sub comment"""

    if request.method == "POST":
        # Fetch the post_id and user_id of the sub comment to redirect properly
        sub_comment = db.execute("""SELECT sub_comments.comment_id, comments.post_id, sub_comments.user_id FROM sub_comments
                                    JOIN comments ON sub_comments.comment_id = comments.id 
                                    WHERE sub_comments.id = ?""", sub_comment_id)
        if not sub_comment:
            flash("Sub comment not found.", "error")
            return redirect("/")

        # Taking values of post_id and user_id
        post_id = sub_comment[0]["post_id"]
        user_id = sub_comment[0]["user_id"]

        # Ensure user can only update their own sub comments
        if user_id != session["user_id"]:
            flash("You do not have permission to update this sub comment.", "error")
            return redirect(url_for('show_comments', post_id=post_id))

        # Ensure user entered new sub comment
        new_sub_comment = request.form.get("new_sub_comment")
        if not new_sub_comment:
            flash("Please enter new sub comment.", "error")
            return redirect(url_for('update_sub_comment', sub_comment_id=sub_comment_id))

        # Update the old sub comment
        db.execute("UPDATE sub_comments SET sub_comment = ? WHERE id = ?", new_sub_comment, sub_comment_id)

        # Redirecting user to show comments page
        flash("Sub comment updated successfully.", "success")
        return redirect(url_for('show_comments', post_id=post_id))

    elif request.method == "GET":
        # Fetch the existing sub comment to display in the form
        sub_comment = db.execute("SELECT sub_comment FROM sub_comments WHERE id = ?", sub_comment_id)
        if not sub_comment:
            flash("Sub comment not found.", "error")
            return redirect("/")

        # Rendering update sub comment form
        return render_template("update_sub_comment.html", sub_comment=sub_comment[0]["sub_comment"], sub_comment_id=sub_comment_id)

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")



@app.route("/update_post/<int:post_id>", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    """ Updates user's post """

    if request.method == "POST":
        # Ensuring user provided title, content, category (Required)
        title = request.form.get("title")
        if not title:
            flash("Please provide a title for your post", "error")
            return redirect(f"/update_post/{post_id}")
        if len(title) > 50:
            flash("Please provide a title that is less than 100 characters.", "error")
            return redirect(f"/update_post/{post_id}")
        
        content = request.form.get("content")
        if not content:
            flash("Please provide content for your post.", "error")
            return redirect(f"/update_post/{post_id}")
        
        category = request.form.get("category")
        if not category:
            flash("Please provide a category for your post.", "error")
            return redirect(f"/update_post/{post_id}")
        
        # Optional additions
        summary = request.form.get("summary")
        if summary and len(summary) > 100:
            flash("Please provide a summary that is less than 250 characters.", "error")
            return redirect(f"/update_post/{post_id}")
        
        tags = request.form.get("tags")
        
        cover_image = request.files.get("cover_image")
        if cover_image:
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join("static/images", filename))
        else:
            filename = None

        # Getting additional information
        publish_date = datetime.now()
        user_id = session["user_id"]

        # Updating the corresponding values in the blogs database
        db.execute("""
            UPDATE posts 
            SET title = ?, content = ?, category = ?, summary = ?, tags = ?, cover_image = ?, publish_date = ?, user_id = ?
            WHERE id = ? AND user_id = ?""", 
            title, content, category, summary, tags, filename, publish_date, user_id, post_id, user_id)

        # Redirecting user to home page
        flash("Post updated successfully!", "success")
        return redirect("/")
    
    elif request.method == "GET":
        # Fetch the post data to pre-fill the form
        post = db.execute("SELECT * FROM posts WHERE id = ? AND user_id = ?", post_id, session["user_id"])
        
        # If post doesn't exist
        if not post:
            flash("You do not have permission to update this post", "error")
            return redirect("/")
        
        return render_template("update_post.html", post=post[0])

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    
    
@app.route("/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
    """ Deletes user's post """

    # Ensure the post exists
    if request.method == "GET":
        post = db.execute("SELECT * FROM posts WHERE id = ?", post_id)
        if not post:
            flash("Post did not found.", "error")
            return redirect("/")
        
        # Ensure users can delete only their own posts
        if post[0]["user_id"] != session["user_id"]:
            flash("You do not have permission to delete this post", "error")
            return redirect("/")
        
        # Query for comment IDs related to the post
        comments = db.execute("SELECT id FROM comments WHERE post_id = ?", post_id)

        # Delete sub comments related to the post comments
        for comment in comments:
            db.execute("DELETE FROM sub_comments WHERE comment_id = ?", comment["id"])

        # Delete comments related to the post
        db.execute("DELETE FROM comments WHERE post_id = ?", post_id)

        # Delete likes related to the post
        db.execute("DELETE FROM likes WHERE post_id = ?", post_id)

        # Finally, delete the post itself
        db.execute("DELETE FROM posts WHERE id = ?", post_id)

        flash("Post has been deleted successfully.", "success")
        return redirect("/")

    else:
       flash("Oops, something went wrong. Please try again.", "error")
       return redirect("/") 
    

@app.route("/profile")
@login_required
def profile():
    """ Provides view the user's profile and if they want update the profile """
    
    if request.method == "GET":
        # Query the data for user
        user_data = db.execute("""SELECT users.*,
                                  (SELECT COUNT(*) FROM posts WHERE user_id = ?) AS post_count
                                  FROM users WHERE id = ?""", session["user_id"], session["user_id"])
        
        # Query user's posts
        user_posts = db.execute("""SELECT posts.*, users.username, 
                                   (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                                   (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count
                                   FROM posts 
                                   JOIN users ON posts.user_id = users.id
                                   WHERE posts.user_id = ?""", session["user_id"])

        # Check user exists
        if user_data:
            return render_template("profile.html", user=user_data[0], posts=user_posts)
        else:
            flash("User not found", "error")
            return redirect("/")

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/update_profile", methods=["POST", "GET"])
@login_required
def update_profile():
    """ Updates profile """

    # Post for updating profile
    if request.method == "POST":
        # Query the data of user
        user_data = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        
        # All of the form elements are optional to update. It's users call
        profile_image = request.files.get("profile_image")
        
        # Ensure user's (if has) bio remains and if user wants to update bio, ensure new bio is less than or equals to 75 characters
        bio = request.form.get("bio")
        if len(bio) > 75:
            flash("Please provide a title that is less than 100 characters.", "error")
            return redirect("/profile")
        if not bio:
            bio = user_data[0]["bio"]
        
        # Save the profile image if provided
        if profile_image:
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join("static/images", filename))
            
            # Update the profile image and bio
            db.execute("UPDATE users SET profile_image = ?, bio = ? WHERE id = ?", 
                       filename, bio, session["user_id"])
        else:
            filename = None
            
            # Update only the bio if no profile image is provided
            db.execute("UPDATE users SET bio = ? WHERE id = ?", bio, session["user_id"])
        
        # Redirecting user to the profile page
        flash("Profile has been updated successfully!", "success")
        return redirect("/profile")

    elif request.method == "GET":
        return render_template("update_profile.html")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/delete_profile_image")
@login_required
def delete_profile_image():
    """ Deletes the user's profile image (Changes back to default profile image) """

    if request.method == "GET":
        # Set the path for default image
        filename = os.path.join('default_profile.jpg')

        # Update the profile image of user
        db.execute("UPDATE users SET profile_image = ? WHERE id = ?", filename, session["user_id"])

        # Redirecting user to profile page
        flash("Profile image deleted successfully", "success")
        return redirect("/profile")

    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")    
    

@app.route("/like_post/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    """ Likes the post """

    if request.method == "POST":
        user_id = session["user_id"]
        
        # Check if the user already liked or disliked the post
        existing = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
        
        if existing:
            if existing[0]["like"] == 1:
                # User already liked the post, so remove the like
                db.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
                flash("Like removed.", "success")
            else:
                # User disliked the post, so change to like
                db.execute("UPDATE likes SET like = 1, dislike = 0 WHERE user_id = ? AND post_id = ?", user_id, post_id)
                flash("Changed to like.", "success")
        else:
            # User has not liked or disliked the post, so add a like
            db.execute("INSERT INTO likes (user_id, post_id, like, dislike) VALUES (?, ?, 1, 0)", user_id, post_id)
            flash("Post liked.", "success")
        
        return redirect("/")
    
    flash("Oops, something went wrong. Please try again.", "error")
    return redirect("/")


@app.route("/dislike_post/<int:post_id>", methods=["POST"])
@login_required
def dislike_post(post_id):
    """ Dislikes the post """

    if request.method == "POST":
        user_id = session["user_id"]
        
        # Check if the user already liked or disliked the post
        existing = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
        
        if existing:
            if existing[0]["dislike"] == 1:
                # User already disliked the post, so remove the dislike
                db.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
                flash("Dislike removed.", "success")
            else:
                # User liked the post, so change to dislike
                db.execute("UPDATE likes SET like = 0, dislike = 1 WHERE user_id = ? AND post_id = ?", user_id, post_id)
                flash("Changed to dislike.", "success")
        else:
            # User has not liked or disliked the post, so add a dislike
            db.execute("INSERT INTO likes (user_id, post_id, like, dislike) VALUES (?, ?, 0, 1)", user_id, post_id)
            flash("Post disliked.", "success")
        
        return redirect("/")
    
    flash("Oops, something went wrong. Please try again.", "error")
    return redirect("/")


@app.route("/search")
@login_required
def search():
    """ Provides the search feature for users """
    
    if request.method == "GET":
        # Search query
        query = request.args.get("query")
        if not query:
            flash("Please enter something.", "error")
            return redirect("/")

        query = f"%{query}%"

        # Query for results
        posts = db.execute("""SELECT posts.*, users.username,
                                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                                (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count 
                                FROM posts
                                JOIN users ON posts.user_id = users.id 
                                WHERE title LIKE ? OR tags LIKE ? OR summary LIKE ? OR content LIKE ?""", query, query, query, query)

        # Query for users
        users = db.execute("SELECT * FROM users WHERE username LIKE ?", query)

        # Check following status for each user
        for user in users:
            user['is_following'] = db.execute("SELECT * FROM follows WHERE following_id = ? AND follower_id = ?", user['id'], session["user_id"])

        # Flash message and rendering results
        if posts or users:
            flash(f"Here are the results for '{query.strip('%')}':", "success")
            return render_template("search.html", posts=posts, users=users)
        else:
            flash(f"Sorry, there is no result found for '{query.strip('%')}'.", "error")
            return redirect("/")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/post_details/<int:post_id>")
@login_required
def post_details(post_id):
    """ Shows the details of selected post """

    # Selecting entire columns of posts to allow user to look in detailed
    if request.method == "GET":
        post = db.execute("""SELECT posts.*, users.username, 
                             (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                             (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count                         
                             FROM posts
                             JOIN users ON posts.user_id = users.id
                             WHERE posts.id = ?""", post_id)
        
        # Check if the post exists or not
        if not post:
            flash("Post not found.", "error")
            return redirect("/")

        # Return the template
        return render_template("detailed_post.html", post=post[0])
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/follow/<int:following_id>", methods=["POST"])
@login_required
def follow(following_id):
    """ Follows the desired user """
    
    if request.method == "POST":
        # Taking value of current logged in user's id
        follower_id = session["user_id"]

        # Ensure user can't follow themselves
        if follower_id == following_id:
            flash("You can't follow yourself.", "error")
            return redirect("/")
        
        # Check if the user already follows the other user
        existing = db.execute("SELECT * FROM follows WHERE following_id = ? AND follower_id = ?", following_id, follower_id)
        
        if not existing:
            # User does not follow this user, so add a follow
            db.execute("INSERT INTO follows (following_id, follower_id) VALUES (?, ?)", following_id, follower_id)

            # Update the following user's following column (increment by 1)
            db.execute("UPDATE users SET following = following + 1 WHERE id = ?", follower_id)

            # Update the follow user's followers column (increment by 1)
            db.execute("UPDATE users SET followers = followers + 1 WHERE id = ?", following_id,)

            flash("User followed.", "success")
        else:
            flash("You are already following this user.", "info")
        
        # Redirecting user to home page
        return redirect("/")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/unfollow/<int:following_id>", methods=["POST"])
@login_required
def unfollow(following_id):
    """ Unfollows the desired user """
    
    if request.method == "POST":
        # Taking value of current logged in user's id
        follower_id = session["user_id"]

        # Ensure user can't unfollow themselves
        if follower_id == following_id:
            flash("You can't unfollow yourself.", "error")
            return redirect("/")

        # Check if the user follows the other user
        existing = db.execute("SELECT * FROM follows WHERE following_id = ? AND follower_id = ?", following_id, follower_id)
        
        if not existing:
            flash("You are not following this user.", "error")
        else:
            # User follows this user, so remove the follow
            db.execute("DELETE FROM follows WHERE following_id = ? AND follower_id = ?", following_id, follower_id)

            # Update the following user's following column (decrement by 1)
            db.execute("UPDATE users SET following = following - 1 WHERE id = ?", follower_id)

            # Update the follow user's followers column (decrement by 1)
            db.execute("UPDATE users SET followers = followers - 1 WHERE id = ?", following_id)

            flash("Unfollowed.", "success")

        # Redirecting user to followng users list page
        return redirect("/following")
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/followers")
@login_required
def followers():
    """ Allows user to see their follower list """

    if request.method == "GET":
        # Query for followers
        followers = db.execute("""SELECT follows.*, users.username, users.profile_image, users.join_date, users.followers, users.following
                                  FROM follows
                                  JOIN users ON follows.follower_id = users.id
                                  WHERE follows.following_id = ?""", session["user_id"])
        
        # Rendering template
        return render_template("followers.html", followers=followers)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")
    

@app.route("/following")
@login_required
def following():
    """ Allows user to see their following list """

    if request.method == "GET":
        # Query for followers
        followings = db.execute("""SELECT follows.*, 
                                   u_following.username AS following_username, 
                                   u_following.profile_image AS following_profile_image, 
                                   u_following.join_date AS following_join_date, 
                                   u_following.followers AS following_followers, 
                                   u_following.following AS following_following,
                                   u_follower.username AS follower_username, 
                                   u_follower.profile_image AS follower_profile_image, 
                                   u_follower.join_date AS follower_join_date, 
                                   u_follower.followers AS follower_followers, 
                                   u_follower.following AS follower_following
                                   FROM follows
                                   JOIN users AS u_following ON follows.following_id = u_following.id
                                   JOIN users AS u_follower ON follows.follower_id = u_follower.id
                                   WHERE follows.follower_id = ?""", session["user_id"])
        
        # Rendering template
        return render_template("following.html", followings=followings)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/posts_by_category/<string:category>")
@login_required
def posts_by_category(category):
    """ Allows user to choose a category to specify their desired posts """

    if request.method == "GET":
        # Query all posts with desired category
        posts = db.execute("""SELECT posts.*, users.username, 
                              (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.like = 1) AS likes_count,
                              (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id AND likes.dislike = 1) AS dislikes_count
                              FROM posts
                              JOIN users ON posts.user_id = users.id 
                              WHERE category = ?""", category)

        # Checking any posts exists with corresponding category or not
        if not posts:
            flash(f"No posts found in the {category} category.", "error")
            return redirect("/")
        
        return render_template("posts_by_category.html", posts=posts, category=category)
    
    else:
        flash("Oops, something went wrong. Please try again.", "error")
        return redirect("/")


@app.route("/about")
def about():
    """ About page """

    # Rendering template
    return render_template("about.html")


@app.route("/blog")
def blog():
    """ Blog page """

    # Rendering template
    return render_template("blog.html")
