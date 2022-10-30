from captcha_detection.decode import decode
from prompts.prompt import company_input,which_index,employee_input
from scraper import get_company_list,run_scrap_for_company


if __name__ == '__main__':
    company_name = company_input()
    company_list,r,session,all_collected_data = get_company_list(company_name)
    print("\nThe Company IDS found under your search are listed here :")
    print(company_list)
    #print(r.text)
    selected_index = int(which_index())
    employee = employee_input()
    run_scrap_for_company(company_name,company_list[selected_index],r,session,employee)

