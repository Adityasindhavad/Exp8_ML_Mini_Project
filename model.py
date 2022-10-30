from wtforms import SubmitField, StringField, validators
from flask_wtf import FlaskForm

class InputForm(FlaskForm):
    company = StringField('Company Name', [validators.DataRequired()])
    employee = StringField('Employee Name', [validators.DataRequired()])
    submit = SubmitField('Submit')

class IndexForm(FlaskForm):
    index_value = StringField('Index', [validators.DataRequired()])
    submit = SubmitField('Search Index')

class BackToHomeForm(FlaskForm):
    submit = SubmitField('Home')
