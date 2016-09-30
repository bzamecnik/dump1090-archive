# Archives dump1090 messages via ZeroMQ to Postgres

Inspired by: [qixtand/dump1090-amqp-postgres](https://github.com/qixtand/dump1090-amqp-postgres) but with ZeroMQ instead of RabbitMQ.

## Architecture

We can one or more receivers with `dump1090` producing a stream of messages in BaseStation CSV format. We'd like to archive them to another host with a database that facilitates storage and further analysis. In our case we store messages to PostgreSQL. Since we may want to merge data from multiple receivers and receivers and storage may be on different computers we utilize a message queue as the means for transport, in this case ZeroMQ.

## Installing

Works OK in Python 3 (via Conda).

### Receiver

We assume that dump1090 is running and offering BaseStation stream at the port 30003.

```
pip install zmq
```

### Storage

```
pip install zmq
pip install psycopg2
```

#### Postgres

```
sudo apt-get update && sudo apt-get install postgresql postgresql-server-dev-9.4

# create user and database schema

# get to the admin console
sudo -u postgres psql
# run commands from create_db.sql (change the password however)
```

## Running

### Receiver

The receiver connects to the ZMQ endpoint and thus it can be behind a NAT.

It already reads from the dump1090 socket, thus there's no need for calling netcat.

```
export ZMQ_HOST=localhost
export ZMQ_PORT=5556
export DUMP1090_HOST=localhost
export DUMP1090_PORT=30003

python dump1090_publisher.py
```

### Storage

The storage ZMQ binds to a port which must be accessible from the receiver, eg. not behind a NAT.

```
export DB_HOST=localhost
export DB_DATABASE=dump1090
export DB_USER=dump1090
export DB_PASSWORD=...

python postgres_subscriber.py
```

## TODO

What will be good, but is (probably) not there yet:

- robustness against network connection outages
- queueing messages on the producer if it's offline
- marking messages with the receiver ID (add a new column)
- parsing dates
- robustness against malformed messages
- more graceful shutdown
- init scripts for running as a service
- cleaner code
