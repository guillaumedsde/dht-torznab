# DHT-Torznab

This Project is an attempt to expose torrents crawled with [magnetico](https://github.com/boramalper/magnetico) through a torznab compatible API.

This project is compose of mutiple services
- A [magneticod](https://github.com/boramalper/magnetico) torrent crawler
- A [beanstalkd](https://beanstalkd.github.io/) work queue for handling crawled torrent information
- A listener service for listening to the beanstalkd work queue and storing crawled torrents in a database
- A [PostgreSQL](https://www.postgresql.org/) database for storing and searching torrent information
- A [Django](https://www.djangoproject.com/) API for serving torrent information 

## Development

### Launching the development stack

The full development stack includes:
- the Magneticod crawler
- Beanstalkd
- the listener service
- the API
- a PostgreSQL database
- adminer, a UI to administer the development database

You can launch it with this command:

```bash
docker-compose up -d --build
```

### Run code formatters

The project's CI pipeline expects code to be formatted with the following tools:

- isort
- black

You can format the source files using this command:

```bash
make format
```

*note: this will modify the source files to format them*

### Run code checks

The project's CI pipeline expects code to pass a number of quality checks using the following tools:

- isort
- flake8
- black
- bandit
- mypy
- pytype
- safety

You can validate the source code with this command:

```bash
make checks
```
*note: this will **not** modify the source files*

### Run tests

You can run the project's test suite and generate a code coverage report with the following command:

```bash
make tests
```

### Performance profiling

The [django-silk](https://github.com/jazzband/django-silk) profiler is accessible at [localhost:8080/silk](http://localhost:8080/silk) in development. You can use it to profile the performance of the code along with the SQL queries

## Acknowledgement

- [@boramalper](https://github.com/boramalper) on GitHub for the [magneticod](https://github.com/boramalper/magnetico) torrent crawler

## License

See [LICENSE.md](LICENSE.md)

## Resources

- [Torznab specification](https://torznab.github.io/spec-1.3-draft/index.html)
- [Sonarr's guidelines on implementing a torznab API](https://github.com/Sonarr/Sonarr/wiki/Implementing-a-Torznab-indexer)
- [Radarr's test XML for torznab API responses](https://github.com/Radarr/Radarr/tree/develop/src/NzbDrone.Core.Test/Files/Indexers/Torznab)
