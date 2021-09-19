import random
import csv

sample_key = random.sample(range(1,1000),500) #1천개 중 백개
sample_value = random.sample(range(1,10000), 500) #1천개 중 백개

index = 0
with open('input_data.csv', 'w', newline='') as f:
    wr = csv.writer(f)
    while index != len(sample_key):
        wr.writerow([sample_key[index],sample_value[index]])
        index += 1
                
