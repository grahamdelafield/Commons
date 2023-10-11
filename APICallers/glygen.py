import requests
import json 

def send_accessions(protein_accession: list) -> dict:
    """Takes list of Uniprot protein accessions, returns hash map of glygen responses.
    
    :arg protein_accession: (list)  list of protein accession numbers
    :returns: dict of dicts
    """

    resp = dict()

    for i, acc in enumerate(protein_accession, start=1):    
        
        try:
            
            # include in url
            base_url = f"https://api.glygen.org/protein/detail/{acc}/"
        
            # get response
            r = requests.get(base_url)

            # dump into json object
            resp[acc] = json.loads(r.text)

        except ValueError:
            print(f"Error in {acc}, which can't be mapped")

        print(f"{(i / len(protein_accession))*100:.2f}%", end="\r")

    return resp



def parse_response(response: str, wanted_quantity: str):
    """
    Looks throug the reponse text and extracts the desired characteristics.

    :arg response:  (str)   output from func(send_accessions)
    :arg qanted_quantity:   (str)   desired characteristic
        currently one of ["type", "category"]
    """
    ret = dict()

    for acc, entry in response.items():

        # linkage, category = [], []

        glyc_info = entry.get("glycosylation", None)

        results = []

        if glyc_info is None:
            # linkage.append(None)
            # category.append(None)
            results.append(None)
            continue


        else:
            for item in glyc_info:
                match wanted_quantity:
                    case "type":
                        info_result = item["type"]
                    case "category":
                        info_result = item["site_category"]
                    case other:
                        raise Exception(f"{wanted_quantity} is not supported by this module, please check and try again.")
                results.append(info_result)

        ret[acc] = list(set(results))

    return ret