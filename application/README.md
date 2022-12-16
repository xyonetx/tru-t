## Setting up the python environment

Ensure you have a recent version of Python3 installed (3.9+).

Create a new Python virtual environment:

```
python3 -m venv <NAME>
```
where `<NAME>` is the name of the environment (e.g. run `python3 -m venv trut` to create a virtual environment named `trut`).

Activate the environment:
```
source <NAME>/bin/activate
```

Install the Python dependencies:
```
pip3 install -r requirements.txt
```

## Using the software

To use the software directly, check the help page for either `main.py` or `trut_main.py`. Note that `main.py` is quite general and `trut_main.py` has customizations specific to the Tru-T system involving testosterone, SHBG, and albumin; it halves the input SHBG values since they are dimers. 
```
$ python3 main.py -h

usage: main.py [-h] -m MODEL_FILE -i INPUT_FILE [-o OUTPUT_FILE] [-t TMAX]

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL_FILE, --model MODEL_FILE
                        The model file in JSON format.
  -i INPUT_FILE, --input INPUT_FILE
                        Path to a table containing initial conditions.
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Path to output results table.
  -t TMAX, --time TMAX  A dimensionless time controlling how long the simulation should run for.
```

The main scripts assume the following:
- There is an appropriate model in JSON format. See `testosterone_model_spec.json` for an example.
- The input file (`-i`) has the required initial conditions *all in the same units*. Conversion should happen prior. The first column should be unique identifiers (e.g. subject or patient identifiers)
- Use of the output file argument (`-o`) will send the output to a tab-delimited text file. Otherwise, the output is printed to stdout.
- The default simulation time (`-t`) is usually appropriate (hence the argument is optional), but can be extended if repeated results are inconsistent due to a lack of convergence. 

For the Tru-T specific script:
```
$ python3 trut_main.py -h

usage: trut_main.py [-h] -m MODEL_FILE -i INPUT_FILE -u UNITS_MAPPING [-o OUTPUT_FILE] [-t TMAX]

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL_FILE, --model MODEL_FILE
                        The model file in JSON format.
  -i INPUT_FILE, --input INPUT_FILE
                        Path to a table containing initial conditions.
  -u UNITS_MAPPING, --units UNITS_MAPPING
                        JSON-format string giving the units of each column in the input table.
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Path to output results table.
  -t TMAX, --time TMAX  A dimensionless time controlling how long the simulation should run for.
```

For example, using the example table in the `test/` folder:
```
python3 trut_main.py \
    -m testosterone_model_spec.json \
    -i test/test_table_in_different_units.tsv \
    -u '{"T":"ng/dL", "SHBG":"nmol/L", "Alb":"g/dL"}'
```