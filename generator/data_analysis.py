import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

df = pd.read_csv('simulations.csv')

def main():
    global df

    sns.boxplot(
        data=df,
        x="Number of Tricycles",
        y="Average Wait Time",
        hue='Intersection Algorithm'
    )

    plt.title("test 1")
    plt.show()

if __name__ == '__main__':
    main() 