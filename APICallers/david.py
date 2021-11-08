import pandas as pd
import re
import chromedriver_autoinstaller
from os import remove
from selenium.webdriver import Chrome
from pathlib import PurePath, Path


VALID_OUTPUTS = ["mf", "bp", "cc"]
VALID_ACCESSION = [
    "AFFYMETRIX_3PRIME_IVT_ID",
    "AFFYMETRIX_EXON_GENE_ID",
    "AFFYMETRIX_SNP_ID",
    "AGILENT_CHIP_ID",
    "AGILENT_ID",
    "AGILENT_OLIGO_ID",
    "ENSEMBL_GENE_ID",
    "ENSEMBL_TRANSCRIPT_ID",
    "ENTREZ_GENE_ID",
    "FLYBASE_GENE_ID",
    "FLYBASE_TRANSCRIPT_ID",
    "GENBANK_ACCESSION",
    "GENPEPT_ACCESSION",
    "GENOMIC_GI_ACCESSION",
    "PROTEIN_GI_ACCESSION",
    "ILLUMINA_ID",
    "IPI_ID",
    "MGI_ID",
    "GENE_SYMBOL",
    "PFAM_ID",
    "PIR_ACCESSION",
    "PIR_ID",
    "PIR_NREF_ID",
    "REFSEQ_GENOMIC",
    "REFSEQ_MRNA",
    "REFSEQ_PROTEIN",
    "REFSEQ_RNA",
    "RGD_ID",
    "SGD_ID",
    "TAIR_ID",
    "UCSC_GENE_ID",
    "UNIGENE",
    "UNIPROT_ACCESSION",
    "UNIPROT_ID",
    "UNIREF100_ID",
    "WORMBASE_GENE_ID",
    "WORMPEP_ID",
    "ZFIN_ID",
]


class David:
    """Sends API call to DAVID and stores response"""

    def __init__(self, call_type, query_list, accession_type):

        self.call_type_lookup = {
            "mf": "GOTERM_MF_DIRECT",
            "bp": "GOTERM_BP_DIRECT",
            "cc": "GOTERM_CC_DIRECT",
        }

        if call_type not in VALID_OUTPUTS:
            raise ValueError(
                f"You requested call type {call_type} but DAVID only accepts one of {VALID_OUTPUTS}"
            )

        if accession_type not in VALID_ACCESSION:
            raise ValueError(
                f"{accession_type} must be one of {VALID_ACCESSION}"
            )

        self.wanted_output = self.call_type_lookup[call_type]
        self.queried_items = [str(item) for item in query_list]
        self.accession_type = accession_type

        # install current chromedriver
        chromedriver_autoinstaller.install(cwd=True)

    def __repr__(self):
        return f"""DAVID caller grabbing {self.wanted_output} using {len(self.queried_items)} items."""

    def create_query_string(self, tool):
        """Creates DAVID API-usable url"""
        url = f'https://david.ncifcrf.gov/api.jsp?type={self.accession_type}&ids={",".join(self.queried_items)},&tool={tool}&annot={self.wanted_output}'
        return url

    def make_call(self, tool="summary"):
        """Calls to DAVID with given URL"""
        self.driver = Chrome()
        self.driver.get(self.create_query_string(tool))
        self.grab_data()
        return

    def grab_data(self):
        """Searches selenium webelements to get data"""
        attrs = self.driver.find_elements_by_class_name("parent")

        # find correct output section
        gene_ont = [a for a in attrs if a.text.startswith("Gene_Ontology")][0]
        gene_ont.click()

        # search for all summary rows
        valid_opts = self.driver.find_elements_by_class_name("summary_row")

        # find row with expected output
        selected_opt = [
            elem for elem in valid_opts if re.search(self.wanted_output, elem.text)
        ][0]
        chart_btn = selected_opt.find_elements_by_tag_name("td")[3]
        chart_btn.click()

        # swtich to new window
        self.driver.switch_to_window(self.driver.window_handles[1])

        # find download button
        download = self.driver.find_elements_by_tag_name("a")
        download_btn = [d for d in download if re.search("Download File", d.text)][0]
        download_btn.click()

        # switch back to main window
        self.driver.switch_to_window(self.driver.window_handles[2])

        # grab body text
        text = self.driver.find_element_by_tag_name("body").text

        self.format_text(text)

    def format_text(self, text):

        # replace spaces in headers
        existing = ["List Total", "Pop Hits", "Pop Total", "Fold Enrichment"]
        changed = ["List_Total", "Pop_Hits", "Pop_Total", "Fold_Enrichment"]

        for i, pat in enumerate(existing):
            pattern = re.compile(pat)
            text = re.sub(pattern, changed[i], text)

        # replace spaces in GO term
        go_pattern = re.compile(r"(GO:\d*\~.*)(\s\d\s\d*\.)")
        for line in text.split("\n")[1:]:
            match = re.search(go_pattern, line)
            if match is None:
                print("None in", line)
            else:
                repl = re.sub(" ", "_", match.group(1))
                text = re.sub(match.group(), repl, text)

        # conjoin genes to preserve column integrity
        gene_ids = re.compile(r"(\w*)(,\s)")
        terminal_gene = re.compile(r"(,\s)(\w*\s)")
        for line in text.split("\n")[1:]:

            prot_match = re.finditer(gene_ids, line)
            term_prot = re.search(terminal_gene, line)
            prot_list = [m.group(1) for m in prot_match] + [term_prot.group(2)[:-1]]
            full_match = ", ".join(prot_list)

            text = re.sub(full_match, full_match.replace(" ", ""), text)

        with open('clean_text.txt', 'w') as f:
            f.write(text)
        self.go_to_frame()
        # self.driver.quit()

    def go_to_frame(self):
        """Turns text into usefule dataframe"""
        df = pd.read_csv("clean_text.txt", delimiter=" ")

        # split GO term to yield ID and term text
        df[["ID", "Term"]] = df.Term.str.split("~", expand=True)

        # create new file
        df.to_csv(f"DAVID_{self.wanted_output}.csv", index=False)

        # remove unneeded text file
        remove("clean_text.txt")


if __name__ == "__main__":
    test_type = "ENTREZ_GENE_ID"
    test_items = ["2919", "6347", "6348", "6364"]
    d = David("cc", query_list=test_items, accession_type=test_type)
    d.make_call()
