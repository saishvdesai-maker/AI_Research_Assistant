import json
import os


FILE = "papers.json"



def save_paper(name):

    papers = load_papers()

    papers.append(name)

    with open(FILE,"w") as f:
        json.dump(papers,f)



def load_papers():

    if not os.path.exists(FILE):
        return []

    with open(FILE,"r") as f:
        return json.load(f)