import requests
from bs4 import BeautifulSoup as soup
from captcha_detection.decode import decode
# from captcha_detection.detection import keras_detection_model
import month_payment_sorter
import json
import csv

INITIAL_URL = "https://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome/"
BASE_URL = "https://unifiedportal-epfo.epfindia.gov.in"


#  ------------- INITIAL BYPASS CODE ---------------

def retrieve_and_read_captcha(web_data, session):
    print("\n...... Generating and Decoding captcha .......")
    img_src = web_data.find("div", {"id": "captchaImg"}).find("img")['src']
    img_url = BASE_URL + img_src
    response = session.get(img_url, stream=True)
    filename = "current_captcha.png"
    with open(filename,"wb") as f: 
        f.write(response.content)
    
    # captcha_detection = keras_detection_model(filename)
    captcha_detection  = "ACD"
    return captcha_detection

def post_search_establishment_request(my_soup, session, est_name,est_code=""):
    est_req = my_soup.find("div", {"class": "col-sm-3 col-md-2 col-lg-2"}).input['onclick'].split("'")[1]
    url = BASE_URL + est_req
    response = None
    while response is None:
        captcha = retrieve_and_read_captcha(my_soup, session)
        captcha = input("Enter captcha :")
        response = session.post(url, data=json.dumps({"EstName": est_name, "EstCode": est_code, "captcha": captcha}),
                                headers={'Content-Type': 'application/json'})
        
        return response

def get_complete_data(table_body):
    data = []
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    return data

def get_company_session_list(establishment_response):
    my_soup = soup(establishment_response.text, "html.parser")
    name_id_list = []
    all_organization_data =[]

    for org in my_soup.find_all("a", href=True):
        name_id_list.append(org["name"])

    all_organization_data = get_complete_data(my_soup.find('tbody'))
    print("....... Company List done .......")
    return name_id_list, all_organization_data

def get_company_list(company_name):
    session = requests.Session()
    web_response = session.get(INITIAL_URL)
    my_soup = soup(web_response.text, "html.parser")
    company_list = []
    r = post_search_establishment_request(my_soup, session, company_name)

    company_list, all_complete_data= get_company_session_list(r)
    print("\nThe complete data is listed below :\n")
    for i in all_complete_data:
        print(i,"\n")

    return company_list, r, session, all_complete_data


#  ---------- Scrapping for Particular Company ----------

def sort_and_save_payment_details(payment_details):
    payment_soup = soup(payment_details.text, "html.parser")
    # the data here is stored in a pretty ugly way, need to sort
    parsed_list = []
    for row in payment_soup.find_all("tr")[1:]:  # first row is the title row
        date = row.find_all("td")[3].find(text=True).split("-")
        timestamp = row.find_all("td")[1].find(text=True)
        amount = row.find_all("td")[2].find(text=True)
        employee_number = row.find("a").contents[0]
        pay_link = row.find("a", href=True)["onclick"].split("'")[1]
        my_trrn = row.find_all("td")[0].find(text=True)
        if int(row.find("a", href=True).contents[0]):
            parsed_list.append([my_trrn, timestamp, amount.strip(), date[1], date[0], employee_number,pay_link])
    return month_payment_sorter.sort_month_and_payment(parsed_list)[::-1]     # Get last all months



def post_get_company_details(r,session,code):
    my_soup = soup(r.text, "html.parser")
    search_url = (my_soup.find_all("a", href=True)[0]["onclick"].split(",'")[1][:-1])
    fetch_url = BASE_URL + search_url
    response = session.post(fetch_url, data=json.dumps({"EstId": code}), headers={'Content-Type': 'application/json'})
    table_soup = soup(response.text, "html.parser")
    company_details=get_complete_data(table_soup.find('tbody'))
    process_data = {}

    for data in company_details:
        process_data[data[0]] = data[1]
    print("\nCompany Details in JSON format:")
    print(process_data)
    return response, process_data

def view_payment_details(company_details, session):
    detail_web_data = soup(company_details.text, "html.parser")
    search_url = detail_web_data.find("a", href=True)["onclick"].split("'")[1]
    fetch_url = BASE_URL + search_url
    payment = session.get(fetch_url)
    return payment

def save_data_into_csv(fields,rows):
    with open('payment_details.csv', 'w', newline='') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(rows)

def get_payment_table(session, link, trrn):
    my_url = BASE_URL + (link)
    table = session.post(my_url, data=json.dumps({"Trrn": trrn}), headers={'Content-Type': 'application/json'})
    return table


def get_name_list(payment_table):
    table_soup = soup(payment_table.text, "html.parser")
    name_list = []
    for row in table_soup.find_all("tr")[1:]:  # first line is title line
        name_list.append((row.find("td").find(text=True)))
    return name_list


def check_name_tags(given_name, employee):
    given_name_list = [word.upper() for word in given_name.split(' ')]
    given_name_list.sort()

    employee_list = [word.upper() for word in employee.split(' ')]
    employee_list.sort()

    return ((given_name.upper() == employee.upper()) or (given_name.upper() in employee.upper()))

#   ----- This is the preprocessing function --------


def get_particular_employee_detail(emp_dict, employee_name, company, payment,aggregate):
    result_json = {
        "company" : company["Establishment Name"],
        "establishment_id" : company["Establishment Code"]
        }

    employee_working_month = []

    name_count = 0

    for data in emp_dict:
        names = emp_dict[data]
        name_count = 0
        for name in names:
            if(check_name_tags(employee_name,name)):
                if name_count <= 1:
                    name_count += 1
                    employee_working_month.append(data)
                else:
                    return {}

    if len(employee_working_month) ==0:
        return {}
        
    working_amount_rel = []

    for working in employee_working_month:
        trrn, year = working.split('_')
        for data in aggregate:
            if data[0] == year:
                working_amount_rel.append([year,data[1],data[2]])

    result_json['working_from'] = employee_working_month[len(employee_working_month)-1]
    result_json['working_till'] = employee_working_month[0]
    result_json['details'] = working_amount_rel
    
    return result_json

def calculate_cagr_score(company,aggregate):
    final_investment = aggregate[len(aggregate)-1][1]
    initial_investment = aggregate[0][1]
    
    y1 = aggregate[len(aggregate)-1][0][3:]
    y2 = aggregate[0][0][3:]
    year = int(int(y1)-int(y2))
    CAGR = (pow((float(final_investment)/float(initial_investment)),float(1/year)) - 1)*100
    print("The mutual fund investment gave you an average return of {}% per annum".format(round(CAGR,4)))
    return CAGR


def run_scrap_for_company(company_name,ind,r,sesh,employee):
    req_dict = dict()
    company_details, list_details = post_get_company_details(r,sesh,ind)
    payment_details = view_payment_details(company_details, sesh)
    req_payments = sort_and_save_payment_details(payment_details)

    fields = ['TRRN','Timestamp','Amount','Year','Month','Employees','Link']
    save_data_into_csv(fields,req_payments)
    
    for req_payment in req_payments:
        month = req_payment[4]
        year = req_payment[3]
        payment_table = get_payment_table(sesh, req_payment[6], req_payment[0])  #Send TRRN and link
        name_list = get_name_list(payment_table)
        
        # Store in dictionary
        req_dict[req_payment[0]+"_"+month+year] = name_list
        # print(req_dict)

    aggregate_list = month_payment_sorter.aggregate_data()
    employee_scrap = get_particular_employee_detail(req_dict,employee,list_details,req_payments,aggregate_list)
    print("Employee Final Data :",employee_scrap)
    cagr=calculate_cagr_score(company_details, aggregate_list)

    return list_details, employee_scrap, 