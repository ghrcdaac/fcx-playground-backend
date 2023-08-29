# Steps to use data processing playground

## Pre-requisites

* Install `python`
* Install `conda` (optional but recommended)
* Use either `pip` or `conda` to install dependencies mentioned in `requirements.txt`
* Data are ingested from AWS S3. So, [Setup AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
    - `aws configure` Preferred. This deployment configuration is assumed to be used.
    - Need ```aws_access_key_id and aws_secret_access_key``` key values; inside `~/.aws/credentials`

## Usage:

* `notebooks` dir contains all the interactive python notebooks to get started with various visualization file generations.
* `src` dir contains modules that enables the visualization file generation.
  - Abstact classes defines the highlevel process on which the raw data are manupulated.
  - The concrete classes are implemented from abstract classes for detailed 3d visualization file generation processes.
  - There are utilities that help the visualization file generation.

## NOTE:
  - Clear Notebook `outputs` before commiting any changes related to notebooks; for clean changes tracking.