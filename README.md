# CLIMVIZ: CLIMate models VIZualization tool

An interactive interface to many of the climate and earth models, such as RRTM.

This is a personal project aiming at developing a user-friendly tool for visualizing and analyzing climate models. 

The tool leverages the power of plotly dash and various scientific libraries to provide insightful visualizations and analyses.

## Features

- **Interactive Visualizations**: Utilize Plotly and Dash to create interactive plots and dashboards.
- **Climate Models Integration**: Integrate with climate models like RRTM for detailed analysis.
- **Customizable Parameters**: Easily adjust model parameters and see the effects in real-time.
- **Sensitivity Analysis**: Perform sensitivity analysis to understand the impact of different parameters.
- **Data Export**: Export data and results for further analysis.

## Installation

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```

## Usage
To start the application, run:

```sh
python -m climviz.app
```


## Project Structure
- climviz: Main application directory.
 - components/: Contains reusable UI components.
 - helpers/: Helper functions for layout and utilities.
 - models/: Climate models and related functions.
 - pages/: Different pages of the Dash application.
- requirements.txt: List of dependencies.
- pyproject.toml: Project configuration file.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
Climlab: A Python package for climate modeling.
Dash: A framework for building analytical web applications.
Plotly: A graphing library for making interactive plots.
