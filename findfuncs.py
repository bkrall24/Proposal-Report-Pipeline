import glob
import os
import pandas as pd
import pickle
import time
import re
from datetime import datetime


def find_study_pattern(text):
    pattern = r"[^{(_\s.]{2,6}_\d{2,3}_\d{1,2}[A-Za-z]*\d{2,4}"
    # pattern = r"_\d{2}_\d{2}[A-Z]{3}\d{2}_"
    pat = re.search(pattern, text)

    return pat
  

def find_all_docx(dirpath, string_match):
    search_path = dirpath + '/**/*' + string_match + "*.doc"
    matches = glob.glob(search_path, recursive= True)

    return matches

def find_study_docx(dirpath):
    filepaths = []
    
    for filename in glob.iglob(os.path.join(dirpath, '**', '*.doc*'), recursive=True):
        _, fn = os.path.split(filename)
    # Check if the filename matches the pattern
        # if re.search(r"_\d{2}_\d{2}[A-Z]{3}\d{2}_", fn):
        if re.search(r"_\d{2,3}_\d{1,2}[A-Za-z]*\d{2,4}_", fn):
            if '~$' not in fn:
                filepaths.append(filename)
    return filepaths

def parse_custom_date(date_str):
    # Mapping of month abbreviations to their numeric representation
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
        'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
        'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    
    # Extract day, month abbreviation, and year
    day = int(date_str[:2])
    month = month_map[date_str[2:5]]
    year = int(date_str[5:])
    
    # Convert the year to a 4-digit year based on the assumption
    # that the year is in the range 00-99 and represents the most recent year matching that
    if year <= datetime.now().year % 100:
        year += 2000
    else:
        year += 1900
    
    # Create a datetime object
    dt = datetime(year, month, day)
     
    return dt.strftime('%Y-%m-%d')

def get_proposal_data(filepath):
    fn = os.path.basename(filepath)
    doc_name, ext  = os.path.splitext(fn)
    
    last_mod = os.path.getmtime(filepath)
    last_mod = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_mod))
    created = os.path.getctime(filepath)
    created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created))

    p = find_study_pattern(doc_name)
    date_end = p.span()[-1]

    trailing_text = doc_name[date_end:]
    # tt = re.split(r'[_\s.]+', trailing_text)
    tt = re.split(r'[_\s.]+', trailing_text, maxsplit=1)
    # tt = trailing_text.split('_', 1)
    study_id = doc_name[p.span()[0]:p.span()[1]] #+ tt[0]
    
    document_id = doc_name[p.span()[0]:]
    try:
        study_date = parse_custom_date(doc_name[date_end-7:date_end])
    except:
        study_date = None

    if len(tt) > 1:
        if 'R' in tt[1]:
            rep_num = re.findall(r"\d+(?:\.\d+)?", tt[1])
            if len(rep_num):
                proposal_number = float(rep_num[0])
            else:
                proposal_number = None
        else:
            proposal_number = None

        if re.search(r"CO(?:[^a-zA-Z]|$)", tt[1]):
            change_order = True
        else:
            change_order = False
    else:
        proposal_number = 0
        change_order = False


    return {'study_id':study_id, 'document_id': document_id, 'filepath': filepath, 'date_created': created, 
            'date_modified': last_mod, 'study_date': study_date, 'draft_number': proposal_number, 'change_order': change_order}

    

def filepath_strings(filepath):

    found_dict = {}
    fn = os.path.basename(filepath)
    doc_name, ext  = os.path.splitext(fn)
    
   
    p = find_study_pattern(doc_name)
    print(doc_name)

    if p is not None:
        date_end = p.span()[-1]
        found_dict['document_id'] = doc_name[p.span()[0]:]
        found_dict['study_id'] = doc_name[p.span()[0]:p.span()[1]] #+ tt[0]
    else:
        p = re.search(r"_\d{2,3}_\d{2}[A-Za-z]*\d{2,4}_", doc_name)
        date_end = p.span()[-1]
        found_dict['document_id'] = doc_name
        found_dict['study_id'] = doc_name[:p.span()[1]]

    found_dict['date_modified'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(filepath)))
    found_dict['date_created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime( os.path.getctime(filepath)))

    try:
        found_dict['study_date'] = parse_custom_date(doc_name[date_end-7:date_end])
    except:
        found_dict['study_date'] = None


    if re.search(r"CO(?:[^a-zA-Z]|$)", doc_name[date_end:]):
        found_dict['change_order'] = True
    

    rep_num = re.findall(r"R\d+(?:\.\d+)?", doc_name[date_end:])
    try:
        found_dict['draft_number'] = max([float(r.split("R")[-1]) for r in rep_num])
    except:
        found_dict['draft_number'] = 0


    dl = doc_name.lower()
   
    if ("study_plan" in dl) or ("study plan" in dl):
        found_dict['study_plan'] = True
    
    if ("annotated" in dl) or ("redline" in dl):
        found_dict['annotated'] = True

    if "draft" in dl:
        found_dict['draft'] = True

    if ("update" in dl) or ("edit" in dl):
        found_dict["edited"] = True

    if "final" in dl:
        found_dict["final"] = True
    
    if "redacted" in dl:
        found_dict["redacted"] = True
    
    if "formulation" in dl:
        found_dict["formulation"] = True

    if "proposal" in dl:
        found_dict['proposal'] = True

    if "report" in dl:
        found_dict['report'] = True
    

    
    found_dict['filepath'] = filepath

    return found_dict


def get_last_proposal(df):
    # pass
    # get unique study id values
    # discard any change orders
    # for each study id value, count number of proposals
    # if there is only one - use that
    # if there are multiple - if there are draft numbers, grab the largest one
    #   if there a multiple with the highest number, take the one with the latest modification
    good_rows = []
    not_found = []
    studies = df['study_id'].unique()
    
    for s in studies:
        matching = df.loc[(df['study_id'] == s) & (~df['change_order'])]
        if len(matching) == 1:
            good_rows.append(matching.index[0])
        else:
            last_draft = matching[matching['draft_number'] == matching['draft_number'].max()]

            if len(last_draft) == 0:
                last_draft = matching

            if len(last_draft) == 1:
                good_rows.append(last_draft.index[0])
            else:
                latest_draft = last_draft[last_draft['date_modified'] == last_draft['date_modified'].max()]
                if len(latest_draft) > 0:
                    good_rows.append(latest_draft.index[0])
                else:
                    not_found.append(s)

    good_proposals = df.iloc[good_rows]
    return good_proposals, not_found

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