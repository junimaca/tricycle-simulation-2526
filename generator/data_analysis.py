import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

df = pd.read_csv('simulations.csv')

def file_name_maker(str):
    return str.lower().replace(' ', "_")

def completion_rate_graphs():
    global df

    for ind_var in ['Number of Tricycles', 'Number of Sectors', 'Intersection Algorithm']:
        for dep_var in ['Completion Rate', 'Average Wait Time', 'Efficiency Percentage']:
            sns.boxplot(
                data=df,
                x=ind_var,
                y="Completion Rate",
            )

            plt.title(f"{ind_var} vs Completion Rate")
            plt.savefig(f"figures/{file_name_maker(ind_var)}_vs_{file_name_maker(dep_var)}.png")
            plt.show()


def main():
    global df

    # sns.boxplot(
    #     data=df,
    #     x="Number of Tricycles",
    #     y="Average Wait Time",
    #     hue='Intersection Algorithm'
    # )

    # plt.title("Average Wait Time vs Number of Tricycles")
    # plt.show()
    # plt.savefig("figures/wait_time.png")

    completion_rate_graphs()

if __name__ == '__main__':
    main() 