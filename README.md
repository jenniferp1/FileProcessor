# fileprocr

## What is it?

**fileprocr** is a Python package that allows users to
load data from flat files and process the data to prepare for upload to
a data warehouse.

Data processing is done using data source specific processors that are
supplied via mixin classes.

## Main Features

 - Load flat files to a pandas DataFrame.
 - Process data using data source specific processors to make suitable for upload
 to a data warehouse.
 - Additional processors easily incorporated by adding a new [processor method](https://htmlpreview.github.io/?https://github.com/jenniferp1/FileProcessor/blob/main/docs/fileprocr.html)
 to the FileProcessor Class via a [Mixin Class](https://htmlpreview.github.io/?https://github.com/jenniferp1/FileProcessor/blob/main/docs/fileprocr.html).
 - Information on flat file processors is easily stored and provided to FileProcessor via
 [yaml files](https://htmlpreview.github.io/?https://github.com/jenniferp1/FileProcessor/blob/main/docs/sample-yaml.html). Storage in a yaml also makes it easy to update or add processors
 over time without having to make changes to the underlying code.

## Documentation

Documentation and help are provided [here](https://htmlpreview.github.io/?https://github.com/jenniferp1/FileProcessor/blob/main/docs/index.html).

Sample input yaml files are also included [here](./input).
