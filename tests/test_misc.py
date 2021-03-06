# -*- coding: utf-8 -*-
"""
    test_emails
    ~~~~~~~~~~~

    Email functionality tests
"""

from pytest import raises

from flask_security import Security
from flask_security.forms import LoginForm, RegisterForm, ConfirmRegisterForm, \
    SendConfirmationForm, PasswordlessForm, ForgotPasswordForm, ResetPasswordForm, \
    ChangePasswordForm, TextField, PasswordField, email_required, email_validator, valid_user_email
from flask_security.utils import capture_reset_password_requests

from utils import authenticate, init_app_with_options, populate_data


def test_async_email_task(app, sqlalchemy_datastore):
    init_app_with_options(app, sqlalchemy_datastore, **{
        'SECURITY_RECOVERABLE': True
    })

    app.mail_sent = False

    @app.security.send_mail_task
    def send_email(msg):
        app.mail_sent = True

    client = app.test_client()
    client.post('/reset', data=dict(email='matt@lp.com'))
    assert app.mail_sent is True


def test_register_blueprint_flag(app, sqlalchemy_datastore):
    app.security = Security(app, datastore=Security, register_blueprint=False)
    client = app.test_client()
    response = client.get('/login')
    assert response.status_code == 404


def test_basic_custom_forms(app, sqlalchemy_datastore):
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True

    class MyLoginForm(LoginForm):
        email = TextField('My Login Email Address Field')

    class MyRegisterForm(RegisterForm):
        email = TextField('My Register Email Address Field')

    class MyForgotPasswordForm(ForgotPasswordForm):
        email = TextField('My Forgot Email Address Field',
                          validators=[email_required, email_validator, valid_user_email])

    class MyResetPasswordForm(ResetPasswordForm):
        password = TextField('My Reset Password Field')

    class MyChangePasswordForm(ChangePasswordForm):
        password = PasswordField('My Change Password Field')

    app.security = Security(app,
                            datastore=sqlalchemy_datastore,
                            login_form=MyLoginForm,
                            register_form=MyRegisterForm,
                            forgot_password_form=MyForgotPasswordForm,
                            reset_password_form=MyResetPasswordForm,
                            change_password_form=MyChangePasswordForm)

    populate_data(app)

    client = app.test_client()

    response = client.get('/login')
    assert b'My Login Email Address Field' in response.data

    response = client.get('/register')
    assert b'My Register Email Address Field' in response.data

    response = client.get('/reset')
    assert b'My Forgot Email Address Field' in response.data

    with capture_reset_password_requests() as requests:
        response = client.post('/reset', data=dict(email='matt@lp.com'))

    token = requests[0]['token']
    response = client.get('/reset/' + token)
    assert b'My Reset Password Field' in response.data

    authenticate(client)

    response = client.get('/change')
    assert b'My Change Password Field' in response.data


def test_confirmable_custom_form(app, sqlalchemy_datastore):
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_CONFIRMABLE'] = True

    class MyRegisterForm(ConfirmRegisterForm):
        email = TextField('My Register Email Address Field')

    class MySendConfirmationForm(SendConfirmationForm):
        email = TextField('My Send Confirmation Email Address Field')

    app.security = Security(app,
                            datastore=sqlalchemy_datastore,
                            send_confirmation_form=MySendConfirmationForm,
                            confirm_register_form=MyRegisterForm)

    client = app.test_client()

    response = client.get('/register')
    assert b'My Register Email Address Field' in response.data

    response = client.get('/confirm')
    assert b'My Send Confirmation Email Address Field' in response.data


def test_passwordless_custom_form(app, sqlalchemy_datastore):
    app.config['SECURITY_PASSWORDLESSABLE'] = True

    class MyPasswordlessLoginForm(PasswordlessForm):
        email = TextField('My Passwordless Email Address Field')

    app.security = Security(app,
                            datastore=sqlalchemy_datastore,
                            passwordless_form=MyPasswordlessLoginForm)

    client = app.test_client()

    response = client.get('/login')
    assert b'My Passwordless Email Address Field' in response.data


def test_addition_identity_attributes(app, sqlalchemy_datastore):
    init_app_with_options(app, sqlalchemy_datastore, **{
        'SECURITY_USER_IDENTITY_ATTRIBUTES': ('email', 'username')
    })
    client = app.test_client()
    response = authenticate(client, email='matt', follow_redirects=True)
    assert b'Hello matt@lp.com' in response.data


def test_flash_messages_off(app, sqlalchemy_datastore, get_message):
    init_app_with_options(app, sqlalchemy_datastore, **{
        'SECURITY_FLASH_MESSAGES': False
    })
    client = app.test_client()
    response = client.get('/profile')
    assert get_message('LOGIN') not in response.data


def test_invalid_hash_scheme(app, sqlalchemy_datastore, get_message):
    with raises(ValueError):
        init_app_with_options(app, sqlalchemy_datastore, **{
            'SECURITY_PASSWORD_HASH': 'bogus'
        })


def test_change_hash_type(app, sqlalchemy_datastore):
    init_app_with_options(app, sqlalchemy_datastore, **{
        'SECURITY_PASSWORD_SCHEMES': ['bcrypt', 'plaintext']
    })

    app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    app.config['SECURITY_PASSWORD_SALT'] = 'salty'

    app.security = Security(app, datastore=sqlalchemy_datastore, register_blueprint=False)

    client = app.test_client()

    response = client.post('/login', data=dict(email='matt@lp.com', password='password'))
    assert response.status_code == 302
