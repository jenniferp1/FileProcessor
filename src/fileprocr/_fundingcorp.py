"""Support FileProcessor Class.

Module contains Funding Corp data file specific processors. User supplies
processor method name and a DataFrame with the data for processing.

Classes:
    | :class:`fileprocr.FileProcessor.FileProcessor` - Loads and processes sets of flat files (ETL)
    | :class:`fileprocr._fundingcorp.ProcessFC` - Methods for processing data sent from Funding Corp

-----------------------------------------------------------------------------------------------------
"""

import pandas as pd


class ProcessFC:
    """Mixin class used by FileProcessor to process Funding Corp data files.

    See Also
    ---------
    :class:`fileprocr.FileProcessor.FileProcessor`: Base data processing class.
    """

    #############################################
    # PUBLIC METHOD TO SELECT CORRECT PROCESSOR #
    #############################################

    def choose_processor(self, df, proc_info):
        """Select user supplied processor method.

        Available processing methods for:
            1. Average Balances TB Q?.xls
            2. Balance Sheet TB Q?.xls

        Parameters
        -----------
        df: pd.DataFrame
            DataFrame with data needing processing.
        proc_info : dict
            Dictionary containing method name.

        Returns
        --------
        pd.DataFrame
            Processed DataFrame ready for upload to data warehouse.

        Examples
        ---------
        Sample dictionary format for proc_info (must include a method key as shown).

        .. code-block:: text

            {"class":"_fundingcorp", "method":"avg_bal_tb"}

        Notes
        ------
        Users need to add new processors methods if additional
        Funding Corp data files are provided.
        """

        proc_name = proc_info.get("method")

        if proc_name == "avg_bal_tb":
            df = self.__avg_bal_tb(df)
        elif proc_name == "bal_sheet_tb":
            df = self.__bal_sheet_tb(df)
        else:
            df = pd.DataFrame()

        return df

    ############################################
    # PRIVATE FUNDING CORP PROCESSING METHODS  #
    ############################################

    # Add new methods below if new data sources are provided.

    def __avg_bal_tb(self, df):
        """Process Average Balances TB xls.

        Private processing method called by choose_processor.

        Parameter
        ----------
        df : pd.DataFrame
            Unprocessed DataFrame.

        Returns
        ---------
        pd.DataFrame
            Processed DataFrame.

        See Also
        ---------
        fileprocr._fundingcorp.ProcessFC.choose_processor
        """

        df = df
        return df

    def __bal_sheet_tb(self, df):
        """Process Balance Sheet TB xls.

        Private processing method called by choose_processor.

        Parameter
        ----------
        df : pd.DataFrame
            Unprocessed DataFrame.

        Returns
        ---------
        pd.DataFrame
            Processed DataFrame.

        See Also
        ---------
        fileprocr._fundingcorp.ProcessFC.choose_processor
        """

        df = df
        return df
