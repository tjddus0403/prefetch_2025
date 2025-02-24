#!/bin/bash

# # 기존 output.txt 삭제 (기존 내용 유지하고 싶으면 제거)
# rm -f output.txt  

for i in {0..9}
do
    python3 main.py $i >> output.txt 2>&1  # 표준 출력과 에러 출력 모두 저장
    echo "--------------------------------" >> output.txt  # 구분선 추가
done