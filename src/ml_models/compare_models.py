from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import os

base_dir = Path(__file__).parent.parent.parent

# Function to plot regression metrics
def plot_regression_metrics(results_df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    results_df.plot(x='Model', y='rmse', kind='bar', ax=axes[0], legend=False, color='skyblue')
    axes[0].set_title('RMSE Vergleich')
    axes[0].set_ylabel('RMSE')
    axes[0].set_xlabel('Modell')
    axes[0].set_xticklabels(results_df['Model'], rotation=20, ha='right')

    results_df.plot(x='Model', y='r2', kind='bar', ax=axes[1], legend=False, color='orange')
    axes[1].set_title('R2 Vergleich')
    axes[1].set_ylabel('R2')
    axes[1].set_xlabel('Modell')
    axes[1].set_xticklabels(results_df['Model'], rotation=20, ha='right')

    plt.tight_layout()
    plt.show()
    # Save the plot
    output_path = base_dir / 'models/metrics/model_comparison_plot.png'
    fig.savefig(output_path, bbox_inches='tight')

# Plot metrics for canceled predictions
def plot_canceled_metrics(csv_path, title, output_path):
    df = pd.read_csv(csv_path)
    metrics = df.iloc[0].to_dict()
    metrics_names = ['precision', 'recall', 'f1']
    metrics_values = [metrics[m] for m in metrics_names]
    plt.figure(figsize=(8,5))
    plt.bar(metrics_names, metrics_values, color=['royalblue', 'orange', 'green'])
    plt.ylim(0, 1)
    plt.title(title)
    plt.ylabel('Wert')
    for i, v in enumerate(metrics_values):
        plt.text(i, v + 0.01, f"{v:.2f}", ha='center')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.show()
    plt.close()

if __name__ == "__main__":
    metrics_files = {
        'LightGBM (mit Wetterdaten)': base_dir / 'models/metrics/lightgbm_metrics_delay_minutes.csv',
        'LightGBM (ohne Wetterdaten)': base_dir / 'models/metrics/lightgbm_metrics_without_delay_minutes.csv',
        'XGBoost (mit Wetterdaten)': base_dir / 'models/metrics/xgboost_metrics_delay_minutes.csv',
        'XGBoost (ohne Wetterdaten)': base_dir / 'models/metrics/xgboost_metrics_without_delay_minutes.csv',
    }

    # Load metrics from CSV files
    results = []
    for name, path in metrics_files.items():
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        df = pd.read_csv(full_path)
        # Convert column names to lowercase for consistency
        df.columns = [c.lower() for c in df.columns]
        row = {'Model': name}
        row['rmse'] = df['rmse'][0] if 'rmse' in df.columns else df.iloc[0, 0]
        row['r2'] = df['r2'][0] if 'r2' in df.columns else df.iloc[0, 1]
        results.append(row)

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(by='rmse', ascending=True).reset_index(drop=True)
    plot_regression_metrics(results_df)

    # With weather data
    canceled_metrics_path = base_dir / 'models/metrics/lightgbm_metrics_canceled.csv'
    output_path_canceled = base_dir / 'models/metrics/canceled_metrics_plot.png'
    plot_canceled_metrics(canceled_metrics_path, 'LightGBM: Ausfälle (mit Wetterdaten)',
                          output_path_canceled)

    # Without weather data
    canceled_metrics_path_wo = base_dir / 'models/metrics/lightgbm_metrics_without_canceled.csv'
    output_path_canceled_wo = base_dir / 'models/metrics/canceled_metrics_plot_without_weather.png'
    plot_canceled_metrics(canceled_metrics_path_wo, 'LightGBM: Ausfälle (ohne Wetterdaten)',
                          output_path_canceled_wo)
