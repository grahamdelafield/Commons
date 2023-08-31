import requests 
import json

def _get_subcell_location(response_portion: dict):
    """Grab subcellular location from response."""
    
    comments = response_portion['comments']
    # print(len(comments))
    for c in comments:
        if c['commentType'] == 'SUBCELLULAR LOCATION':
            loc = c['subcellularLocations'][0]['location']['value']
    return loc            

def send_accessions(protein_accession: list) -> dict:
    """Takes list of Uniprot protein accessions, returns hash map of gene names.
    
    :arg protein_accession: (list)  list of protein accession numbers
    :returns: json/dict
    """

    # join accessions
    accs = "%2C".join(protein_accession)
    
    # include in url
    base_url = f"https://rest.uniprot.org/uniprotkb/accessions?accessions={accs}"
    
    # get response
    r = requests.get(base_url)

    # dump into json object
    resp = json.loads(r.text)
    return resp

def parse_response(uniprot_resp: dict, wanted_value: str):
    """Parses uniprot response.
    
    :arg unriprot_resp: (dict)  response from uniprot
    :arg wanted_value:  (str)   value requested from response
    
    :returns:   dict(accession -> gene)
    """
    
    # account for single searches
    if len(uniprot_resp) != 0:
        data = uniprot_resp["results"]
    else:
        data = uniprot_resp
    
    # keep track of results and misisng values
    lookup = {}
    count = 0

    for entry in data:
        # grab accession that was passed in
        val = entry["primaryAccession"]
        
        # some accessions do not have associated genes
        try:
            match wanted_value:
                case "gene":
                    info_result = entry["genes"][0]["geneName"]["value"]
                case "description":
                    info_result = entry['proteinDescription']['recommendedName']['fullName']['value']
                case "sequence":
                    info_result = entry["sequence"]["value"]
                case "sc_location":
                    info_result = _get_subcell_location(entry)
                case other:
                    raise Exception(f"{other} is not currently supported in the uniprot caller.")
        except:
            info_result = None
            count += 1
        
        # add gene to map
        lookup[val] = info_result
    
    # provide warning
    if count > 0:
        print(f"{count} {wanted_value}(s) were not mapped!")

    return lookup