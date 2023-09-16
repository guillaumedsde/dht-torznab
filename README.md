# 🐛 DHT-Torznab

This Project is an attempt to expose torrents crawled with [magnetico](https://github.com/boramalper/magnetico) through a torznab compatible API.

## ⚙️ Services

This project is compose of mutiple services
- A [magneticod](https://github.com/boramalper/magnetico) torrent crawler
- A [beanstalkd](https://beanstalkd.github.io/) work queue for handling crawled torrent information
- A listener service for listening to the beanstalkd work queue and storing crawled torrents in a database
- A peer count updater service for retrieving up to date torrent peer counts
- A [PostgreSQL](https://www.postgresql.org/) database for storing and searching torrent information
- A [FastAPI](https://fastapi.tiangolo.com/) API for serving torrent information 


## 🧪 Development

### 🚀 Launching the development stack

You can launch the full stack locally using:

```bash
docker compose up
```

## 🔮 Roadmap

- [x] Insert torrents into PGSQL DB from magneticod
- [x] Search for torrents by name
- [x] Functional minimal torznab API
- [x] Functional minimal torznab API authentication
- [x] Implement a peer count updater
  - [bashkirtsevich-llc/aiobtdht](https://github.com/bashkirtsevich-llc)
  - [nitmir/btdht](https://github.com/nitmir/btdht)
- [x] Setup PGSQL schema for models with Alembic migrations
- [ ] Search for torrents by name of its files
- [ ] Torrent classifier
- [ ] Fully featured torznab API
- [ ] Users and credentials

## License

See [LICENSE.md](LICENSE.md)