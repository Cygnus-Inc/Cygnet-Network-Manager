"""
This module provides functionality and services that interact with
the AWS networking functionality.

AWS EC2 instances can make use of "Elasic Network Interfaces", which
can be bound to a docker container in order to provide it with a
dedicated network address.
"""
from boto.utils import get_instance_metadata
from boto.utils import get_instance_identity

try:
    instance_identity = get_instance_identity()
    instance_metadata = get_instance_metadata()
except Exception as err:
    raise err

# TODO: work out if this can be better integrated with click.
