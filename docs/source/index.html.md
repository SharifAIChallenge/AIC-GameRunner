---
title: Middle Brain API Reference



toc_footers:
  - <a href='https://github.com/tripit/slate'>Documentation Powered by Slate</a>

includes:
  - errors

search: true
---


# Authentication

MiddleBrain uses a token to authenticate requests. It excepts the token to be
included in all API requests. Token generation can be done by the system admin.
Tokens may be bound to one or more IP addresses, in which case they only
authenticate successfully if the request is made through one of those addresses.

```
# With shell, you can just pass the correct header with each request
curl "api_endpoint_here"
  -H "Authorization: <your_token_goes_here>"
```

# API commands

The description given in each section,
assumes that the authentication is successful. In case of authentication failure,
a 401 or 403 error is returned.

If the request is not in the format described in the request section
of the command, a 400 error is returned.


## Files

### Upload

#### URL:

<aside>/storage/new_file/</aside>

#### Request:

Post the file as the body of the request.

#### Response:

The response is a JSON encoded dictionary containing the following keywords:

- token: A string to reference the file in future requests.

### Download

#### URL:

<aside>/storage/get_file/</aside>

#### Request:

The request should be a JSON encoded dictionary containing the following
keywords:

- token: A string used for referencing the file obtained in previous requests
to the API.

#### Response:

The file is served as the response.

## Game

### Run

#### URL:

<aside>/game/run/</aside>

#### Request:

```JSON
[{
  "game": "AIC17",
  "section": "play",
  "parameters": {
    "string_parameter1": "parameter1_value",
    "string_parameter2": "parameter2_value",
    "file_parameter1": "file_parameter1_token"
  }
}]
```

TYPE: POST

The request should be a JSON encoded **list of dictionaries**
 each representing a separate Run, containing the following keywords:

- game: The name of the game for this run. e.g. SharifAIC17
- section: The section of the game for this run. e.g. compile, play.
- parameters: a dictionary containing the parameters for this section.




#### Response:

The response is a JSON encoded **list of dictionaries**, each describing the status
for creating the Run described by the element in the same place in the request.

Each dictionary contains the following keyword:

- success: A boolean indicating whether the Run was created successfully.

In case success is true the dictionary contains the following keywords as well.

- token: A token to be used for referencing this run in future API requests.

In case success is false the dictionary contains the following keywords as well.

- errors: Errors preventing creation of the Run.

### Report

### URL:
<aside>/game/report/</aside>

### Request:

TYPE: GET

You may use ``time`` field to specify time.
Otherwise last request to this page will be considered as ``time``.

### Response:
A list of dictionaries of completed runs after ``time``. Each dictionary contains
the following keywords:

- token
- success: A boolean indicating whether the run was completed successfully.

In case success is false the dictionary contains the following keywords as well.

- errors

In case success is true the dictionary contains the following keywords as well.

- parameters: A dictionary containing the output parameters of the run.
Tokens are returned for files. You may download each file separately through
the API.
