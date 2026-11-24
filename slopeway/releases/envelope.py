from ..encoding import digest
from ..evaluation.index import compile_index

FORMAT = 'slopeway-release/1'


def seal(body):
    fingerprint = digest(body)
    return {'format': FORMAT, 'id': f'sw-{fingerprint}', 'sha256': fingerprint, 'body': body}


def _matching_digest(record, field):
    return record[field] == digest({key: value for key, value in record.items() if key != field})


def verify(envelope):
    body = envelope['body']
    meta = body['meta']
    topology = body['topology']
    payload = {key: topology[key] for key in ('label', 'nodes', 'segments')}
    checks = {
        'format': envelope['format'] == FORMAT,
        'identity': envelope['id'] == f"sw-{envelope['sha256']}",
        'body_hash': digest(body) == envelope['sha256'],
        'topology': (topology['digest'] == digest(payload)
                     and topology['district'] == meta['district'] and topology['revision'] == meta['revision']),
        'input_cutoff': all(
            row['reported_at'] <= meta['cutoff'] and row['district'] == meta['district']
            and row['revision'] == meta['revision'] and _matching_digest(row, 'digest')
            for row in body['feeds']
        ),
        'compiled_index': compile_index(body['feeds'], meta['start'], meta['end']) == body['index'],
    }
    return {'id': envelope['id'], 'sha256': envelope['sha256'], 'verified': all(checks.values()), 'checks': checks}
