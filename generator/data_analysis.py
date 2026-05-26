import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

df = None

def create_unified_dataframe():
    global df

    csv_files = [os.path.join("csv", f) for f in os.listdir("csv") if f.endswith('.csv')]
    df = pd.concat(map(pd.read_csv, csv_files))
    # # print(df["Seed"].value_counts())
    # df.groupby("Seed").size().unique()
    # # valid_seeds = unfiltered_df["Seed"].value_counts()
    # # valid_seeds = valid_seeds[valid_seeds == 24].index

    # # df = unfiltered_df[unfiltered_df["Seed"].isin(valid_seeds)]


def file_name_maker(str):
    return str.lower().replace(' ', "_")

def main_graphs():
    global df

    for ind_var in ['Number of Tricycles', 'Number of Sectors', 'Intersection Algorithm']:
        for dep_var in ['Completion Rate', 'Total Trips Completed', 'Average Wait Time', 'Total Distance', 'Productive Distance', 'Efficiency Percentage']:
            sns.boxplot(
                data=df,
                x=ind_var,
                y=dep_var,
            )

            plt.title(f"{ind_var} vs {dep_var}")
            plt.savefig(f"figures/{file_name_maker(ind_var)}_vs_{file_name_maker(dep_var)}.png")
            plt.close()
            # plt.show()

# def poisson_distribution_graph():
#     global df

def pass_vs_eff_rate(df):
    x = df["Number of Passengers"]
    y = df["Efficiency Percentage"]
    # Third variable for coloring
    z = df["Number of Sectors"]

    plt.figure(figsize=(8, 5))  

    # -----------------------------------
    # CORRELATION
    # -----------------------------------

    correlation = x.corr(y)

    print("Pearson correlation:", correlation)

    # -----------------------------------
    # LINE OF BEST FIT
    # -----------------------------------

    m, b = np.polyfit(x, y, 1)

    # -----------------------------------
    # PLOT
    # -----------------------------------

    plt.figure(figsize=(8, 5))

    # Scatter plot
    plt.scatter(
        x,
        y,
        c=z,
        cmap="viridis",   # colormap
        alpha=0.8
    )       

    # Regression line
    plt.plot(x, m*x + b)

    plt.xlabel("Number of Passengers")
    plt.ylabel("Efficiency Rate")
    plt.title(
        f"Passengers vs Efficiency Rate\n"
        f"Correlation = {correlation:.3f}"
    )

    plt.grid(True)
    plt.savefig(f"figures/magic.png")
    plt.close()

def main():
    global df

    create_unified_dataframe()
    main_graphs()
    pass_vs_eff_rate(
        df[
            (df["Number of Tricycles"] == 15) &
            (df["Number of Sectors"] == 8)
        ]
    )

    sns.boxplot(
        data=df,
        x="Number of Sectors",
        y="Number of Passengers",
    )

    plt.savefig("figures/numofpassengers")

    print(f"Number of simulations processed: {len(df)}")
    df.to_csv('compiled_simulation_data.csv')

if __name__ == '__main__':
    main() 