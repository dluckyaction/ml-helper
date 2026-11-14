## Purpose

Lets users load a single time series, visualize it as an interactive chart, and classify it into the Syntetos-Boylan series types through a marimo notebook entrypoint.

## ADDED Requirements

### Requirement: Load a time series from CSV or Parquet

The system SHALL load a single time series from a CSV or Parquet data source provided either as a local file path or URL, or as an uploaded file.

#### Scenario: Load from local path

- **WHEN** the user enters a valid local CSV or Parquet path
- **THEN** the system loads the corresponding rows as a single series

#### Scenario: Load from URL

- **WHEN** the user enters a valid HTTP(S) URL pointing to a CSV or Parquet file
- **THEN** the system downloads and loads the file as a single series

#### Scenario: Load from uploaded file

- **WHEN** the user uploads a CSV or Parquet file
- **THEN** the system loads the uploaded content as a single series

#### Scenario: Invalid or unsupported source

- **WHEN** the path does not exist, the download fails, or the file is not CSV/Parquet
- **THEN** the system shows an error message and renders no chart or classification

### Requirement: Select date and value columns

The system SHALL let the user indicate, by name, which column holds the date/index and which column holds the numeric value of the series.

#### Scenario: Valid column names

- **WHEN** the user specifies a date column and a numeric value column that both exist in the data
- **THEN** the system reads exactly those two columns as the series

#### Scenario: Unknown column name

- **WHEN** the user specifies a column name that is not present in the data
- **THEN** the system shows an error message and renders no chart or classification

### Requirement: Form-driven classification

The notebook SHALL present a form gathering the date column, the value column, and the data source, and SHALL load, visualize, and classify the series only when the user submits the form.

#### Scenario: Classification triggered by submit

- **WHEN** the user has provided a data source and column names and submits the form
- **THEN** the system loads the data, renders the chart, and displays the series type

#### Scenario: Nothing shown before submit

- **WHEN** the form has not been submitted
- **THEN** neither the chart nor the series type is displayed

### Requirement: Syntetos-Boylan classification

The system SHALL classify the loaded series into exactly one of Smooth, Erratic, Intermittent, Lumpy, or Not Classifiable using the average demand interval (ADI) and the squared coefficient of variation (CV²), where ADI is the number of observed periods divided by the number of periods with nonzero demand, and CV² is the square of the ratio of the standard deviation of nonzero demand sizes to their mean. ADI is considered high at 1.32 or above, and CV² is considered large at 0.49 or above. A series with no zero-demand periods (ADI equal to 1.0) or with no demand at all (all values zero) is outside the intermittent-demand model and SHALL be labeled Not Classifiable.

#### Scenario: Smooth series

- **WHEN** ADI < 1.32 and CV² < 0.49
- **THEN** the series type is Smooth

#### Scenario: Erratic series

- **WHEN** ADI < 1.32 and CV² >= 0.49
- **THEN** the series type is Erratic

#### Scenario: Intermittent series

- **WHEN** ADI >= 1.32 and CV² < 0.49
- **THEN** the series type is Intermittent

#### Scenario: Lumpy series

- **WHEN** ADI >= 1.32 and CV² >= 0.49
- **THEN** the series type is Lumpy

#### Scenario: Continuous series with no zeros

- **WHEN** every period has a nonzero value, so ADI is 1.0
- **THEN** the series type is Not Classifiable

#### Scenario: Series with no demand at all

- **WHEN** every period has a value of zero
- **THEN** the series type is Not Classifiable

#### Scenario: Non-numeric value column

- **WHEN** the selected value column cannot be interpreted as numbers
- **THEN** the system shows an error message and renders no series type

### Requirement: Visualize the selected series

The system SHALL render the selected series as an interactive time-series chart of the value column over the date column once classified.

#### Scenario: Chart rendered

- **WHEN** the form has been submitted and the data is valid
- **THEN** an interactive chart plotting the value column against the date column is displayed

### Requirement: Display the series type

The system SHALL display the classified series type in a clearly visible box alongside the chart.

#### Scenario: Type box shown

- **WHEN** classification has completed successfully
- **THEN** a box showing the series type label (Smooth, Erratic, Intermittent, Lumpy, or Not Classifiable) is displayed