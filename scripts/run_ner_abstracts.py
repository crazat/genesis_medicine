import os
import pandas as pd
from transformers import pipeline
from datasets import Dataset

# --- 1. 견고한 방식으로 원본 데이터 불러오기 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'alz_abstracts.csv')
print(f"데이터 로딩 중: {file_path}")
df = pd.read_csv(file_path)

# --- 2. Hugging Face Dataset으로 변환 ---
hf_dataset = Dataset.from_pandas(df[['abstract']])

# --- 3. 파이프라인 생성 및 배치 처리 실행 ---
ner_pipeline = pipeline(
    "ner",
    model="d4data/biomedical-ner-all",
    aggregation_strategy="simple",
    device=0
)
print(f"총 {len(hf_dataset)}개의 초록을 배치 처리 방식으로 분석합니다...")
all_entities = ner_pipeline(hf_dataset['abstract'], batch_size=64)
print("분석 완료.")


# --- 4. 결과 정리 (데이터 클리닝) ---
# V-- 이 부분이 추가되었습니다 --V
print("결과 데이터 정리 중 (NumPy 타입 -> 기본 float 타입 변환)...")
cleaned_all_entities = []
for entities_list in all_entities:
    cleaned_entities_per_abstract = []
    if entities_list:
        for entity in entities_list:
            # 각 entity의 score를 일반 float으로 변환하여 새로운 딕셔너리를 만듭니다.
            cleaned_entity = entity.copy()
            cleaned_entity['score'] = float(entity['score'])
            cleaned_entities_per_abstract.append(cleaned_entity)
    cleaned_all_entities.append(cleaned_entities_per_abstract)
print("정리 완료.")
# ^-- 여기까지가 추가된 부분입니다 --^


# --- 5. 최종 결과 추가 및 저장 ---
df['entities'] = cleaned_all_entities # 정리된 데이터를 'entities' 컬럼에 할당
output_path = os.path.join(script_dir, 'ner_results_alz.csv')
df.to_csv(output_path, index=False)
print(f"최종 결과가 {output_path} 파일로 저장되었습니다.")