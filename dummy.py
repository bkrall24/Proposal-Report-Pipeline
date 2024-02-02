# import os

from datetime import datetime

if __name__ == "__main__":
    
    logfile = "/Users/rebeccakrall/Code/Proposal-Report-Pipeline/test.txt"
    with open(logfile, 'a') as f:
        t = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        f.write(t)
        f.write('\n')



## PATH = /Users/rebeccakrall/miniconda3/envs/pra/bin
    
## */15 * * * 1-5 /Users/rebeccakrall/Code/Proposal-Report-Pipeline/dist/template_filler > /Users/rebeccakrall/Code/Proposal-Report-Pipeline/log.txt