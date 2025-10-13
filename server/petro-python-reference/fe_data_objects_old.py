import pandas as pd
import pickle
import json
import matplotlib.pyplot as plt
import lasio
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@dataclass
class Constant:
    name: str
    value: float

class LogFrame(pd.DataFrame):
    # Define the static log types
    class LogType:
        INDEX = "Index"
        VARIABLE = "Variable"
        TOP = "Top"

    def __init__(self, data=None, index=None, columns=None, **kwargs):
        # Initialize the DataFrame with provided data
        super().__init__(data=data, index=index, columns=columns, **kwargs)
        # Ensure the DataFrame has the 'DEPT' column
        required_column = 'DEPT'
        if required_column not in self.columns:
            raise ValueError(f"DataFrame must contain the column: {required_column}")

    def get_log_summary(self):
        # Example method to get a summary of the DataFrame
        return self.describe()

    def to_dict(self) -> Dict[str, Any]:
        """Convert WellLog DataFrame to dictionary."""
        return {
            'columns': self.columns.tolist(),
            'index': self.index.tolist(),
            'data': self.values.tolist()
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LogFrame':
        """Create a LogFrame DataFrame from a dictionary."""
        df = pd.DataFrame(data['data'], columns=data['columns'])
        df.index = data['index']
        return LogFrame(df)

    def serialize(self, filename: str):
        """Serialize LogFrame to a file."""
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def deserialize(filename: str) -> 'LogFrame':
        """Deserialize WellLog from a file."""
        with open(filename, 'rb') as file:
            return pickle.load(file)

    def filter_by_depth(self, min_depth: float, max_depth: float) -> 'LogFrame':
        """Filter WellLog data by depth range."""
        if min_depth >= max_depth:
            raise ValueError("Minimum depth must be less than maximum depth.")
        filtered_data = self[(self['DEPT'] >= min_depth) & (self['DEPT'] <= max_depth)]
        return LogFrame(filtered_data)

    def add_log(self, name: str, data: List[float]) -> None:
        """Add a new log to the WellLog."""
        if name in self.columns:
            raise ValueError(f"Log '{name}' already exists.")
        self[name] = data

    def plot(self, logs: List[str] = None, depth_column: str = 'DEPT', title: str = 'Well Log', xlabel: str = 'Value', ylabel: str = 'Depth'):
        """Plot WellLog data using matplotlib."""
        if logs is None:
            logs = self.columns.tolist()
        if depth_column not in self.columns:
            raise ValueError(f"Depth column '{depth_column}' not found in WellLog.")
        if not logs:
            logs = [col for col in self.columns if col != depth_column]

        plt.figure(figsize=(12, 8))
        for log in logs:
            if log == depth_column:
                continue
            plt.plot(self[log], self[depth_column], label=log)
        
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.show()
        
@dataclass
@dataclass
class WellLog:
    """Data class representing a well log."""
    name: str
    date: str
    description: str
    log: List[float]  # New attribute for log values
    dtst: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert WellLog to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "date": self.date,
            "description": self.description,
            "logs": self.log,  # Serialize the logs
            "dtst": self.dtst,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WellLog':
        """Create a WellLog from a dictionary."""
        return WellLog(
            name=data['name'],
            date=data['date'],
            description=data['description'],
            log=data['log'],  # Deserialize the logs
            dtst=data['dtst']
        )
        
@dataclass
class Dataset:
    date_created: datetime
    name: str
    type: str
    wellname: str
    constants: List[Constant] = field(default_factory=list)
    index_log: List[float] = field(default_factory=list)
    index_name: str = ""
    well_logs: List[WellLog] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        """Convert the Dataset to a dictionary for JSON serialization."""
        return {
            "date_created": self.date_created.isoformat(),
            "name": self.name,
            "type": self.type,
            "wellname": self.wellname,
            "constants": [vars(constant) for constant in self.constants],
            "index_log": self.index_log,
            "index_name": self.index_name,
            "well_logs": [log.to_dict() for log in self.well_logs],
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data):
        """Create a Dataset from a dictionary."""
        constants = [Constant(**constant) for constant in data['constants']]
        well_logs = [WellLog.from_dict(log) for log in data['well_logs']]
        date_created = datetime.fromisoformat(data['date_created'])
        return Dataset(
            date_created=date_created,
            name=data['name'],
            type=data['type'],
            wellname=data['wellname'],
            constants=constants,
            index_log=data['index_log'],
            index_name=data['index_name'],
            well_logs=well_logs,
            metadata=data['metadata'],
        )


    @staticmethod
    def from_csv(filename: str, dataset_name: str, dataset_type: str, well_name: str) -> 'Dataset':
        """Create a Dataset from a CSV file."""
        # Read the CSV file
        df = pd.read_csv(filename)
        
        # Extract the index column name and values
        index_name = 'DEPT'  # Assuming 'DEPT' is the depth column
        if index_name not in df.columns:
            raise ValueError(f"CSV file must contain the column: {index_name}")
        
        index_log = df[index_name].tolist()
        
        # Remove the index column to process the remaining columns as logs
        df_logs = df.drop(columns=[index_name])
        
        # Create WellLog objects from each remaining column in the DataFrame
        well_logs = []
        for column in df_logs.columns:
            log_data = df_logs[column].tolist()
            well_log = WellLog(df[[index_name, column]])
            well_logs.append(well_log)
        
        # Create and return the Dataset object
        return Dataset(
            date_created=datetime.now(),
            name=dataset_name,
            type=dataset_type,
            wellname=well_name,
            index_log=index_log,
            index_name=index_name,
            well_logs=well_logs,
            metadata={'source': 'CSV import'}
        )

    @staticmethod
    def from_las(filename: str, dataset_name: str, dataset_type: str, well_name: str) -> 'Dataset':
        """Create a Dataset from a LAS file using lasio."""
        # Read the LAS file
        print('in Dataset from las',filename)
        las = lasio.read(filename)
        df=las.df()
        df.reset_index(inplace=True)
        #print(df)
        
        
        # Extract depth column
        index_name = ['DEPT','DEPTH']  # Assuming 'DEPT' is the depth column
        if index_name not in df.columns:
            raise ValueError(f"LAS file must contain the column: {index_name}")
        
        # Extract index log
        index_log = df[index_name].tolist()
        
        # Extract logs (excluding depth column)
        df_logs = df.drop(columns=[index_name])
        
        # Create WellLog objects from each log in the DataFrame
        well_logs = []
        for column in df_logs.columns:
            
            log_data = df_logs[column].tolist()
            
            log_df = pd.DataFrame({
                index_name: index_log,
                column: log_data
            })
            
            log_frame = LogFrame(log_df)
            w=WellLog(name = column,date=datetime.now(),description='Created from'+ filename,dataframe=log_frame, dtst='WIRE')
            well_logs.append(w)
        
        # Create and return the Dataset object
        return Dataset(
            date_created=datetime.now(),
            name=dataset_name,
            type=dataset_type,
            wellname=well_name,
            index_log=index_log,
            index_name=index_name,
            well_logs=well_logs,
            metadata={'source': 'LAS import'}
        )

    def plot_well_logs(self):
        """Plot each WellLog in the Dataset as subplots with DEPT on the y-axis and GR and RT on separate x-axes using twiny."""
        num_logs = len(self.well_logs)
        if num_logs == 0:
            raise ValueError("No WellLogs available to plot.")

        fig, axes = plt.subplots(nrows=num_logs, ncols=1, figsize=(12, 4 * num_logs), sharey=True)

        if num_logs == 1:
            axes = [axes]  # Ensure axes is iterable when there's only one subplot

        for ax, well_log in zip(axes, self.well_logs):
            ax.plot(well_log['GR'], well_log['DEPT'], label='GR', color='blue')
            ax.set_xlabel('GR')
            ax.set_ylabel('DEPT')
            ax.set_title(f'Well Log: {self.name}')
            ax.legend()
            ax.grid(True)

            ax2 = ax.twiny()
            ax2.plot(well_log['RT'], well_log['DEPT'], label='RT', color='red')
            ax2.set_xlabel('RT')
            ax2.legend(loc='upper right')

        plt.tight_layout()
        plt.show()

@dataclass
class Well:
    date_created: datetime
    well_name: str
    well_type: str
    datasets: List[Dataset] = field(default_factory=list)

    def add_dataset_from_csv(self, filename: str, dataset_name: str, dataset_type: str):
        """Add a Dataset to the Well from a CSV file."""
        dataset = Dataset.from_csv(filename, dataset_name, dataset_type, self.well_name)
        self.add_dataset(dataset)

    def add_well_from_las(self, filename: str, dataset_name: str, dataset_type: str):
        """Add a Dataset to the Well from a LAS file."""
        dataset = Dataset.from_las(filename, dataset_name, dataset_type, self.well_name)
        self.add_dataset(dataset)
        
    def add_dataset_from_las(self, filename: str, dataset_name: str, dataset_type: str):
        """Add a Dataset to the Well from a LAS file."""
        dataset = Dataset.from_las(filename, dataset_name, dataset_type, self.well_name)
        self.add_dataset(dataset)

    def add_dataset(self, dataset: Dataset):
        """Add a Dataset to the Well."""
        self.datasets.append(dataset)

    def remove_dataset(self, dataset_name: str):
        """Remove a Dataset by its name."""
        self.datasets = [ds for ds in self.datasets if ds.name != dataset_name]

    def get_dataset(self, dataset_name: str) -> Dataset:
        """Retrieve a Dataset by its name."""
        for ds in self.datasets:
            if ds.name == dataset_name:
                return ds
        raise ValueError(f"No Dataset found with name: {dataset_name}")

    def plot_all_well_logs(self):
        """Plot WellLogs for all datasets in the Well."""
        for dataset in self.datasets:
            dataset.plot_well_logs()

    def summary(self) -> Dict[str, Any]:
        """Generate a summary of the Well, including dataset names."""
        return {
            'well_name': self.well_name,
            'well_type': self.well_type,
            'dataset_names': [ds.name for ds in self.datasets]
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert Well to dictionary."""
        return {
            'date_created': self.date_created.isoformat(),
            'well_name': self.well_name,
            'well_type': self.well_type,
            'datasets': [dataset.to_dict() for dataset in self.datasets]
        }
    def serialize_well(self, filename: str):
        """Serialize Well to a file."""
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, default=str)

    @staticmethod
    def deserialize_well(filename: str) -> 'Well':
        """Deserialize Well from a file."""
        with open(filename, 'r') as file:
            data = json.load(file)
            return Well.from_dict(data)
    

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Well':
        """Create Well from a dictionary."""
        datasets = [Dataset.from_dict(ds) for ds in data.get('datasets', [])]
        return Well(
            date_created=datetime.fromisoformat(data['date_created']),
            well_name=data['well_name'],
            well_type=data['well_type'],
            datasets=datasets
        )

def serialize_WellLog(obj: WellLog, filename: str):
    """Serialize a CustomObject to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(obj.to_dict(), f)

def deserialize_WellLog(filename: str) -> WellLog:
    """Deserialize a CustomObject from a JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return WellLog.from_dict(data)
        
def serialize_dataset(dataset: Dataset, filename: str):
    """Serialize a Dataset to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(dataset.to_dict(), f)

def deserialize_dataset(filename: str) -> Dataset:
    """Deserialize a Dataset from a JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    return Dataset.from_dict(data)
