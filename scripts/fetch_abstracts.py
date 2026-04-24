from Bio import Entrez
import pandas as pd
from tqdm import tqdm

def search_pubmed(query, email, retmax=10000):
    Entrez.email = email
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax=str(retmax),
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results['IdList']

def fetch_details(id_list, email):
    ids = ','.join(id_list)
    Entrez.email = email
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    records = Entrez.read(handle)
    return records

# --- 실행 ---
MY_EMAIL = "crazat@naver.com"
# MeSH Term을 활용하여 검색 정확도 높이기
QUERY = '"Alzheimer disease"[Mesh] AND ("target"[All Fields] OR "pathway"[All Fields])'

print("Searching PubMed...")
id_list = search_pubmed(QUERY, MY_EMAIL, retmax=20000) # 예시로 2만개 수집

print(f"Found {len(id_list)} results. Fetching details...")
records = fetch_details(id_list, MY_EMAIL)

abstracts = []
for record in tqdm(records['PubmedArticle']):
    pmid = record['MedlineCitation']['PMID']
    try:
        abstract = record['MedlineCitation']['Article']['Abstract']['AbstractText']
        abstracts.append({'pmid': pmid, 'abstract': ' '.join(abstract)})
    except KeyError:
        continue # 초록이 없는 경우 건너뛰기

df = pd.DataFrame(abstracts)
df.to_csv('nsclc_abstracts.csv', index=False)
print("Data saved to nsclc_abstracts.csv")