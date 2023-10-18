# Documentation

## Steps to Use

### 1. Installation:
 ```
 pip install fcx-playground
 ```

### 2. Usage:
* To use data processing steps for NAV:
```
from fcx_playground.fcx_dataprocess.czml_nav import NavCZMLDataProcess
obj = NavCZMLDataProcess()

data = obj.ingest("<path_to_input>")
pre_processed_data = obj.preprocess(data)
czml_str = obj.prep_visualization(pre_processed_data)

```

* To use data processing steps for CRS rad-range:
```
from fcx_playground.fcx_dataprocess.tiles_rad_range import RadRangeTilesPointCloudDataProcess
obj = RadRangeTilesPointCloudDataProcess()

data = obj.ingest("<path_to_input>")
pre_processed_data = obj.preprocess(data)
point_clouds_tileset = obj.prep_visualization(pre_processed_data)

```

* To visualize NAV CZML:
```
from fcx_playground.fcx_cesium_viz.czml_viz import CZMLViz
czml_viz_obj = CZMLViz()
nav_czml_cesium_html = czml_viz_obj.generate_html("<path_to_saved_czml>")

# use the nav_czml_cesium_html in IPython.display.HTML to render it.
```

* To visualize CRS rad-range 3DTiles:
```
from fcx_playground.fcx_cesium_viz.tiles_viz import TilesViz
tileset_viz_obj = TilesViz()
point_clouds_tileset_html = tileset_viz_obj.generate_html("<path_to_saved_point_clouds_tileset>")

# use the point_clouds_tileset_html in IPython.display.HTML to render it.
```

### Note:
`ingest`, `preprocess`, `prep_visualization` methods are inherited from `DataProcess` Abstract Class. \
As per need, we can override or write custom methods for `ingest`, `preprocess`, `prep_visualization`, by maintaining consistency on the return type of the overrides.


## Steps to use fcx playground from Source Code

## Pre-requisites

### 1. General direction:
* Install `python`
* Install `conda` (optional but recommended)
* Use either `pip` or `conda` to install dependencies mentioned in `requirements.txt`
* Data are ingested from AWS S3. So, [Setup AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
    - `aws configure` Preferred. This deployment configuration is assumed to be used.
    - Need ```aws_access_key_id and aws_secret_access_key``` key values; inside `~/.aws/credentials`

### 2. Using Docker
* Install [Docker](https://docs.docker.com/desktop/)
* Data are ingested from AWS S3. So, [Setup AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
    - `aws configure` Preferred. This deployment configuration is assumed to be used.
    - Need ```aws_access_key_id and aws_secret_access_key``` key values; inside `~/.aws/credentials`
* Run `docker compose build` (will take few minutes)
* Run `docker compose up`, and note down the `token_id`
* Use `localhost:8888/tree?token=<token_id>` to run Jupyter Notebook.

## Usage:

* `notebooks` dir contains all the interactive python notebooks to get started with various visualization file generations.
* `src` dir contains modules that enables the visualization file generation.
  - Abstact classes defines the highlevel process on which the raw data are manupulated.
  - The concrete classes are implemented from abstract classes for detailed 3d visualization file generation processes.
  - There are utilities that help the visualization file generation.

### Devloper guidelines:
  - Clear Notebook `outputs` before commiting any changes to git; for clean changes tracking.