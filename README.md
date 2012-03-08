# Flask-Security

Simple security for Flask applications combining [Flask-Login](http://packages.python.org/Flask-Login/), [Flask-Principal](http://packages.python.org/Flask-Principal/), [Flask-WTF](http://packages.python.org/Flask-WTF/), [passlib](http://packages.python.org/passlib/), and your choice of datastore. Currently [SQLAlchemy](http://www.sqlalchemy.org) via [Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/) and [MongoEngine](http://www.mongoengine.org) via [Flask-MongoEngine](https://github.com/sbook/flask-mongoengine) are supported out of the box. You will need to install the necessary Flask extensions that you'll be using. Additionally, you may need to install an encryption library such as [py-bcrypt](http://www.mindrot.org/projects/py-bcrypt/) to support bcrypt passwords.

## Overview

Flask-Security does a few things that Flask-Login and Flask-Principal don't provide out of the box. They are:

1. Setting up login and logout endpoints
2. Authenticating users based on username or email
3. Limiting access based on user 'roles'
4. User and role creation
5. Password encryption

That being said, you can still hook into things such as the Flask-Login and Flask-Principal signals if need be.


## Getting Started

The best place to get started is to look at the example application(s) and corresponding tests. The example apps are currently used to test Flask-Security as well so they are solid examples of most, if not all, features. Configuration options are illustrated in the tests as well.

Essentially, the only thing you need to do on your own is setup a login form/view. Again, refer to the example app to see how easily this is done.

However, the following are some hypothetical examples to give you a sense of how Flask-Security works:

### Require a logged in user:
    
    from flask import render_template
    from flask.ext.security import login_required
    
    … application setup …
    
    @app.route('/profile')
    @login_required
    def profile():
    	return render_template('profile.html')
    	
### Require an admin:
    
    from flask import render_template
    from flask.ext.security import roles_required
    
    … application setup …
    
    @app.route('/admin')
    @roles_required('admin')
    def admin():
    	return render_template('admin/index.html')
    	
### Require any of the specified roles:
    
    from flask import render_template
    from flask.ext.security import roles_accepted
    
    … application setup …
    
    @app.route('/admin')
    @roles_accepted('admin', 'editor', 'author')
    def admin():
    	return render_template('admin/index.html')
    	
### Showing a link in a template only for an admin:

    {% if current_user.has_role('admin') %}
    <a href="{{ url_for('admin.index') }}">Admin Panel</a>
    {$ endif %}