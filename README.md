
## Installation

You'll need:

- python 3.6
- pipenv
- postgresql


```
pipenv install
```

Then copy `.env.sample` to `.env` and replace variables as necessary.

(You *may* need to pip install fabric3.)

```
pipenv shell
fab db.create
```

## Development

```
pipenv shell  # If you're not already in a pipenv shell
fab server
```
