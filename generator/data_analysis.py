import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from statsmodels.miscmodels.ordinal_model import OrderedModel
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

def ordinal_reg(df):

    analysis_df = df.copy()

    if 'Efficiency Percentage' in analysis_df.columns:
        analysis_df['Eff_Level'] = pd.qcut(analysis_df['Efficiency Percentage'], q=3, labels=[0,1,2])
    else:
        return
    
    predictors = ['Number of Tricycles', 'Number of Sectors', 'Number of Passengers']
    valid_cols = [col for col in predictors if col in analysis_df.columns]

    analysis_df = analysis_df[valid_cols + ['Eff_Level']].dropna()
    X = analysis_df[valid_cols]
    y = analysis_df['Eff_Level']

    X = pd.get_dummies(X, drop_first=True, dtype=int)

    try:
        model = OrderedModel(y, X, distr='logit')
        result = model.fit(method='bfgs', disp=False)
        print(result.summary())

        plot_ordinal_probabilities(result, X, target_name='Efficiency Level')
    
    except Exception as e:
        print(f"An error occurred while fitting or graphing the ordinal model: {e}")


def plot_ordinal_probabilities(result, X, target_name="Efficiency Level"):
    """
    Plots the predicted probabilities for each ordinal category across an independent variable.
    """
    plt.figure(figsize=(10, 6))
    
    # We will pick a continuous predictor to vary across the X-axis. 
    # If 'Number of Passengers' is in your X matrix, let's use that.
    # Otherwise, fallback to the first available numeric column.
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    if 'Number of Passengers' in numeric_cols:
        plot_var = 'Number of Passengers'
    elif len(numeric_cols) > 0:
        plot_var = numeric_cols[0]
    else:
        print("No continuous numeric features available to generate a probability curve.")
        return

    # Create a smooth grid sequence across the range of that variable
    x_grid = np.linspace(X[plot_var].min(), X[plot_var].max(), 100)
    
    # Create a dummy DataFrame to hold hypothetical data for prediction
    # We hold other variables at their median value while varying the main variable
    dummy_df = pd.DataFrame(index=range(100), columns=X.columns)
    for col in X.columns:
        if col == plot_var:
            dummy_df[col] = x_grid
        else:
            dummy_df[col] = X[col].median() # Hold other factors constant
            
    # Calculate predicted probabilities for each of our 3 classes (0, 1, 2)
    predicted_probs = result.predict(dummy_df)
    
    # Labels for your ordinal categories
    labels = ['Low', 'Medium', 'High']
    colors = ['#e41a1c', '#377eb8', '#4daf4a']
    
    # Plot a line for each category
    for i in range(predicted_probs.shape[1]):
        plt.plot(
            x_grid, 
            predicted_probs.iloc[:, i], 
            label=f'P({labels[i]} {target_name})', 
            color=colors[i], 
            linewidth=2.5
        )
        
    plt.xlabel(plot_var, fontsize=12)
    plt.ylabel("Predicted Probability", fontsize=12)
    plt.title(f"Ordinal Logistic Regression: Predicted Probability of {target_name}", fontsize=14)
    plt.ylim(-0.05, 1.05)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='best', fontsize=11)
    
    os.makedirs("figures", exist_ok=True)
    plt.savefig("figures/ordinal_regression_probabilities.png", dpi=300)
    plt.close()
    print("Successfully saved probability curves to 'figures/ordinal_regression_probabilities.png'")





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

    ordinal_reg(df)

if __name__ == '__main__':
    main() 