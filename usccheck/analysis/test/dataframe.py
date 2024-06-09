import pandas as pd

# Sample DataFrame
data = {
    'Category': ['A', 'B', 'A', 'B', 'A', 'B'],
    'Value': [10, 20, 30, 40, 50, 60]
}

df = pd.DataFrame(data)

# Group by 'Category' and count occurrences of each group
grouped_count = df.groupby('Category').size()
print(grouped_count, type(grouped_count))
print(grouped_count.index)
print("A" in grouped_count.index)
print(type(grouped_count[grouped_count.index[0]]))
print(grouped_count[grouped_count.index[0]])
for index in grouped_count.index:
    print(index)

# Group by 'Category' and count non-null values in each group
grouped_count = df.groupby('Category').count()

print(grouped_count, type(grouped_count))
print(grouped_count.index)
print("A" in grouped_count.index)
print(grouped_count.loc[grouped_count.index[0], "Value"])

for index in grouped_count.index:
    print(index)
