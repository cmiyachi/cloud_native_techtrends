import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

no_of_conns=0  # global variable to count connectionslogg

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global no_of_conns
    no_of_conns +=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    if post is  None:
        logging.info("Article id {0}  not found".format(post_id))
    else:
        logging.info("Article '{0}' found".format(post['title']))
              
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    '''Heart Beat - Health Check of application'''
    con = get_db_connection()
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Status request successfull')
    return response

@app.route('/metrics')
def metrics():
    '''Return total users and total number of database connections'''
    connection = get_db_connection()
    no_of_posts=connection.execute('SELECT COUNT(*) from posts').fetchone()[0]
    response = app.response_class(
            response=json.dumps({"status":"success","data":{"db_connection_count":no_of_conns,"post_count":no_of_posts}}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
