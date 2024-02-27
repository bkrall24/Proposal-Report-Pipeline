
#!/Users/rebeccakrall/miniconda3/envs/pra
from template_filling import proposal_to_report
import os
from datetime import datetime

if __name__ == "__main__":

    template_path = "/Users/rebeccakrall/Data/Proposal-Report-Data/Templates/Report_Template_dxpt.docx"
    proposal_dir = "/Volumes/O-Drive/Clients/_PROPOSALS FOR REPORT TEMPLATE_Becca/Proposals"
    report_dir = "/Volumes/O-Drive/Clients/_PROPOSALS FOR REPORT TEMPLATE_Becca/Reports"
    # proposal_dir = "/Users/rebeccakrall/Desktop/Proposal"
    # report_dir = "/Users/rebeccakrall/Desktop/Report"

    current_proposals = os.listdir(proposal_dir)
    current_reports = os.listdir(report_dir)

    proposal_names = [x.split('.docx')[0] for x in current_proposals]
    report_names = [x.split('_REPORT.docx')[0] for x in current_reports]

    unmatched = [p for r,p in zip(proposal_names, current_proposals) if r not in report_names]
    for u in unmatched:
        proposal_path = os.path.join(proposal_dir, u)
        temp, save_path = proposal_to_report(proposal_path, save_path = report_dir)

    logfile = "/Users/rebeccakrall/Code/Proposal-Report-Pipeline/report.txt"
    with open(logfile, 'a') as f:
        if len(unmatched) > 0:
            t = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            f.write(t)
            f.write('\n')
            for u in unmatched:
                f.write(u + " Report generated")
                f.write('\n')