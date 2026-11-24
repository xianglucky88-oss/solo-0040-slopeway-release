from .evaluation.profiles import PROFILES
from .intake.sources import catalog
from .releases.channels import CHANNELS, state
from .storage.topology_store import districts


def available(connection):
    return {'districts': districts(connection), 'profiles': PROFILES,
            'sources': catalog(), 'channels': list(CHANNELS)}


def district_channels(connection, district):
    return {'district': district, 'heads': state(connection, district)}
