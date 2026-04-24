from transformers import pipeline
import pandas as pd
from tqdm import tqdm

ner_pipeline = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")
text = "Apolipoprotein E (APOE) is a major genetic risk factor for Alzheimer's disease, and drugs like Donepezil are used for treatment."
entities = ner_pipeline(text)
# 결과: [{'entity_group': 'GENE_OR_GENE_PRODUCT', 'word': 'egfr', ...}, {'entity_group': 'CANCER', 'word': 'non - small cell lung cancer', ...}]

print(entities)