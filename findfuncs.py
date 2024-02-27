import glob
import os
import pandas as pd
import pickle

def find_company_folder(company, dirpath):
    codes = pd.read_excel("/Users/rebeccakrall/Data/Proposal-Report-Data/Reference_Data/Company_Codes.xlsx")
    full_name = codes["Company"][codes['Code'] == company]
    if len(full_name) > 0:
        full_name = full_name.values[0]
        for f in os.scandir(dirpath):
            if f.is_dir() and full_name in f.name:
                return f.path
            elif f.is_dir() and f.name in full_name:
                return f.path
    else:
        return None
            

def find_all_docx(dirpath, string_match):
    search_path = dirpath+ '/**/*'+ string_match+ "*.docx"
    matches = glob.glob(search_path, recursive= True)

    # search_path_2 = dirpath + '/*/*/*'+ string_match+ "*.docx"
    # matches2 = glob.glob(search_path_2)

    # matches.extend(matches2)csv
    return matches



def add_report_paths(csv_file, toplevel_path):
    proj = pd.read_csv(csv_file)
    data_dict = {}
    for a in range(proj.shape[0]):
        company = proj.iloc[a]['Name'].split('_')[0]
        company_folder = find_company_folder(company, toplevel_path)

        if company_folder is not None:
            docs = find_all_docx(company_folder, proj.iloc[a]['Name'].split(' ')[0])
            data_dict[proj.iloc[a]['Name']] = docs

            print('Adding '+ proj.iloc[a]['Name'])
        else:
            print("Could not find "+company+ " folder")
    
    # df = pd.DataFrame(data_dict)
    # df.to_csv("/Users/rebeccakrall/Desktop/reports_2023.csv")


    with open('/Users/rebeccakrall/Desktop/proposals_2023.pkl', 'wb') as handle:
        pickle.dump(data_dict, handle)