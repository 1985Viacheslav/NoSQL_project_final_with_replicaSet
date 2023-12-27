#!/bin/bash

# Параметры аутентификации
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example

# Ожидание запуска MongoDB и маршрутизатора запросов (mongos)
sleep 10

# Создание административного пользователя (если еще не создан)
mongo --host mongos --port 27017 <<EOF
use admin;
db.createUser({
  user: "$MONGO_INITDB_ROOT_USERNAME",
  pwd: "$MONGO_INITDB_ROOT_PASSWORD",
  roles: [{ role: "root", db: "admin" }]
});
EOF

# Ожидание создания пользователя
sleep 5

# Инициализация реплика-сета для конфигурационных серверов
mongo --host configsvr1 --port 27019 -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin <<EOF
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [
    { _id: 0, host: "configsvr1:27019" },
    { _id: 1, host: "configsvr2:27020" },
    { _id: 2, host: "configsvr3:27021" }
  ]
})
EOF

# Ожидание инициализации конфигурационного реплика-сета
sleep 10

# Инициализация шардов
mongo --host shard0 --port 27018 -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin <<EOF
rs.initiate({
  _id: "shard0ReplSet",
  members: [{ _id: 0, host: "shard0:27018" }]
})
EOF

mongo --host shard1 --port 27022 -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin <<EOF
rs.initiate({
  _id: "shard1ReplSet",
  members: [{ _id: 0, host: "shard1:27022" }]
})
EOF

# Ожидание инициализации шардов
sleep 10

# Добавление шардов в кластер через маршрутизатор запросов (mongos)
mongo --host mongos --port 27017 -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin <<EOF
sh.addShard("shard0ReplSet/shard0:27018")
sh.addShard("shard1ReplSet/shard1:27022")
EOF

echo "Sharding setup completed."
