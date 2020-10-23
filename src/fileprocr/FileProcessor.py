"""Load and process flat files.

Given a set of flat files load into a DataFrame and process
the data to make it acceptable to load to a data warehouse.

Classes:
    | :class:`fileprocr.FileProcessor.FileProcessor` - Base processing class
    | :class:`fileprocr._fundingcorp.ProcessFC` - Mixin class specific for processing Funding Corp files

Examples
----------
**Usage example**

.. code-block:: python

  # identify directory your files are located
  path = "C:/Documents/projects/ReportingPlatform/FilesForUpload"

  # identify where your YAML is located
  proc_yaml = "C:/Documents/projects/ReportingPlatform/processors/processors.yml"

  # initialize instance of FileProcessor
  processor = FileProcessor(path)

  # get list of files in directory
  fnames = processor.files()

  for file, ext in fnames.items():
      # load data from file to DataFrame
      df = processor.load(file, ext[0])

      # process data for upload to data warehouse
      df = processor.process(file, df, proc_yaml)

-----------------------------------------------------------------------------------------------------
"""

# find other in-house packages in directory path
import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# import standard python packages
import pandas as pd
from datetime import datetime

# import Mixin Classes
from fileprocr import _fundingcorp

# import other homegrown modules
from utilsx.readin import get_fnames, checkdir, read_yaml


class FileProcessor(_fundingcorp.ProcessFC):
    """Process files for upload to data warehouse.

    Given a directory, return a list of files in the directory,
    load files to DataFrames, process DataFrames to prepare for load
    to a data warehouse.

    To add loadable file formats: Add an auxiliary (sub)method to load().
    To add specific data source processors: Add a mixin class to FileProcessor().

    Current loadable file formats:
        - xls, xlsx
        - html, eml

    Current data source specific processing mixin classes used by FileProcessor:
        - `_fundingcorp.ProcessFC <./_fundingcorp.html#_fundingcorp module>`_

    .. tip:: New processors for specific data sources can be added via a mixin class.

    Parameters
    ------------
    dpath : str
        Directory path with files to process.
    proc_yaml : str
        Fully qualified path and name of YAML with info on data source specific processors.

    Attributes
    -----------
    df : pd.DataFrame
        DataFrame with data loaded from files.
    extensions : list
        Loadable extensions.
    log : file
        Auto-generated log with errors and process status (saved in run directory).

    Notes
    -------
    **Extending FileProcessor capabilities**

    .. note:: A mixin class design is used in building FileProcessor. See :ref:`reference-label` for more information on mixins.

    * Files are loaded based on format.  A new format can be added by adding a new sub-method that is called by the main `load() method <./fileprocr.html#fileprocr.FileProcessor.FileProcessor.load>`_.
    * Files are processed for specific data sources.  A new source can be added via :ref:`mixin classes <reference-label>`.
    * When file formats are added, add file extension to self.extensions so user can print list of loadable formats using `loadable_formats() <./fileprocr.html#fileprocr.FileProcessor.FileProcessor.loadable_formats>`_.

    **Processor Data File (YAML)**

    Processing flat files requires data source specific processors.  Information for calling a file's
    processor is saved in a yaml. The yaml should be structured as:

    File name:
        | class: <your-mixin-class-name>
        | method: <file-specific-processor-from-mixin-class>

    where the `File name` header is the name of the flat file (e.g., My Data.xlsx)
    being processed.

    .. note:: An example of a yaml is `here <./sample-yaml.html>`_.

    .. _reference-label:

    References
    ----------

    `Making Python classes more modular using mixins <https://www.residentmar.io/2019/07/07/python-mixins.html>`_

    `Multiple inheritance and mixin classes in Python <https://www.thedigitalcatonline.com/blog/2020/03/27/mixin-classes-in-python/>`_

    `Making Python classes more modular using mixins <https://www.residentmar.io/2019/07/07/python-mixins.html>`_

    `Multiple inheritance and mixin classes in Python <https://www.thedigitalcatonline.com/blog/2020/03/27/mixin-classes-in-python/>`_
    """

    def __init__(self, dpath):

        # expand self.extensions if a new method to load a file format is added
        # a new sub-method should also be added below and called by the public load method
        # Note: eml and html treated the same
        self.extensions = ["xls", "xlsx", "html", "eml"]

        self.dpath = dpath

        # initialize log
        self.create_log()

        return

    def create_log(self):
        """Auto-generate a log upon initialization.

        When a FileProcessor instance is initialized a log will be created.
        The log will be saved in a logs subdirectory located in the run directory.

        Parameters
        ----------
        None

        Returns
        ---------
        None : None

        See Also
        ----------
        FileProcessor.write_log
        """

        log_path = "./logs"
        checkdir(
            log_path
        )  # create log subdir if it does not exist in run dir

        # logging date-time information
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_date = f"-- Session Activity on {timestamp} --\n"
        timestamp = timestamp.replace(":", "")
        timestamp = timestamp.replace(" ", "_")

        # create log file name by appending date and time
        self.log_name = f"{log_path}/log_{timestamp}.txt"

        # write standard log header to log
        self.log = open(self.log_name, "w")
        self.log.write(log_date)
        message = self.loadable_formats()
        for msg in message:
            self.log.write(msg)
            self.log.write("\n")
        self.log.write("\n\n")
        self.log.close()

        # create lists to store warnings, errors, and status updates
        # these are written to log when write_log is called
        self.log_issues = []  # warnings and errors
        self.log_loads = []  # files successfully loaded to DataFrame
        self.log_loadfails = []  # files that failed to load to DataFrame
        self.log_procs = []  # files successfully processed (via mixins)
        self.log_procfails = []  # files that failed processing step

        return

    def files(self):
        """Get list of file names and their extensions.

        Leveraging utilsx.get_fnames to return a list of all
        the files in a directory (fully qualified path of directory
        is given by self.dpath).

        Parameters
        -----------
        None

        Returns
        --------
        dict
            Dictionary with file names as keys and file extensions as values.

        Examples
        ---------
        Sample dictionary key-value structure returned: {full_path_of_file_name:[file_extension]}

        .. code-block:: text

            {"C:/User/doejohn/Documents/My Data File.xlsx":["xlsx"],
             "C:/User/doejohn/Documents/Another Data File.csv":["csv"]}
        """

        fnames = get_fnames(self.dpath)

        return fnames

    def load(self, fname, fext):
        """Load file into DataFrame.

        Based on file format (i.e., file extension) calls a private
        load method for that file type.  If a load submethod does not
        exist for a given file format, an error will be logged and an
        empty DataFrame returned.

        Parameters
        -----------
        fname : str
            Fully qualified path and file name to be loaded.
        fext : str
            File extension denoting file type of file to be loaded.

        Returns
        --------
        pd.DataFrame
            DataFrame with file contents.
        """

        if fext not in self.extensions:
            self.log_issues.append(
                f"\n- ERROR: '{fext}' is not a loadable format for {fname}. \n\tNo data loaded."
            )
            self.log_loadfails.append(f"{fname}")
            print(f"Skipping... '{fname}' (see log for details)")
            return pd.DataFrame()
        else:
            print(f"Loading... '{fname}'")

            # Call correct loader sub-method
            if fext == "xls" or fext == "xlsx":
                df = self.__load_excel(fname)
            elif fext == "eml" or fext == "html":
                df = self.__load_html(fname)

            if not df.empty:
                self.log_loads.append(f"{fname}")
            else:
                self.log_loadfails.append(f"{fname}")

        return df

    def __load_excel(self, file):
        """Load Excel file to DataFrame.

        Private file loading sub-method called by load.

        Parameters
        -----------
        file : str
            Fully qualified path and file name to be loaded.

        Returns
        --------
        pd.DataFrame
            DataFrame with contents of file.

        See Also
        ---------
        FileProcessor.load
        """

        xl = pd.ExcelFile(file)
        sheets = []
        for name in xl.sheet_names:
            if not name.startswith("Sheet"):
                sheets.append(name)
        # TODO add multi-sheet load
        if len(sheets) > 1:
            self.log_issues.append(
                "\n- Warning: multiple worksheets detected. \n\tOnly first worksheet was loaded."
            )
            df = pd.read_excel(xl, sheets[0])
        elif len(sheets) == 1:
            df = pd.read_excel(xl, sheets[0])
        else:
            df = pd.DataFrame()

        return df

    def __load_html(self, file):
        """Load HTML or EML file to DataFrame.

        Private file loading sub-method called by load.

        Parameters
        -----------
        file : str
            Fully qualified path and file name to be loaded.

        Returns
        --------
        pd.DataFrame
            DataFrame with contents of file.

        See Also
        ---------
        FileProcessor.load
        """

        frames = pd.read_html(file)
        max_frame = frames[0].shape[0] * frames[0].shape[1]

        for index, frame in enumerate(frames):
            if frame.shape[0] * frame.shape[1] > max_frame:
                max_frame = frame.shape[0] * frame.shape[1]
                max_index = index

        df = frames[max_index]

        return df

    def loadable_formats(self, verbose=False):
        """Print list of loadable file formats.

        Prints a list of loadable file formats to screen or
        to log depending on verbose setting. To print to the screen
        set verbose to True.

        List of formats is obtained from self.extensions.

        Parameters
        -----------
        verbose : bool
            True to print to screen; False to print to log (default False).

        Returns
        --------
        list
            Message listing loadable file formats.
        """

        message = ["\nFile formats that can be loaded:"]
        for ext in self.extensions:
            message.append(f"\t- {ext}")
        message.append(
            "\n\tIf you need to load another format, add a sub-method under load()"
        )

        if verbose:
            for msg in message:
                print(msg)

        return message

    def process(self, fname, df, proc_yaml):
        """Process data in DataFrames.

        Process a DataFrame to make it suitable for loading
        contents to a data warehouse.

        .. note:: the file name in fname should be the same as the header in the `proc_yaml <./sample-yaml.html>`_.

        where proc_yaml should be structured as:

        File name:
            | class: <your-mixin-class-name>
            | method: <file-specific-processor-from-mixin-class>

        Parameters
        -----------
        fname : str
            Fully qualified path and file name of file to be processed.
        df : pd.DataFrame
            DataFrame with unprocessed file contents.
        proc_yaml : str
            Fully qualified path and file name of yaml with info on data source specific processors.

        Returns
        ----------
        pd.DataFrame
            Processed DataFrame suitable for upload to data warehouse.
        """

        file = fname.split("/")[-1]

        processor_info = read_yaml([proc_yaml, file], abort=False)

        if processor_info:
            df = self.choose_processor(df, processor_info)

            if not df.empty:
                self.log_procs.append(f"{fname}")
            else:
                self.log_issues.append(
                    f"\n- ERROR: no processor found for '{file}'. \n\tAdd processor to data source's mixin class."
                )
                self.log_procfails.append(f"{fname}")
        else:
            self.log_issues.append(
                f"\n- ERROR: no entry found for '{file}' in yaml. \n\tVerify entry in {proc_yaml}."
            )
            self.log_procfails.append(f"{fname}")

        return df

    def write_log(self, field="all"):
        """Write to log.

        Write warnings, errors, and load/process status to a log.

        Parameters
        ----------
        field : str
            Keyword to specify what should be written to log (default all).

        Returns
        -------
        None : None

        Notes
        ------
        Keyword options for **field**: `all`, `issue`, `load`, `process`

            * `all` prints everything to the log
            * `issue` prints only errors and warnings to log
            * `load` prints only load status updates to log
            * `process` prints only processing status updated to log
        """

        field_options = ["issue", "load", "process", "all"]
        if field not in field_options:
            print(f"{field} is unrecognized option. Log not updated")
            return

        self.log = open(self.log_name, "a")

        if field == "all" or field == "issue":
            if len(self.log_issues) == 0:
                self.log.write("Warnings or Errors")
                self.log.write("\n------------------\n")
                self.log.write("No warnings or errors.")
            else:
                print("\nThere were warnings or errors. See:")
                print(f"\t{self.log_name}")
                self.log.write("Warnings or Errors")
                self.log.write("\n------------------")
                for msg in self.log_issues:
                    self.log.write(f"\t{msg}")

        if field == "all" or field == "load":
            if len(self.log_loads) == 0:
                self.log.write("\n\n\nFiles Successfully Loaded")
                self.log.write("\n-------------------------\n")
                self.log.write("None")
            else:
                self.log.write("\n\n\nFiles Successfully Loaded")
                self.log.write("\n-------------------------")
                for msg in self.log_loads:
                    self.log.write(f"\n- {msg}")

            if len(self.log_loadfails) == 0:
                self.log.write("\n\n\nFiles Failing Load")
                self.log.write("\n------------------\n")
                self.log.write("None")
            else:
                self.log.write("\n\n\nFiles Failing Load")
                self.log.write("\n------------------")
                for msg in self.log_loadfails:
                    self.log.write(f"\n- {msg}")

        if field == "all" or field == "process":
            if len(self.log_procs) == 0:
                self.log.write("\n\n\nFiles Successfully Processed")
                self.log.write("\n----------------------------\n")
                self.log.write("None")
            else:
                self.log.write("\n\n\nFiles Successfully Processed")
                self.log.write("\n----------------------------")
                for msg in self.log_procs:
                    self.log.write(f"\n- {msg}")

            if len(self.log_procfails) == 0:
                self.log.write("\n\n\nFiles Failing Processing")
                self.log.write("\n------------------------\n")
                self.log.write("None")
            else:
                self.log.write("\n\n\nFiles Failing Processing")
                self.log.write("\n------------------------")
                for msg in self.log_procfails:
                    self.log.write(f"\n- {msg}")

        self.log.close()

        return


if __name__ == "__main__":
    # execute only if run as a script

    print("\n")
    path = "M:/Documentsmy/projects/PublicReportingPlatform/FilesForUpload"
    proc_yaml = "M:/Documentsmy/projects/PublicReportingPlatform/processors/processors.yml"

    processor = FileProcessor(path)
    fnames = processor.files()

    for file, ext in fnames.items():
        df = processor.load(file, ext[0])
        if not df.empty:
            # process data for upload to data warehouse
            df = processor.process(file, df, proc_yaml)
            print(df.head())

    # TODO build processors for specific files (use Mixins)

    processor.write_log()
