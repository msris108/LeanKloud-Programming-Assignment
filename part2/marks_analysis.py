import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])

# dropping column
subjects = df.columns.drop('Name')

# total calculation
df['Total'] = df.sum(axis = 1, skipna=True) 

# loop:1
for subject in subjects:
	print("Topper in {} is {}".format(subject, df[df[subject] == df[subject].max()].get('Name').tolist()[0]))

# sorting
toppers = df.sort_values(by=['Total'], ascending=False).head(3)['Name'].tolist()

print("Best students in the class are ", tuple(toppers))

'''
	Usage : python marks_analysis <filename>.csv
	
	This script can handle any number of subjects.

	Time Complexity Analysis:
	-------------------------
		n = number of students
		m = number of subjects 

		Dropping Column = m

		Total(SUM) Calcualation = m * n

		max() -> takes place in O(1)
		=> loop:1 = n * m

		sorting = n log(n)

		Total time complexity = m + (n * m) + (n * m) + n log(n)

		Therefore complete program executes in O(n * m)
'''
