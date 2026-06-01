from flask import Flask, render_template, flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey12345"

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message="Username must be between 4 to 0 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be atleast 8 characters.")
    ])
    submit = SubmitField('Sign Up')

@app.route('/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}", "success")
        return redirect(url_for('register'))
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)