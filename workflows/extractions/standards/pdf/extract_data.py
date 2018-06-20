from tabula import read_pdf

def extract(source_path):
    return read_pdf(source_path, pages='all')
