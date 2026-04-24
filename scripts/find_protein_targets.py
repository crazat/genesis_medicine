import pandas as pd
import ast
import re
from collections import Counter
import requests

# --- 1. 데이터 및 유전자 목록 로딩 ---
print("데이터 및 유전자 목록 로딩 중...")
# 이전에 생성한 최종 NER 결과 파일
df = pd.read_csv("/workspace/scripts/ner_results_alz.csv")
df['entities'] = df['entities'].apply(ast.literal_eval)

# 1. URL에서 직접 텍스트 데이터를 가져옵니다.
url = "https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt"
print("HGNC 유전자 목록을 URL에서 직접 다운로드합니다...")
response = requests.get(url)
response.raise_for_status()  # 요청이 실패하면 오류를 발생시킴

# 2. 가져온 텍스트를 한 줄씩 나누고, 이전과 동일하게 처리합니다.
# TSV(탭으로 구분된 값) 파일이므로, 각 줄에서 첫 번째 항목(유전자 기호)만 추출합니다.
lines = response.text.strip().splitlines()
gene_list = {line.split('\t')[1].lower() for line in lines[1:]}


# --- 2. 핵심 영역('해마') 관련 데이터 필터링 ---
# 'hippocampus'가 생물학적 구조로 태깅된 초록을 모두 찾습니다.
hippocampus_abstracts = []
for index, row in df.iterrows():
    for entity in row['entities']:
        # 'hippocampus' 라는 단어가 'Biological_structure'로 태깅된 경우
        if entity.get('entity_group') == 'Biological_structure' and 'hippocampus' in entity.get('word', ''):
            hippocampus_abstracts.append(row['abstract'])
            break # 한 초록에 여러 번 나와도 한 번만 추가

print(f"'해마(hippocampus)'를 언급한 초록 {len(hippocampus_abstracts)}개를 찾았습니다.")


# --- 3. 필터링된 초록 내에서 단백질/유전자 이름 추출 ---
print("해마 관련 초록에서 단백질 후보군 추출 중...")
mentioned_genes = []
for abstract in hippocampus_abstracts:
    # 텍스트를 소문자로 바꾸고, 단어 단위로 분리 (간단한 정규식 사용)
    words = set(re.findall(r'\b\w+\b', abstract.lower()))
    
    # 초록의 단어들과 전체 유전자 목록을 비교하여 겹치는 것을 찾습니다.
    found_genes = words.intersection(gene_list)
    mentioned_genes.extend(list(found_genes))


# --- 4. 최종 후보군 순위화 ---
# 가장 자주 언급된 상위 30개 단백질/유전자 후보
top_30_protein_targets = Counter(mentioned_genes).most_common(30)

print("\n--- 최종 분석 결과 ---")
print("[알츠하이머 '해마' 영역에서 가장 자주 언급된 단백질/유전자 Top 30]")
for gene, count in top_30_protein_targets:
    print(f"{gene.upper():<15} | 언급 횟수: {count}")


# --- 5. 다음 단계 제안 ---
print("\n--- 다음 단계 제안 ---")
if top_30_protein_targets:
    top_protein = top_30_protein_targets[0][0].upper()
    print(f"✅ 1. AlphaFold: '{top_protein}'의 3D 단백질 구조를 AlphaFold DB에서 확인하고, 약물 결합 포켓을 예측할 수 있습니다.")
    print("✅ 2. GNN: 이 순위 데이터를 기반으로 '단백질-질병' 관계 예측 GNN 모델을 훈련시키거나, 알려진 약물과의 상호작용을 예측하는 모델을 만들 수 있습니다.")