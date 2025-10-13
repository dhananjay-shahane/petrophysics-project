import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class Kmeans_Clustering:
    def __init__(self, datasets, n_clusters=2):
        """Initialize with multiple datasets and number of clusters."""
        self.datasets = [pd.DataFrame(data) for data in datasets]
        self.n_clusters = n_clusters
        self.scaled_data = None
        self.kmeans = None
        self.cluster_names = {}
        self.cluster_colors = {}

    def filter_data(self, bounds):
        """Filter the data based on specified bounds for each column."""
        for df in self.datasets:
            for column, (lower, upper) in bounds.items():
                df.drop(df[(df[column] < lower) | (df[column] > upper)].index, inplace=True)

    def prepare_data(self):
        """Prepare and standardize the data."""
        # Define lower and upper bounds for each column
        bounds = {
            'GR': (0, 100),
            'NPHI': (0, 0.5),
            'RHOB': (1.5, 3.0)
        }
        
        self.filter_data(bounds)

        # Concatenate all datasets
        self.df = pd.concat(self.datasets, ignore_index=True)
        
        # Select features for clustering
        features = ['GR', 'NPHI', 'RHOB']
        X = self.df[features]
        
        # Standardize the features
        scaler = StandardScaler()
        self.scaled_data = scaler.fit_transform(X)

    def perform_clustering(self):
        """Perform K-Means clustering on the data."""
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.df['Cluster'] = self.kmeans.fit_predict(self.scaled_data)

        # Assign arbitrary names and discrete colors to each cluster
        cluster_names = [f"Cluster {i + 1}" for i in range(self.n_clusters)]
        discrete_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                           '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']  # Up to 10 discrete colors

        for i in range(self.n_clusters):
            self.cluster_names[i] = cluster_names[i]
            self.cluster_colors[i] = discrete_colors[i % len(discrete_colors)]

    def visualize_clusters(self):
        """Visualize the clusters."""
        plt.figure(figsize=(10, 6))
        for cluster in range(self.n_clusters):
            cluster_data = self.df[self.df['Cluster'] == cluster]
            plt.scatter(cluster_data['GR'], cluster_data['RHOB'], 
                        color=self.cluster_colors[cluster], 
                        label=self.cluster_names[cluster], 
                        marker='o', zorder=3)  # Set zorder to place points above the grid

        # Add titles and labels
        plt.title('K-Means Clustering of Minerals', fontsize=16)
        plt.xlabel('Gamma Ray (GR)', fontsize=14)
        plt.ylabel('Bulk Density (RHOB)', fontsize=14)

        # Show grid
        plt.grid(zorder=1)  # Set zorder for grid to be below the points
        plt.legend()
        plt.show()

    def plot_depth_vs_cluster(self):
        """Plot depth versus cluster using a strip plot."""
        plt.figure(figsize=(10, 6))
        sns.stripplot(data=self.df, x='Cluster', y='DEPTH', jitter=True, order=sorted(self.df['Cluster'].unique()))
        
        # Invert y-axis to have depth increase from top to bottom
        plt.gca().invert_yaxis()
        plt.title('Depth vs Cluster', fontsize=16)
        plt.xlabel('Cluster', fontsize=14)
        plt.ylabel('Depth', fontsize=14)
        plt.grid()
        plt.show()

    def get_clustered_dataframe(self):
        """Return the original DataFrame with the cluster column added."""
        return self.df

    def predict_clusters(self, new_data):
        """Predict clusters for new dataset."""
        new_df = pd.DataFrame(new_data)
        
        # Standardize the features using the same scaler
        scaler = StandardScaler()
        scaled_new_data = scaler.fit_transform(new_df[['GR', 'NPHI', 'RHOB']])
        
        # Predict clusters
        new_df['Cluster'] = self.kmeans.predict(scaled_new_data)
        new_df['Cluster_Name'] = new_df['Cluster'].map(self.cluster_names)
        new_df['Cluster_Color'] = new_df['Cluster'].map(self.cluster_colors)
        return new_df

    def run(self):
        """Run the full clustering process."""
        self.prepare_data()
        self.perform_clustering()
        print(self.get_clustered_dataframe())  # Print the resulting DataFrame with clusters
        self.visualize_clusters()
        self.plot_depth_vs_cluster()

# Generate a depth series and fill in values for GR, NPHI, and RHOB
depth_series = np.arange(0, 100.1, 0.1)

# Generating values for GR, NPHI, and RHOB
np.random.seed(42)  # For reproducibility
GR_values = np.random.uniform(40, 80, size=depth_series.shape)  # Random values between 40 and 80
NPHI_values = 0.2 - (depth_series * 0.002)  # NPHI decreases linearly with depth
RHOB_values = 2.4 + (depth_series * 0.004)  # RHOB increases linearly with depth

# Create dataset
dataset1 = pd.DataFrame({
    'DEPTH': depth_series,
    'GR': GR_values,
    'NPHI': NPHI_values,
    'RHOB': RHOB_values
})

# Generate a second dataset with slightly different values
depth_series2 = np.arange(100, 200.1, 0.1)
GR_values2 = np.random.uniform(60, 90, size=depth_series2.shape)  # Random values between 60 and 90
NPHI_values2 = 0.25 - (depth_series2 * 0.0025)  # NPHI decreases linearly with depth
RHOB_values2 = 2.5 + (depth_series2 * 0.005)  # RHOB increases linearly with depth

# Create the second dataset
dataset2 = pd.DataFrame({
    'DEPTH': depth_series2,
    'GR': GR_values2,
    'NPHI': NPHI_values2,
    'RHOB': RHOB_values2
})

# Create an instance of MineralClusterer with 10 clusters
mineral_clusterer = MineralClusterer([dataset1, dataset2], n_clusters=10)

# Run the clustering process
mineral_clusterer.run()

# Sample new data for prediction
new_data = {
    'DEPTH': [1100, 1150, 1200, 1250, 1300],
    'GR': [66, 63, 69, 72, 70],
    'NPHI': [0.12, 0.15, 0.11, 0.10, 0.09],
    'RHOB': [2.55, 2.60, 2.63, 2.58, 2.55]
}

# Predict clusters for the new dataset
predicted_clusters = mineral_clusterer.predict_clusters(new_data)
print("\nPredicted Clusters for New Data:")
print(predicted_clusters)
