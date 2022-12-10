## Tru-T API spec

- ### POST `/api/calculate/`

#### Payload:

```
{
    "model"                     : <string>,
    "initial_conditions"        : <object>,
    "return_species"            : <array>,
    "return_initial_conditions" : <boolean>,
    "ic_postfix"                : <string>
}
```

The fields are:
- `model`(required): A string identifier which specifies the model to use.
- `initial_conditions` (required): An object specifying the initial conditions. The object itself has keys which are "subject identifiers" (e.g. a patient ID or aliquot ID) which allows us to unambiguously map the initial conditions and results without concerns for potential ordering issues. In turn, those identifiers each reference an "initial condition" object which looks like:

```
{
    "<species identifier 1>": {
        "value": <number: the initial concentration to use>,
        "unit" : <string: measurement unit>
    },
    ...
    "<species identifier M>": {
        "value": <number: the initial concentration to use>,
        "unit" : <string: measurement unit>
    }}
```
e.g. for the Tru-T model using SHBG, testosterone ("T"), and albumin ("Alb"):

```
{
    "T": {
        "value": 566.2,
        "unit": "ng/dL"
    },
    "SHBG": {
        "value": 40.2, 
        "unit": "nmol/L"
    },
    "Alb": {
        "value": 4.3,
        "unit" : "g/dL"
    }
}
```

Thus, a valid object for `initial_conditions` can look like:

```
{
    "subject_0": {
        "T": {
            "value": 566.2,
            "unit": "ng/dL"
        },
        "SHBG": {
            "value": 40.2, 
            "unit": "nmol/L"
        },
        "Alb": {
            "value": 4.3,
            "unit" : "g/dL"
        }
    },
    ...
    "subject_N": {
        "T": {
            "value": 476.1,
            "unit": "ng/dL"
        },
        "SHBG": {
            "value": 21.6, 
            "unit": "nmol/L"
        },
        "Alb": {
            "value": 4.4,
            "unit" : "g/dL"
        }
    }
}
```
This allows subject measurements that each have a different set of units (although such a situation would be rare in practice).

The units themselves are part of a controlled vocabulary. The API has unit conversion routines to allow all the initial conditions to be converted to a common unit (e.g. all measurements are converted to nmol/L), which is required for the actual equilibrium calculations.

- `return_species` (optional, but practically required): An object which tells the API which of the species should be returned (the equilibrium concentrations) and in the desired unit. This allows the API to return only a subset results that we care about (e.g. only the free T in units of ng/dL). *If omitted, we return nothing*. An example of this is:

```
{
    "Tf": "ng/dL",
    "SHBG": "nmol/L"
}
```
which would mean the result payload would only have measurements for free T (`Tf`) and free SHBG (`SHBG`) in the specified units.

Note that this implies that results are returned in a consistent set of units, regardless of the input units.

- `return_initial_conditions` (optional, default=`false`): A boolean indicating whether the API should return the initial conditions that were sent. If `false`, the initial conditions are NOT echoed back. If set to `true`, consider also the `ic_postfix` field.
- `ic_postfix` (optional, default="_0"): A string which will be appended to the end of the initial conditions. This avoids ambiguity between initial conditions and intermediate species that have the same name. As an example, consider the following submited initial conditions (for a single subject):
```
{
    "subject_A": {
        "T": {
            "value": 566.2,
            "unit": "ng/dL"
        },
        "SHBG": {
            "value": 40.2, 
            "unit": "nmol/L"
        },
        "Alb": {
            "value": 4.3,
            "unit" : "g/dL"
        }
    }
}
```
This means that we initially prescribe the initial value for unbound SHBG to be 40.2; since the other SHBG species (bound and unbound i.e. S1, SHBG:T, S1:T, SHBG:T2) default to zero, this means that it is also the total SHBG in the system.

Now, when we run the equilibrium calculation, one of the outputs is the unbound SHBG at equilibrium, which would (in general) be less since some SHBG has converted to S1 and some is bound to T. To avoid ambiguity between the initial and equilibrium values of SHBG, we add a suffix/postfix to the initial value. Hence, if the request included `return_initial_conditions=true` and `ic_postfix="_0"`, then the results would look like:

```
{
    "subject_A": {
        "T_0"    : {
            "value": 566.2,
            "unit": "ng/dL"
        },
        "SHBG_0": {
            "value": 40.2, 
            "unit": "nmol/L"
        },
        "Alb_0": {
            "value": 4.3,
            "unit" : "g/dL"
        },
       <additional requested outputs here>
    }
}
```

#### Response

Examples are the best way to show how the payload affects the response. For all examples, we consider a single subject (which is easily generalized to >1 subjects).

Consider the following input payload:

```
{
    "model": "EAM",
    "initial_conditions": {
        "subject_A": {
            "T": {
                "value": 566.2,
                "unit": "ng/dL"
            },
            "SHBG": {
                "value": 40.2, 
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit" : "g/dL"
            }
        }
    },
    "return_species": {
        "Tf": "ng/dL",
        "SHBG": "nmol/L"        
    },
}
```

which results in the following response:
```
{
    "results": {
        "subject_A": {
            "Tf"    : {
                "value": 6.04,
                "unit": "ng/dL"
            },
            "SHBG": {
                "value": 34.5, 
                "unit": "nmol/L"
            }
        }
    }
}
```
Notes:
- The initial conditions are not returned by default (and they were not requested)


```
{
    "model": "EAM",
    "initial_conditions": {
        "subject_A": {
            "T": {
                "value": 566.2,
                "unit": "ng/dL"
            }
            "SHBG": {
                "value": 40.2, 
                "unit": "nmol/L"
            }
            "Alb": {
                "value": 4.3,
                "unit" : "g/dL"
            }
        }
    },
    "return_species": {
        "Tf": "ng/dL"
    },
    "return_initial_conditions" : true,
    "ic_postfix"                : "_init"
}
```

results in,
```
{
    "results": {
        "subject_A": {
            "Tf"    : {
                "value": 6.04,
                "unit": "ng/dL"
            },
            "T_init": {
                "value": 566.2,
                "unit": "ng/dL"
            },
            "SHBG_init": {
                "value": 40.2, 
                "unit": "nmol/L"
            },
            "Alb_init": {
                "value": 4.3,
                "unit" : "g/dL"
            }
        }
    }
}
```