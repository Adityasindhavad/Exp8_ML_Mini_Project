from flask import Flask, request, render_template, redirect, url_for, session
import numpy as np
from model import InputForm, IndexForm, BackToHomeForm
from flask_bootstrap import Bootstrap
from prompts.prompt import employee_input
from scraper import get_company_list,run_scrap_for_company
from flask_session import Session


app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='e030d695ec83dae70a96c5499abf46bf')
    
#configuring the session type as a filesyste and hence not storing in the browser
app.config["SESSION_TYPE"] = "filesystem"
Bootstrap(app)
Session(app)

@app.route('/', methods=['GET', 'POST'])
def basics():
    form = InputForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        company_name = form.company.data
        employee_name= form.employee.data
        company_list,r,session_used,all_company_data = get_company_list(company_name)
        print("\nThe Company IDS found under your search are listed here :")
        print(company_list)
        #print("BEFORE ENCODING session_used:",session_used.post)

        #Storing the session variables
        session['employee_name']= employee_name
        session['company_name'] = company_name
        session['company_list'] = company_list
        session['r'] = r
        session['session_used']=session_used
        session['all_company_data']=all_company_data

        #redirecting to the index search page
        return redirect(url_for('index_search'))
    return render_template('employee_verification_system.html', form=form) 


@app.route('/index_search', methods=['GET', 'POST'])
def index_search():
    form=IndexForm(request.form)

    #Using the session variables created
    company_name=session.get('company_name')
    company_list = session.get('company_list')
    r = session.get('r')
    session_used=session.get('session_used') 
    all_company_data=session.get('all_company_data')
    employee_name=session.get('employee_name')

    if request.method == 'POST' and form.validate_on_submit():
        chosen_index = int(form.index_value.data)   
        company_details, employee_details, cagr=run_scrap_for_company(company_name,company_list[chosen_index],r,session_used,employee_name)

        #creating session variables for company details and employee details
        session['company_details']=company_details
        session['employee_details']=employee_details
        session['cagr']=cagr

        return redirect(url_for('details'))
    return render_template('index_form.html',form=form,all_company_data=all_company_data) 



@app.route('/details', methods=['GET', 'POST'])
def details():
    form=BackToHomeForm(request.form)

    #Using the session variables created
    employee_name=session.get('employee_name')
    employee_details=session.get('employee_details')
    company_details=session.get('company_details')
    cagr=session.get('cagr')

    if request.method == 'POST':
        return redirect(url_for('basics'))

    return render_template('view.html',form=form,company_details=company_details,employee_details=employee_details,employee_name=employee_name,cagr=cagr) 




if __name__ == '__main__':
    app.run()
