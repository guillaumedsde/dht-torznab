# DHT-Torznab

This Project is an attempt to expose torrents crawled with [magnetico](https://github.com/boramalper/magnetico) through a well structured API, eventually with the torznab specification.

This project is compose of mutiple services
- A [magneticod](https://github.com/boramalper/magnetico) torrent crawler
- A [beanstalkd](https://beanstalkd.github.io/) work queue for handling crawled torrent information
- A listener service for listening to the beanstalkd work queue and storing crawled torrents in a database
- A [PostgreSQL](https://www.postgresql.org/) database for storing torrent information
- A [Django](https://www.djangoproject.com/) API written with [django-rest-framework](https://www.django-rest-framework.org/) for serving torrent information 

## Acknowledgement

- [@boramalper](https://github.com/boramalper) on GitHub for the [magneticod](https://github.com/boramalper/magnetico) torrent crawler

## License

See [LICENSE.md](LICENSE.md)

## Resources

- [Torznab specification](https://torznab.github.io/spec-1.3-draft/index.html)
- [Sonarr's guidelines on implementing a torznab API](https://github.com/Sonarr/Sonarr/wiki/Implementing-a-Torznab-indexer)
