# cinder-k8s

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Code overview

Get familiarise with [Charmed Operator Framework](https://juju.is/docs/sdk)
and [Sunbeam documentation](sunbeam-docs).

cinder-k8s charm uses the ops\_sunbeam library and extends
OSBaseOperatorAPICharm from the library.

cinder-k8s charm consumes shared-db relation to connect to database,
identity-service to register the service endpoints to keystone
and ingress-internal/ingress-public relation to get exposed over
internal and public networks.

## Intended use case

cinder-k8s charm deploys and configures OpenStack Block storage service
on a kubernetes based environment. It should be possible to use
local storage or ceph based storage as backend.

## Roadmap

TODO

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests

## Deployment

This project uses tox for building and managing. To build the charm
run:

    tox -e build

To deploy the local test instance:

    juju deploy ./cinder-k8s_ubuntu-20.04-amd64.charm --resource cinder-api-image=kolla/ubuntu-binary-cinder-api:xena --resource cinder-scheduler-image=kolla/ubuntu-binary-cinder-scheduler:xena

<!-- LINKS -->

[sunbeam-docs]: https://github.com/openstack-charmers/advanced-sunbeam-openstack/blob/main/README.rst
