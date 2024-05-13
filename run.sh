docker kill rsm
sleep 1

docker run \
  --rm \
  --detach \
  --env-file .env \
  --volume ~/work/resume_assistant:/usr/src/app \
  --publish 8502:8502 \
  --workdir /usr/src/app \
  --name resume \
  siva:assist ui.py --server.port 8502
