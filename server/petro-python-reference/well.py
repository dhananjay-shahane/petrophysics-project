import sys
import pandas as pd
from felib.location import *
from felib.fields import las_fields as LAS_FIELDS
from dataset import *

class Well(object):
    """
    Well contains everything about the well.
    """

    def __init__(self, params=None):
        """
        Generic initializer.
        """
        if params is None:
            params = {}

        for k, v in params.items():
            if k and (v is not None):
                setattr(self, k, v)

        # empty header if none is passed
        empty_header = pd.DataFrame(columns=['original_mnemonic', 'mnemonic',
                                             'unit', 'value', 'descr', 'section'])

        self.dataset_list = list[dataset]
        self.datasets = getattr(self, 'datasets', {})
        self.header = getattr(self, 'header', empty_header)
        self.location = getattr(self, 'location', Location())
    
    @property
    def uwi(self):
        """
        Property. Simply a shortcut to the UWI from the header, or the
        empty string if there isn't one.
        """
        try:
            return self.header[self.header.mnemonic == 'UWI'].value.iloc[0]
        except:
            return ''
    @uwi.setter
    def uwi(self, uwi):
        """
        Set the uwi of the well by adding a row to the header dataframe

        Args:
            uwi (str): Unique Well Identifier

        Returns:
            Nothing, works inplace
        """
        # delete existing row for uwi if it exists
        if any(self.header.mnemonic.isin(['UWI'])):
            self.header = self.header[self.header.mnemonic != 'UWI']

        self.add_header_item('uwi', uwi)
    
    @property
    def name(self):
        """
        Property. Simply a shortcut to the well name from the header, or the
        empty string if there isn't one.
        """
        try:
            return self.header[self.header.mnemonic == 'WELL'].value.iloc[0]
        except:
            return ''

    @name.setter
    def name(self, name):
        """
        Set the name of the well by adding a row to the header dataframe

        Args:
            name (str): Name of the well

        Returns:
            Nothing, works inplace
        """
        # delete existing row for name if it exists
        if 'WELL' in self.header.mnemonic:
            self.header = self.header[self.header.mnemonic != 'WELL']

        self.add_header_item('name', name)

        
    def add_header_item(self, item, value, unit=None, descr=None):
            """
            Args:
                item (str): The item name to add. Requires to be present in
                    `las_fields` (e.g. well, uwi, null)
                value (str/float/int): The value of the item to add
                unit (str): Optional. The unit of the item to add
                descr (str): Optional. The description of the item to add

            Returns:
                Nothing, works inplace.
            """
            for obj, dic in LAS_FIELDS.items():
                for key, df_item in dic.items():
                    if key == item:
                        # create new row to add to header
                        new_row = {'original_mnemonic': df_item[1],
                                'mnemonic': df_item[1],
                                'unit': unit,
                                'value': value,
                                'descr': descr,
                                'section': obj}

                        new_df = pd.DataFrame(new_row, index=[0])

                        # Add new row to header. (df.append is deprecated.)
                        self.header = pd.concat([self.header, new_df], ignore_index=True)
    def append_dataset(self, dataset):
            """
            Args:
                item (str): The item name to add. Requires to be present in
                    `las_fields` (e.g. well, uwi, null)
                value (str/float/int): The value of the item to add
                unit (str): Optional. The unit of the item to add
                descr (str): Optional. The description of the item to add

            Returns:
                Nothing, works inplace.
            """
            self.dataset_list.append(dataset)

