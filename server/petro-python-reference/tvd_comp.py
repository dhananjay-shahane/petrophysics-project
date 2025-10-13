import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
def compute_tvd_minimum_curvature(depths, deviations, azimuths):
    """Compute Total Vertical Depth (TVD) using the Minimum Curvature method."""
    tvds = [depths[0]]  # TVD at the first depth point
    norths = [0]  # TVD at the first depth point
    souths = [0]  # TVD at the first depth point
    cumulative_tvd = [depths[0]]  # Cumulative TVD starts with the first depth point
    #print(deviations)
    #deviations = np.array(deviations)  # Convert to a NumPy array if it's not already
    pi = 3.141592653589793
    for i in range(1, len(depths)):
        
        #print('min curve', i-1, type(depths[i-1]), deviations[i-1], azimuths[i-1])
        D = depths[i] - depths[i - 1]  # Calculate vertical distance
        deviation_radians = (np.radians)(0.5*(deviations[i - 1]+ deviations[i]))  # Convert deviation to radians
        azimuth_radians = np.radians(0.5*(azimuths[i - 1]+azimuths[i]))  # Convert deviation to radians

        # Calculate vertical depth change using the deviation
        vertical_distance = D * np.cos(deviation_radians)
        
        # Calculate vertical depth change using the deviation
        horizontl_distance = D * np.sin(deviation_radians)
        north = horizontl_distance*np.cos(azimuth_radians)
        south = horizontl_distance*np.sin(azimuth_radians)
        # Update TVD without constraints
        new_tvd = tvds[i - 1] + vertical_distance
        new_north = norths[i-1] + north
        new_south = souths[i-1] + south
        
        tvds.append(new_tvd)
        norths.append(new_north)
        souths.append(new_south)

    return tvds, norths, souths

# Provided data
# Data: depth, deviation, azimuth
dev_data = [
    (348.00, 0.00, 0.00),
    (355.00, 1.10, 100.34),
    (385.00, 1.60, 206.30),
    (416.20, 4.90, 239.40),
    (444.40, 7.38, 241.15),
    (473.26, 9.20, 254.90),
    (502.12, 10.10, 266.60),
    (530.99, 11.40, 275.00),
    (559.80, 13.80, 276.30),
    (590.00, 16.90, 275.90),
    (617.60, 19.30, 276.50),
    (646.50, 22.30, 277.20),
    (675.36, 24.44, 276.30),
    (704.23, 26.24, 279.30),
    (733.07, 28.00, 278.00),
    (762.63, 27.50, 277.88),
    (791.51, 28.00, 279.64),
    (820.36, 28.30, 279.46),
    (849.20, 28.80, 277.80),
    (878.05, 28.65, 277.53),
    (906.90, 29.15, 277.10),
    (935.80, 29.90, 278.20),
    (964.65, 29.00, 275.00),
    (993.50, 29.80, 276.80),
    (1022.38, 29.23, 274.75),
    (1051.24, 28.75, 275.33),
    (1080.12, 29.23, 275.60),
    (1108.99, 29.23, 274.90),
    (1137.86, 28.87, 275.86),
    (1166.80, 29.10, 274.28),
    (1195.62, 28.75, 275.34),
    (1224.50, 29.10, 276.48),
    (1253.30, 29.60, 277.70),
    (1282.20, 29.90, 276.20),
    (1311.10, 28.50, 278.70),
    (1339.90, 28.60, 278.85),
    (1368.87, 29.05, 278.67),
    (1397.70, 28.50, 278.40),
    (1426.52, 29.01, 278.00),
    (1455.50, 29.20, 278.80),
    (1484.30, 28.90, 278.50),
    (1513.22, 28.90, 278.10),
    (1542.10, 28.70, 278.20),
    (1571.00, 28.60, 276.10),
    (1599.90, 28.50, 275.95),
    (1626.00, 28.45, 275.90),
    (1645.00, 28.41, 275.86)
]
def Calculate_TVD(dev_df, ref_depths):
        # Extracting depths and deviations
        depths = dev_df['DEPTH'].to_list()
        deviations = dev_df['DEVI'].to_list()
        azimuths = dev_df['AZIM'].to_list()

        # Compute TVD and cumulative TVD
        tvd_values, north_values, south_values = compute_tvd_minimum_curvature(depths, deviations, azimuths)

        computed_data = np.column_stack((depths, deviations, azimuths, tvd_values, north_values, south_values))
        # Create a new array of depths from min to max with step 0.5
        new_depths = ref_depths #np.arange(np.min(depths), np.max(depths) + 0.5, 0.5)
        # Perform linear interpolation for Devi and Azim
        devi_interp = interp1d(depths, deviations, kind='linear', fill_value="extrapolate")
        azim_interp = interp1d(depths, azimuths, kind='linear', fill_value="extrapolate")
        tvd_interp = interp1d(depths, tvd_values, kind='linear', fill_value="extrapolate")

        new_deviations = devi_interp(new_depths)
        new_tvds = tvd_interp(new_depths)
        new_azimuths = azim_interp(new_depths)

        interpolated_data = np.column_stack((new_tvds, new_deviations,new_azimuths))
        return interpolated_data
def InterPolate_TVD_Using_Datasets(dev_dtst, ref_dtst):
        # Extracting depths and deviations
        depths = [well_log for well_log in dev_dtst.well_logs if well_log.name == 'DEPTH'][0].log
        deviations = [well_log for well_log in dev_dtst.well_logs if well_log.name == 'DEVI'][0].log
        azimuths = [well_log for well_log in dev_dtst.well_logs if well_log.name == 'AZIM'][0].log
        #print(len(depths),len(deviations), len(azimuths))

        # Compute TVD and cumulative TVD
        tvd_values, north_values, south_values = compute_tvd_minimum_curvature(depths, deviations, azimuths)

        computed_data = np.column_stack((depths, deviations, azimuths, tvd_values, north_values, south_values))
        # Create a new array of depths from min to max with step 0.5
        #print(type(ref_dtst))
        new_depths = ref_dtst.well_logs[0].log

        # Perform linear interpolation for Devi and Azim
        devi_interp = interp1d(depths, deviations, kind='linear', fill_value="extrapolate")
        azim_interp = interp1d(depths, azimuths, kind='linear', fill_value="extrapolate")
        tvd_interp = interp1d(depths, tvd_values, kind='linear', fill_value="extrapolate")

        
        new_tvds = tvd_interp(new_depths)
        new_deviations = devi_interp(new_depths)
        new_azimuths = azim_interp(new_depths)
        

        interpolated_data = np.column_stack((new_tvds, new_deviations,new_azimuths))
        return interpolated_data
# Display results
#print(f"{'Depth (m)':<15}{'Devi (deg)':<15}{'Azim(deg)':<15}{'TVD (m)':<20}{'North (m)':<20}{'South (m)':<20}")
#for depth, deviation, azimuth, tvd, north, south in zip(depths, deviations, azimuths, tvd_values, north_values, south_values):
    #print(f"{depth:<15.2f}{deviation:<15.2f}{azimuth:<15.2f}{tvd:<20.2f}{north:<20.2f}{south:<20.2f}")
    
# Extracting depths and deviations
def Calc():
    dev_df = pd.DataFrame(dev_data,columns=['DEPTH', 'DEVI', 'AZIM'])
    depths = dev_df['DEPTH'].to_list()
    ref_depths = np.arange(np.min(depths), np.max(depths) + 0.5, 0.5)
    interpolated_data = Calculate_TVD(dev_df, ref_depths)
    for row in interpolated_data:
        print(f"{row[0]:.2f}\t{row[1]:.2f}\t{row[2]:.2f}")
#Calc()