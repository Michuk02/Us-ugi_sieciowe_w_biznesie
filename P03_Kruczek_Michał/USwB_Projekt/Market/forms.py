from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from Market.models import User

class RegisterForm(FlaskForm):
    def validate_username(self, username_check):
        if User.query.filter_by(username=username_check.data).first():
            raise ValidationError('Login już istnieje! Spróbuj użyć innej nazwy.')
    
    def validate_email_address(self, email_address_check):
        if User.query.filter_by(email_address=email_address_check.data).first():
            raise ValidationError('Adres e-mail już istnieje! Spróbuj użyć innego adresu mailowego.')

    username = StringField(label='Login', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Adres e-mail', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Hasło', validators=[Length(min=3), DataRequired()])
    password2 = PasswordField(label='Potwierdź hasło', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Utwórz konto')

class LoginForm(FlaskForm):
    username = StringField(label='Login', validators=[DataRequired()])
    password = PasswordField(label='Hasło', validators=[DataRequired()])
    submit = SubmitField(label='Zaloguj się')

class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Kup przedmiot!')

class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sprzedaj przedmiot!')
