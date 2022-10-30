import pandas as pd
month_to_num_map = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def get_month_number(month):
    return month_to_num_map[month]


def sort_month_and_payment(tuple_list):
    return sorted(tuple_list, key=lambda y: (y[3], get_month_number(y[4])))

def sort_aggregated_list(tuple_list):
    return sorted(tuple_list, key=lambda y: (y[0][3:], get_month_number(y[0][:-2])))

def aggregate_data():
    df = pd.read_csv("payment_details.csv")
    df.drop(df.columns[[0]], axis = 1, inplace = True)
    df["Amount"] = df["Amount"].replace("[$,]", "", regex=True).astype(int)
    df["Date"] = df["Month"]+df["Year"].astype(str)
    df.drop(df.columns[[0,2,3,5]], axis = 1, inplace = True)
    df2 = df.groupby(['Date'],as_index = False).sum()
    df2.values.tolist()
    sorted_val = sort_aggregated_list(df2.values)
    return sorted_val