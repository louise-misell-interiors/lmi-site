#!/bin/bash

HASH=`git log --pretty=format:'%H' -n 1`

docker build -t evilben/lmi-django:$HASH .
docker push evilben/lmi-django:$HASH
cat kubes/django.yml | sed "s/(hash)/$HASH/g" | kubectl apply -f -
kubectl -n lmi rollout status deployment/site-django
