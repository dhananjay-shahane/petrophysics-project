import numpy as np
import pandas as pd
from scipy.optimize import minimize

class VolumeOptimizer:
    def __init__(self, characteristic_values):
        self.characteristic_values = characteristic_values

    def objective(self, volumes, target_values, uncertainties):
        predicted = self.characteristic_values @ volumes
        weight = 1 / (uncertainties ** 2)
        return np.sum(weight * (predicted - target_values) ** 2)

    def constraint_sum(self, volumes):
        return np.sum(volumes) - 1

    def solve_volumes(self, target_values, uncertainties):
        initial_guess = [0.25, 0.25, 0.25]
        constraints = [{'type': 'eq', 'fun': self.constraint_sum}]
        bounds = [(0.02, 1) for _ in range(len(initial_guess))]

        result = minimize(self.objective, initial_guess, args=(target_values, uncertainties), 
                          constraints=constraints, bounds=bounds)

        if result.success:
            return result.x
        else:
            raise ValueError("Optimization failed: " + result.message)

    def calculate_volumes_from_df(self, df):
        optimized_volumes = df.apply(
            lambda row: self.solve_volumes(
                row[['target_1', 'target_2', 'target_3']].values, 
                np.array([row['uncertainty_1'], row['uncertainty_2'], row['uncertainty_3']])
            ), 
            axis=1
        )

        volumes_df = pd.DataFrame(optimized_volumes.tolist(), columns=['Volume_Quartz', 'Volume_Water', 'Volume_Clay'])

        # Reconstruct the target values using the optimized volumes
        reconstructed_targets = volumes_df.values @ self.characteristic_values.T

        # Create a DataFrame for reconstructed targets
        reconstructed_df = pd.DataFrame(reconstructed_targets, columns=[f'Reconstructed_Target_{i+1}' for i in range(reconstructed_targets.shape[1])])
        
        # Add the original targets and volumes for reference
        result_df = pd.concat([df['DEPTH'], volumes_df, reconstructed_df], axis=1)

        return result_df

if __name__ == "__main__":
    # Characteristic values for quartz, water, and clay
    quartz = [15, -0.04, 2.65]
    water = [0, 1, 1]
    clay = [110, 0.5, 2.58]
    characteristic_values = np.array([quartz, water, clay]).T

    # Create a DataFrame with target values and uncertainty ranges for each target
    data = {
        'target_1': [87.7646, 87.3053, 86.8459, 85.2646, 82.3496, 31.6220, 79.8000],
        'target_2': [0.4160500, 0.4251800, 0.4397400, 0.4592100, 0.4784100, 0.2229800, 0.4982700],
        'target_3': [2.589260, 2.537750, 2.480800, 2.452950, 2.446090, 2.489500, 2.591330],
        'uncertainty_1': [3] * 7,  # Uncertainty for target 1
        'uncertainty_2': [0.02] * 7, # Uncertainty for target 2
        'uncertainty_3': [0.02] * 7, # Uncertainty for target 3
    }
    df = pd.DataFrame(data)

    # Initialize the optimizer
    optimizer = VolumeOptimizer(characteristic_values)

    # Calculate volumes and reconstructed targets
    result_df = optimizer.calculate_volumes_from_df(df)

    # Display results
    print(result_df)
