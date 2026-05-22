import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

df = None

def create_unified_dataframe():
    global df

    csv_files = [os.path.join("csv", f) for f in os.listdir("csv") if f.endswith('.csv')]
    df = pd.concat(map(pd.read_csv, csv_files))


def file_name_maker(str):
    return str.lower().replace(' ', "_")

def main_graphs():
    global df

    for ind_var in ['Number of Tricycles', 'Number of Sectors', 'Intersection Algorithm']:
        for dep_var in ['Completion Rate', 'Average Wait Time', 'Total Distance', 'Productive Distance', 'Efficiency Percentage']:
            sns.boxplot(
                data=df,
                x=ind_var,
                y=dep_var,
            )

            plt.title(f"{ind_var} vs {dep_var}")
            plt.savefig(f"figures/{file_name_maker(ind_var)}_vs_{file_name_maker(dep_var)}.png")
            plt.close()
            # plt.show()


def main():
    global df

    create_unified_dataframe()
    main_graphs()

if __name__ == '__main__':
    main() 