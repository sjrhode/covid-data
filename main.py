import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

<<<<<<< Updated upstream
=======
#BRANCH TEST
>>>>>>> Stashed changes

# Function for reading the excel file in
def read_excel(name_in, rows_low, rows_high, sheet_in, header_in, na_in):
    new_df = pd.read_excel(name_in, sheet_name=sheet_in, header=header_in, index_col=0, na_values=na_in)
    new_df = new_df[rows_low:rows_high]
    return new_df


# Function to create individual multiindex df for some section of the maindf
def create_multiindex(df_in, rows_low, rows_high, question_in):
    new_df = df_in.iloc[rows_low:rows_high]
    # Add level to multiindex: https://stackoverflow.com/questions/14744068/prepend-a-level-to-a-pandas-multiindex
    new_df = pd.concat([new_df], keys=[question_in])
    new_df = new_df.dropna(how="all", axis=0)
    return new_df


# Tester example with data about govt guidelines/trust in them
file_1 = "CovidSocialImpacts290121 copy.xlsx"
gov_guidelines_df = read_excel(file_1, 0, 69, "Table 11", [3, 4], [":", ".."])

# Get rid of the empty "UCL1" rows that were coming up
gov_guidelines_df = gov_guidelines_df.dropna(how="all", axis=1)

# Get rid of the "1" from footnotes at end of column names
new_levels = gov_guidelines_df.columns.get_level_values(0)
for level in new_levels:
    # todo: This is fine bc it's only words which end in 1 but would potentially be an issue later
    #  if you had e.g. '16 to 41' as column name
    level_new = re.sub(r"1$", r"", level)
    gov_guidelines_df.rename(columns={level: level_new}, inplace=True)

# Cut out the subtable about reasons why it's difficult to follow measures
gov_guidelines_df = gov_guidelines_df.iloc[:53]

# todo: check for lowercase / uppercase, trailing spaces etc with "Sample size"
# Get the locations & values of the questions I will want to extract to another multiindex level
# - always 2 lines after 'sample size' row
row = gov_guidelines_df.index.get_loc("Sample size")
sample_size_locs = np.where(gov_guidelines_df.index == "Sample size")[0]
question_locs = sample_size_locs + 2
question_locs = np.insert(question_locs, 0, 0)

questions = []
for i in range(len(question_locs) - 1):
    questions.append(gov_guidelines_df.index[question_locs[i]])

# Create list of multiindex versions of the different table sections
df_list = []
for i in range(len(questions)):
    new_df = create_multiindex(gov_guidelines_df, question_locs[i], question_locs[i + 1], questions[i])
    df_list.append(new_df)

# Concatenating into one df for use as needed - but could also just use df_list to create individual graphs
gov_guidelines_multi = pd.concat(df_list)

# Test plot
# Using this as template: https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html
# And this: https://medium.com/analytics-vidhya/create-a-grouped-bar-chart-with-matplotlib-and-pandas-9b021c97e0a
gov_info_ages_df = df_list[0]
sample_size = gov_info_ages_df.iloc[-1, 0]
gov_info_ages_df = gov_info_ages_df.iloc[:-2]

# Just using values for % (not UCL, LCL)
gov_info_ages_df = gov_info_ages_df.iloc[:, [0, 3, 6, 9, 12]]

x_labels = gov_info_ages_df.index.get_level_values(1)
label_positions = np.arange(len(x_labels))

ax = gov_info_ages_df.plot(kind="bar")
fig = ax.get_figure()
fig.set_size_inches(12, 7)

# Labels and formatting
ax.legend()
ax.set_title(questions[0])
ax.set_xticks(label_positions)
ax.set_xticklabels(x_labels)
plt.xticks(rotation=0)
ax.set_ylabel(f"% (Sample size = {sample_size})")
ax.set_xlabel("Responses")

# fig.tight_layout()
plt.show()
