# Code Graveyard - Reference of deleted code in case I change my mind about processes


# for inserting images
from docxtpl import DocxTemplate, subdoc, InlineImage
myimage = InlineImage(template, image_descriptor="/Users/rebeccakrall/Desktop/Example for Proposal Report Automation/Bio_Pics/Vivian Cong.jpg", width = Mm(42.672), height= Mm(42.672))


# assays and methods

assays = pd.read_excel("/Users/rebeccakrall/Desktop/Example for Proposal Report Automation/Assay Codes.xlsx")
doc = docx.Document("/Users/rebeccakrall/Desktop/Example for Proposal Report Automation/Standard  Methods -Mice 100410.docx")
toc = [p.text.split('\t')[-2] for p in doc.paragraphs if bool(re.search(r'\t+\d', p.text))]

for x in toc:
    if x in list(assays['Assay']):
        print(x+' found')