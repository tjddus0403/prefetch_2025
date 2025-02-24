import pandas as pd

trace = 'bc'
# raw 데이터 주소 설정
# 학습 및 검증에 사용할 데이터셋
dataset_raw = f"./raw/{trace}_4m.cstate"
# vocab에는 등장하는 모든 주소가 들어가야 함
vocabset_raw = f"./raw/{trace}_5m.cstate"

# csv 데이터 주소 설정
dataset_csv = f"./csv/{trace}_train.csv"
vocabset_csv = f"./csv/{trace}_vocab.csv"
testset_csv = f"./csv/{trace}_test.csv"

def create_csv(file_path):
    input_list = list()
    output_list = list()
    with open(file_path, 'r') as dataset:
        line = dataset.readline().split()
        while line:
            strline = [str(dstr) for dstr in line]
            input_list.append(" ".join(strline[:-1]))
            output_list.append(strline[-1])
            line = dataset.readline().split()

    final_data = pd.DataFrame(input_list, columns=['pa'])
    final_data['label'] = output_list

    if file_path == dataset_raw:
        final_data.to_csv(dataset_csv, index=False)
        print("Complete create train/val dataset")
    elif file_path == vocabset_raw:
        final_data.to_csv(vocabset_csv, index=False)
        print("Complete create vocab dataset")
        test_data = final_data.iloc[-1000000:]
        test_data.to_csv(testset_csv, index=False)
        print("Complete create test dataset")

if __name__ == "__main__":
    create_csv(dataset_raw)
    create_csv(vocabset_raw)